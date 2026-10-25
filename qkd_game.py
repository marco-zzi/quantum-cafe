"""State machine for one game of 'The Messenger Wisps'.

One Game serves every mode. 'bob' and 'eve' are solo runs (the other two roles are bots); 'room' is a multiplayer match in which
every role that has a phone is human and every other role is a bot. The server owns all secrets: view() returns only what a
given role is allowed to see, so nothing hidden ever reaches a browser.

Phases, in order: setup (Bob picks the number of wisps, only when Alice is a bot), alice, eve, bob, sample, verdict, result.
A phase waits on a human only when that role is human; otherwise the bot acts at once.
"""
import qkd_engine as E

ROLES = ("alice", "bob", "eve")
PHASES = ("setup", "alice", "eve", "bob", "sample", "verdict", "result", "over")


class Game:
    def __init__(self, mode, humans, seed=None):
        assert mode in ("bob", "eve", "room")
        self.mode = mode
        self.humans = set(humans)
        self.rng = E.rng_new(seed)
        self.round = 0
        self.score = 0                  # solo: points of the run
        self.towers = 0                 # room: Alice and Bob together
        self.eve_total = 0              # room: Eve's points; solo Eve uses score
        self.alive = True
        self.mana = E.MANA_START
        self.version = 0
        self.result = None
        self.history = []               # one entry per finished round
        self.phase = "setup"
        self._begin_round()

    # ---- round set-up -------------------------------------------------------------------------------------------------------
    def _cfg(self):
        table = E.EVE_ROUNDS if self.mode == "eve" else E.BOB_ROUNDS
        return table[min(self.round, len(table) - 1)]

    def _begin_round(self):
        self.result = None
        self.n = 0
        self.a_bits = self.a_lens = self.e_choice = self.e_res = self.b_lens = self.b_res = None
        self.sifted = self.sample = None
        self.fraction = None
        self.verdicts = {}
        if self.mode == "room":
            self.storm, self.cfg = E.ROOM_STORM, dict(name="Round %d" % (self.round + 1), goal="", fact="")
            self.spy_tap = self.rng.choice((0.0, 0.4, 0.7, 1.0))
        else:
            self.cfg = self._cfg()
            self.storm = self.cfg["storm"]
            self.spy_tap = self.cfg["tap"] if self.mode == "bob" and self.rng.random() < self.cfg["spy"] else 0.0
        if self.mode == "bob" and self.round > 0:
            self.mana = min(E.MANA_CAP, self.mana + E.MANA_PER_ROUND)
        if self.mode == "bob" and self.mana < E.MIN_WISPS:
            self.alive, self.phase = False, "over"
            return
        if self.mode == "eve":
            self.n = self.cfg["n"]
            self.a_bits, self.a_lens = E.prepare(self.rng, self.n)
            self.phase = "eve" if "eve" in self.humans else "alice"
        else:
            self.phase = "alice" if "alice" in self.humans else ("setup" if "bob" in self.humans else "alice")
        self._advance()

    def _chooser(self):
        return "alice" if "alice" in self.humans else ("bob" if "bob" in self.humans else None)

    # ---- bots ---------------------------------------------------------------------------------------------------------------
    def _advance(self):
        """Run bot turns until a human is needed or the round is over."""
        while True:
            ph = self.phase
            if ph == "setup":
                if "bob" in self.humans:
                    return
                self.phase = "alice"
            elif ph == "alice":
                if "alice" in self.humans and self.a_bits is None:
                    return
                if self.a_bits is None:
                    if self.n == 0:
                        self.n = self.rng.choice((16, 24, 32))
                    self.a_bits, self.a_lens = E.prepare(self.rng, self.n)
                self.phase = "eve"
            elif ph == "eve":
                if "eve" in self.humans and self.e_choice is None:
                    return
                if self.e_choice is None:
                    self.e_choice = E.eve_bot(self.rng, self.n, self.spy_tap)
                self._eve_measure()
                self.phase = "bob"
            elif ph == "bob":
                if "bob" in self.humans and self.b_lens is None:
                    return
                if self.b_lens is None:
                    self.b_lens = [self.rng.randint(0, 1) for _ in range(self.n)]
                self._bob_measure()
                self.phase = "sample"
            elif ph == "sample":
                if self.fraction is None:
                    chooser = "bob" if "bob" in self.humans else ("alice" if "alice" in self.humans else None)
                    if chooser:
                        return
                    self.fraction = self.cfg.get("sample", 0.5)
                self.sample = E.pick_sample(self.rng, self.sifted, self.fraction)
                self.phase = "verdict"
            elif ph == "verdict":
                need = [r for r in ("alice", "bob") if r in self.humans]
                if need and len(self.verdicts) < len(need):
                    return
                self._finish()
                return
            else:
                return

    def _eve_measure(self):
        self.e_res = [None if c == E.PASS else (self.a_bits[i] if c == self.a_lens[i] else self.rng.randint(0, 1))
                      for i, c in enumerate(self.e_choice)]
        self._eve_resend = [(c, r) if c != E.PASS else None for c, r in zip(self.e_choice, self.e_res)]

    def _bob_measure(self):
        self.b_res = []
        for i in range(self.n):
            lens, bit = (self.a_lens[i], self.a_bits[i]) if self._eve_resend[i] is None else self._eve_resend[i]
            res = bit if lens == self.b_lens[i] else self.rng.randint(0, 1)
            if self.rng.random() < self.storm:
                res ^= 1
            self.b_res.append(res)
        self.sifted = E.sift(self.a_lens, self.b_lens)

    def _finish(self):
        t = E.tally(self.a_bits, self.b_res, self.a_lens, self.e_choice, self.sifted, self.sample)
        humans_ab = [r for r in ("alice", "bob") if r in self.humans]
        if humans_ab:
            verdict = "keep" if all(self.verdicts[r] == "keep" for r in humans_ab) else "abort"
        else:
            verdict = E.bot_verdict(t, self.cfg.get("tol", E.THRESHOLD))
        if verdict == "keep" and not t["key"]:
            verdict = "abort"
        oc = E.outcome(verdict, t)
        ab, ev = E.points(oc, t)
        self.result = dict(t, verdict=verdict, outcome=oc, ab=ab, eve=ev)
        if self.mode == "bob":
            self.score += 0 if oc == "breach" else ab         # a leaked key ends the run and earns nothing
            self.alive = oc not in ("false_alarm", "breach")
        elif self.mode == "eve":
            self.score += ev
            self.alive = oc != "caught"
        else:
            self.towers += ab
            self.eve_total += ev
        self.history.append(dict(round=self.round + 1, outcome=oc, n=self.n, key=len(t["key"]), known=len(t["eve_known"]),
                                 qber=round(t["qber"], 3), tapped=t["tapped"]))
        self.phase = "result"

    # ---- actions ------------------------------------------------------------------------------------------------------------
    def act(self, role, kind, p):
        """Apply one action from one role. Returns an error string, or None when it was applied."""
        if role not in self.humans and kind != "next":
            return "not a player"
        fn = getattr(self, "_a_" + str(kind), None)
        if fn is None:
            return "unknown action"
        try:
            err = fn(role, p if isinstance(p, dict) else {})
        except (TypeError, ValueError, KeyError):
            return "bad request"
        if err is None:
            self._advance()
            self.version += 1
        return err

    def _max_n(self):
        return min(E.MAX_WISPS_BOB, self.mana) if self.mode == "bob" else E.MAX_WISPS_ROOM

    def _a_set_n(self, role, p):
        if self.phase != "setup" or role != "bob":
            return "not now"
        n = int(p.get("n", 0))
        if not E.MIN_WISPS <= n <= self._max_n():
            return "bad number of wisps"
        self.n = n
        if self.mode == "bob":
            self.mana -= n
        self.a_bits, self.a_lens = E.prepare(self.rng, n)
        self.phase = "alice"
        return None

    def _bits(self, seq, n, lo, hi):
        return isinstance(seq, list) and len(seq) == n and all(isinstance(x, int) and lo <= x <= hi for x in seq)

    def _a_alice_lock(self, role, p):
        if self.phase != "alice" or role != "alice":
            return "not now"
        n = int(p.get("n", 0))
        if not E.MIN_WISPS <= n <= E.MAX_WISPS_ROOM:
            return "bad number of wisps"
        if not (self._bits(p.get("bits"), n, 0, 1) and self._bits(p.get("lens"), n, 0, 1)):
            return "bad wisps"
        self.n, self.a_bits, self.a_lens = n, list(p["bits"]), list(p["lens"])
        self.phase = "eve"
        return None

    def _a_eve_lock(self, role, p):
        if self.phase != "eve" or role != "eve":
            return "not now"
        if not self._bits(p.get("choice"), self.n, -1, 1):
            return "bad taps"
        self.e_choice = list(p["choice"])
        return None

    def _a_bob_lock(self, role, p):
        if self.phase != "bob" or role != "bob":
            return "not now"
        if not self._bits(p.get("lens"), self.n, 0, 1):
            return "bad lenses"
        self.b_lens = list(p["lens"])
        return None

    def _a_set_sample(self, role, p):
        if self.phase != "sample" or role not in ("alice", "bob"):
            return "not now"
        if role == "alice" and "bob" in self.humans:
            return "Bob chooses"
        f = float(p.get("fraction", 0))
        if f not in E.SAMPLE_FRACTIONS:
            return "bad share"
        self.fraction = f
        return None

    def _a_verdict(self, role, p):
        if self.phase != "verdict" or role not in ("alice", "bob"):
            return "not now"
        if p.get("choice") not in ("keep", "abort"):
            return "bad choice"
        if role in self.verdicts:
            return "already answered"
        self.verdicts[role] = p["choice"]
        return None

    def _a_next(self, role, p):
        if self.phase not in ("result", "over"):
            return "not now"
        if self.mode != "room" and (role not in self.humans):
            return "not a player"
        if self.mode == "room" and role not in ("table", *self.humans):
            return "not a player"
        if not self.alive and self.mode != "room":
            self._restart()
        else:
            self.round += 1
            self._begin_round()
        return None

    def _restart(self):
        keep, ver = self.history, self.version
        self.__init__(self.mode, self.humans)
        self.history, self.version = keep, ver

    # ---- views --------------------------------------------------------------------------------------------------------------
    def waiting_on(self):
        """Roles the game is waiting on. A phase only stays open while a human is needed."""
        ph = self.phase
        if ph == "setup":
            return ["bob"]
        if ph in ("alice", "eve", "bob"):
            return [ph] if ph in self.humans else []
        if ph == "sample":
            return ["bob"] if "bob" in self.humans else (["alice"] if "alice" in self.humans else [])
        if ph == "verdict":
            return [r for r in ("alice", "bob") if r in self.humans and r not in self.verdicts]
        return []

    def view(self, role):
        """What `role` (alice, bob, eve or table) may see right now."""
        ph = self.phase
        v = dict(version=self.version, mode=self.mode, role=role, humans=sorted(self.humans), phase=ph,
                 round=self.round + 1, name=self.cfg["name"], goal=self.cfg["goal"], fact=self.cfg.get("fact", ""), solo=self.mode != "room", storm=self.storm, n=self.n,
                 waiting=self.waiting_on(), alive=self.alive, score=self.score, towers=self.towers, eveTotal=self.eve_total,
                 mana=self.mana, manaMax=E.MANA_CAP, maxN=self._max_n(), minN=E.MIN_WISPS, threshold=E.THRESHOLD,
                 fractions=list(E.SAMPLE_FRACTIONS), fraction=self.fraction, history=self.history[-8:])
        at_public = ph in ("sample", "verdict", "result", "over")
        if role == "alice" and self.a_bits is not None and ph != "alice":
            v.update(aBits=self.a_bits, aLens=self.a_lens)
        if role == "eve" and self.e_choice is not None:
            v.update(eChoice=self.e_choice, eRes=self.e_res)
        if role == "bob" and self.b_lens is not None:
            v.update(bLens=self.b_lens, bRes=self.b_res)
        if at_public and self.b_lens is not None:
            v.update(aLens=self.a_lens, bLens=self.b_lens, sifted=self.sifted)
        if ph in ("verdict", "result") and self.sample is not None:
            v.update(sample=self.sample, sampleA=[self.a_bits[i] for i in self.sample],
                     sampleB=[self.b_res[i] for i in self.sample],
                     errors=sum(self.a_bits[i] != self.b_res[i] for i in self.sample),
                     qber=sum(self.a_bits[i] != self.b_res[i] for i in self.sample) / max(1, len(self.sample)))
            v["verdicts"] = {r: (c if r == role or ph == "result" else "locked") for r, c in self.verdicts.items()}
        if ph == "result" or ph == "over":
            if self.result:
                v["result"] = self.result
                v.update(aBits=self.a_bits, aLens=self.a_lens, eChoice=self.e_choice, eRes=self.e_res,
                         bLens=self.b_lens, bRes=self.b_res)
        return v
