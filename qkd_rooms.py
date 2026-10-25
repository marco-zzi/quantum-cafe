"""Multiplayer rooms for 'The Messenger Wisps'.

A room has a table (the host device), three seats (Alice, Bob, Eve) and one Game once the table presses Play. Every seat has its
own unguessable token, carried in the QR code. The first device that claims a seat keeps it (identified by a random id its
browser keeps in localStorage), so a second scan of the same code is refused while a phone that reloads can rejoin.

Rooms live in the server process only: they are lost when the app restarts or sleeps, and expire after TTL seconds.
"""
import hashlib
import secrets
import threading
import time

from qkd_game import ROLES, Game

TTL = 3 * 3600
CODE_LEN = 4
ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"        # no 0/O, 1/I/L


class Room:
    def __init__(self, code, host_token):
        self.code = code
        self.host_token = host_token
        self.tokens = {r: secrets.token_urlsafe(9) for r in ROLES}
        self.claimed = {}                           # role -> client id
        self.game = None
        self.last_nonce = {}                        # who -> last applied nonce
        self.touched = time.time()
        self.version = 0                            # lobby changes

    def role_for(self, token):
        for r, t in self.tokens.items():
            if secrets.compare_digest(t, token or ""):
                return r
        return None


class Registry:
    def __init__(self):
        self.lock = threading.RLock()
        self.rooms = {}
        self.salt = secrets.token_bytes(16)         # per-process secret, part of the seed for room codes
        self.counter = 0

    # ---- codes --------------------------------------------------------------------------------------------------------------
    def _code(self, ip):
        """Short code from a hash of the time, a process secret and the caller's IP. The collision check against live rooms is
        what guarantees two games never overlap; the hash only spreads the codes out."""
        while True:
            self.counter += 1
            seed = b"|".join([str(time.time_ns()).encode(), self.salt, (ip or "").encode(), str(self.counter).encode()])
            digest = hashlib.sha256(seed).digest()
            num = int.from_bytes(digest[:8], "big")
            code = ""
            for _ in range(CODE_LEN):
                num, d = divmod(num, len(ALPHABET))
                code += ALPHABET[d]
            if code not in self.rooms:
                return code

    def _purge(self):
        now = time.time()
        for c in [c for c, r in self.rooms.items() if now - r.touched > TTL]:
            del self.rooms[c]

    # ---- rooms --------------------------------------------------------------------------------------------------------------
    def create(self, ip=None):
        with self.lock:
            self._purge()
            code = self._code(ip)
            room = Room(code, secrets.token_urlsafe(12))
            self.rooms[code] = room
            return room

    def get(self, code):
        with self.lock:
            self._purge()
            room = self.rooms.get((code or "").upper())
            if room:
                room.touched = time.time()
            return room

    def claim(self, code, token, client):
        """Seat a device. Returns (role, status) where status is ok, taken, started, or missing."""
        with self.lock:
            room = self.get(code)
            if not room:
                return None, "missing"
            role = room.role_for(token)
            if not role:
                return None, "missing"
            owner = room.claimed.get(role)
            if owner is not None:
                return role, "ok" if owner == client else "taken"
            if room.game is not None:
                return role, "started"
            room.claimed[role] = client
            room.version += 1
            return role, "ok"

    def play(self, code, host_token):
        with self.lock:
            room = self.get(code)
            if not room or not secrets.compare_digest(room.host_token, host_token or ""):
                return "not the host"
            if room.game is not None:
                return None
            if len(room.claimed) < 2:
                return "at least two players are needed"
            room.game = Game("room", set(room.claimed))
            room.version += 1
            return None

    def reset(self, code, host_token):
        """Back to the lobby with the same seats."""
        with self.lock:
            room = self.get(code)
            if not room or not secrets.compare_digest(room.host_token, host_token or ""):
                return "not the host"
            room.game = None
            room.version += 1
            return None

    def act(self, code, who, kind, payload, nonce):
        """Apply one action from a seat ('alice', 'bob', 'eve') or the table. Duplicate nonces are ignored."""
        with self.lock:
            room = self.get(code)
            if not room or room.game is None:
                return "no game"
            if nonce is not None and room.last_nonce.get(who) == nonce:
                return None
            room.last_nonce[who] = nonce
            return room.game.act(who, kind, payload)

    def view(self, code, who):
        with self.lock:
            room = self.get(code)
            if not room:
                return None
            if room.game is None:
                return dict(phase="lobby", version=room.version, humans=sorted(room.claimed))
            return room.game.view(who)
