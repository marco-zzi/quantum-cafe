import socket
import segno
import streamlit as st

import qkd_study as study
from qc_theme import apply_theme
from qkd_game import Game
from qkd_rooms import Registry
from qkd_widget import qkd as _qkd

st.set_page_config(page_title="Quantum Café - The Messenger Wisps", layout="wide")
apply_theme()

PAGE_PATH = "The_Messenger_Wisps"
PUBLIC_BASE = "https://quantumcafe.streamlit.app"      # used in the QR codes when the request gives no host


@st.cache_resource
def registry():
    return Registry()


REG = registry()
qp = st.query_params
ROLE_BLURB = {
    "alice": "Prepares the wisps and keeps their runes secret.",
    "bob": "Catches the wisps and reads their runes.",
    "eve": "Taps the wisps and tries to learn the key unseen.",
}


# ---------- helpers ----------
def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def base_url():
    """Address phones can reach. On the hosted app it comes from the request headers; locally it is this machine's LAN address."""
    override = st.session_state.get("qkd_base", "").strip().rstrip("/")
    if override:
        return override
    h = st.context.headers
    host = h.get("X-Forwarded-Host") or h.get("Host")
    if not host:
        return PUBLIC_BASE
    proto = (h.get("X-Forwarded-Proto") or "http").split(",")[0].strip()
    if host.startswith(("localhost", "127.0.0.1", "[::1]")):
        port = host.split(":")[1] if ":" in host else "8501"
        return f"http://{lan_ip()}:{port}"
    return f"{proto}://{host}"


def client_ip():
    ip = getattr(st.context, "ip_address", None)
    if ip:
        return ip
    return (st.context.headers.get("X-Forwarded-For") or "").split(",")[0].strip()


def qr_svg(url):
    return segno.make(url, error="m").svg_inline(scale=1, border=2, dark="#0b0b10", light="#ffffff", omitsize=True)


# ---------- Play: solo ----------
def solo_game(mode):
    g = st.session_state.get("qkd_game")
    if g is None or g.mode != mode:
        role = mode
        g = Game(mode, {role})
        st.session_state.qkd_game = g
        st.session_state.qkd_gen = st.session_state.get("qkd_gen", 0) + 1
    return g


@st.fragment
def solo_fragment(mode):
    g = solo_game(mode)
    act = _qkd(dict(kind="game", view=g.view(mode)), key=f"qkd_solo_{st.session_state.qkd_gen}")
    if act and act.get("type") == "act" and act.get("nonce") != st.session_state.get("qkd_nonce"):
        st.session_state.qkd_nonce = act["nonce"]
        g.act(mode, act.get("kind"), act.get("payload"))
        st.rerun(scope="fragment")


# ---------- Play: a phone with a seat ----------
@st.fragment(run_every=1.0)
def seat_fragment(code, token):
    room = REG.get(code)
    role = room.role_for(token) if room else None
    client = st.session_state.get("qkd_client")
    if not room or not role:
        payload = dict(kind="missing")
    elif not client:
        payload = dict(kind="hello")
    else:
        _, status = REG.claim(code, token, client)
        if status != "ok":
            payload = dict(kind=status)
        else:
            view = REG.view(code, role)
            payload = dict(kind="lobby", role=role, code=code) if view["phase"] == "lobby" else dict(kind="game", view=view)
    val = _qkd(payload, key=f"qkd_seat_{code}_{role}")
    if not val:
        return
    if val.get("client") and val["client"] != client:
        st.session_state.qkd_client = val["client"]
        st.rerun(scope="fragment")
    if val.get("type") == "act" and role:
        REG.act(code, role, val.get("kind"), val.get("payload"), val.get("nonce"))
        st.rerun(scope="fragment")


# ---------- Play: the table (host device) ----------
def lobby_cards(room):
    base = base_url()
    cards = []
    for role in ("alice", "bob", "eve"):
        url = f"{base}/{PAGE_PATH}?room={room.code}&seat={room.tokens[role]}"
        joined = role in room.claimed
        chip = '<span class="qc-chip">Joined</span>' if joined else '<span class="qc-chip off">Waiting for a phone</span>'
        qr = f'<div style="width:100%;max-width:190px;margin:8px auto 4px;border-radius:14px;overflow:hidden;opacity:{.25 if joined else 1}">{qr_svg(url)}</div>'
        cards.append(
            f'<div class="qc-card" style="align-items:stretch"><div class="qc-eyebrow" style="margin:0">{role.capitalize()}</div>'
            f'<div class="t">{role.capitalize()}</div><div class="d">{ROLE_BLURB[role]}</div>{qr}'
            f'<a class="d" style="font-size:11.5px;word-break:break-all;opacity:.75" href="{url}" target="_blank">{url}</a>{chip}</div>')
    return '<div class="qc-grid" style="grid-template-columns:repeat(auto-fit,minmax(210px,1fr))">' + "".join(cards) + "</div>"


@st.fragment(run_every=1.0)
def table_fragment(code, host):
    room = REG.get(code)
    if not room or room.host_token != host:
        st.warning("This room has closed.")
        if st.button("Open a new room"):
            st.query_params.clear()
            st.rerun()
        return
    if room.game is None:
        n = len(room.claimed)
        st.markdown(f'<div class="qc-eyebrow">Room {code}</div>', unsafe_allow_html=True)
        st.subheader("Scan a code to take a seat")
        st.caption("Each phone scans one code. Roles without a phone are played by the spell itself. At least two phones are needed.")
        st.markdown(lobby_cards(room), unsafe_allow_html=True)
        c1, c2 = st.columns([1, 3])
        with c1:
            if st.button("Play", type="primary", disabled=n < 2, use_container_width=True):
                err = REG.play(code, host)
                if err:
                    st.error(err)
                st.rerun(scope="fragment")
        with c2:
            who = ", ".join(r.capitalize() for r in ("alice", "bob", "eve") if r in room.claimed) or "nobody yet"
            bots = ", ".join(r.capitalize() for r in ("alice", "bob", "eve") if r not in room.claimed)
            st.caption(f"Phones joined: {who}." + (f" Played by the spell: {bots}." if bots and n else ""))
        return
    view = REG.view(code, "table")
    val = _qkd(dict(kind="game", view=view), key=f"qkd_table_{code}")
    if val and val.get("type") == "act":
        REG.act(code, "table", val.get("kind"), val.get("payload"), val.get("nonce"))
        st.rerun(scope="fragment")
    if st.button("Back to the lobby (same seats)"):
        REG.reset(code, host)
        st.rerun(scope="fragment")


def play_tab():
    room_code, seat, host = qp.get("room"), qp.get("seat"), qp.get("host")
    if room_code and seat:
        seat_fragment(room_code.upper(), seat)
        return
    if room_code and host:
        table_fragment(room_code.upper(), host)
        if st.button("Close this room"):
            st.query_params.clear()
            st.rerun()
        return
    mode = st.session_state.get("qkd_mode")
    if mode:
        if st.button("Change how you play"):
            st.session_state.qkd_mode = None
            st.session_state.pop("qkd_game", None)
            st.rerun()
        solo_fragment(mode)
        return
    left, mid, right = st.columns(3, gap="medium")
    cards = [
        (left, "Solo", "Be Bob", "Choose the lenses, read the key and decide: was Eve listening? The other two are played by the spell.", "bob"),
        (mid, "Solo", "Be Eve", "Tap the wisps and learn what you can without being caught. Alice and Bob are played by the spell.", "eve"),
        (right, "With friends", "Host a game", "This screen becomes the table. Up to three phones scan a code each and take a seat: Alice, Bob and Eve.", "host"),
    ]
    for col, eyebrow, title, text, key in cards:
        with col:
            st.markdown(f'<div class="qc-card"><div class="qc-eyebrow" style="margin:0">{eyebrow}</div><div class="t">{title}</div><div class="d">{text}</div></div>',
                        unsafe_allow_html=True)
            if st.button(title, key=f"start_{key}", use_container_width=True):
                if key == "host":
                    room = REG.create(client_ip())
                    st.query_params.update(room=room.code, host=room.host_token)
                else:
                    st.session_state.qkd_mode = key
                st.rerun()
    with st.expander("Phones cannot reach this address?"):
        st.text_input("Address phones should use", key="qkd_base", placeholder=base_url(),
                      help="Used in the QR codes. On a local run, phones must be on the same network.")


# ---------- Study ----------
def key_chips(bits, marks=None, known=()):
    marks = marks or {}
    out = []
    for i, b in enumerate(bits):
        style = {"bad": "background:rgba(255,69,58,.25)", "ok": "background:rgba(50,215,75,.22)", "fix": "background:rgba(255,214,120,.3)"}.get(marks.get(i), "background:rgba(255,255,255,.08)")
        if i in known:
            style = "background:rgba(255,69,58,.25)"
        gap = "margin-right:10px;" if i % 4 == 3 else ""
        out.append(f'<span style="display:inline-block;width:26px;height:30px;line-height:30px;text-align:center;border-radius:8px;{style};{gap}'
                   f'font-variant-numeric:tabular-nums;font-weight:700">{b}</span>')
    return '<div style="display:flex;flex-wrap:wrap;gap:4px;margin:4px 0">' + "".join(out) + "</div>"


def last_key():
    g = st.session_state.get("qkd_game")
    if g is not None and g.result and g.result["key"]:
        r = g.result
        a = [g.a_bits[i] for i in r["key"]]
        b = [g.b_res[i] for i in r["key"]]
        known = sorted(j for j, i in enumerate(r["key"]) if i in set(r["eve_known"]))
        return a, b, known, True
    a, b, known = study.demo_key()
    return a, b, known, False


def study_tab():
    a, b, known, real = last_key()
    st.markdown("### The steps")
    st.markdown(
        "1. **Release.** Alice gives every wisp a random rune (0 or 1) and a random lens, Sun or Moon.\n"
        "2. **Catch.** Bob picks a lens for each wisp. With the same lens as Alice he reads her rune. With the other lens his result is a coin flip.\n"
        "3. **Announce.** The towers say aloud which lenses they used, never the runes. They keep the bits where the lenses matched, about half. This is *sifting*.\n"
        "4. **Check.** They sacrifice a random share of the sifted bits and compare them aloud. A spy leaves a mark: **about one bit in four** disagrees if she tapped every wisp "
        "(she guesses the wrong lens half the time, and then Bob's result is wrong half the time). Honest noise adds to the count. Above roughly **11%** no secret can be made.\n"
        "5. **Distil.** The towers correct the leftover mistakes and shrink the key so that whatever Eve might know is squeezed out. The two panels below show how, "
        + ("on **your last key**." if real else "on an example key (finish a round as Bob to use your own).")
    )
    st.info("Eve cannot copy a wisp: an unknown quantum state cannot be cloned, so to learn anything she must measure it, and measuring disturbs it. That is the whole security of the check.")

    st.markdown("### Error correction")
    st.caption("Parities, spoken aloud, locate and fix the bits the storm flipped. Every parity spoken is a bit Eve hears as well.")
    steps = study.cascade_trace(a, b)
    s = st.slider("Step", 0, len(steps) - 1, 0, key="qkd_ec_step")
    cur = steps[s]
    st.markdown(f"**Alice**{key_chips(a)}**Bob**{key_chips(cur['b'], cur['marks'])}", unsafe_allow_html=True)
    st.write(cur["text"])
    st.caption(f"Parity bits spoken aloud so far: {cur['leaked']}")

    st.markdown("### Privacy amplification")
    st.caption("Even a corrected key may be partly known to Eve. Hashing shrinks it: each new bit is the parity of a random subset of the old key.")
    L = len(a)
    ks = sorted(known)
    st.markdown(f"**Corrected key** (red = bits Eve holds for certain: {len(ks)} of {L})" + key_chips(a, known=set(ks)), unsafe_allow_html=True)
    default = max(1, L - len(ks) - 2)
    m = st.slider("Length of the final key", 1, L, min(default, L), key="qkd_pa_out")
    rows = study.hash_matrix(L, m)
    final = study.amplify(a, rows)
    unc = study.eve_uncertainty(rows, L, ks)
    st.markdown("**Final key**" + key_chips(final), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Final bits", m)
    c2.metric("Eve is unsure about", f"{unc} of {m}")
    c3.metric("Rule of thumb", f"≤ {max(0, L - len(ks))}", help="Key length minus the bits Eve knows, minus a safety margin")
    if unc == m:
        st.success("Every final bit still depends on bits Eve does not have, so she learns nothing she can use.")
    else:
        st.warning(f"Too long: {m - unc} of the final bits are fixed by what Eve already knows. Shrink the key further.")


def curtain_tab():
    st.markdown("### From story to science")
    st.markdown(
        """
| In the story | In the science |
| :--- | :--- |
| A wisp, made by the Spell of Winged Light | One photon, a qubit carried by light |
| The rune on a wisp (0 or 1) | The bit encoded in the photon |
| The Sun lens, the Moon lens | The two measurement bases (for example horizontal/vertical and diagonal polarisation) |
| Reading with the wrong lens | Measuring in the wrong basis: the result is random and the state is disturbed |
| The storm | Noise in the channel and detectors: it flips some bits even with no spy |
| Eve, the Scrying Crow | An eavesdropper using an intercept-and-resend attack |
| The Crow cannot copy a wisp | The no-cloning theorem |
| Announcing lenses aloud | The public classical channel (sifting) |
| Sacrificing bits to compare | Parameter estimation: the quantum bit error rate (QBER) |
| The 11% line | The asymptotic BB84 bound: no secret key can be distilled above roughly 11% |
| Mana | Time and photons spent on the link |
"""
    )
    st.markdown("### What the game leaves out")
    st.markdown(
        "- **Photon loss.** Real links lose most photons, and an attacker can exploit that. Here every wisp arrives.\n"
        "- **Single photons.** Real sources sometimes emit two photons, which opens an attack. Decoy states close it.\n"
        "- **Smarter spies.** Eve here always measures with a random lens. Real analysis must cover every attack that physics allows.\n"
        "- **Authentication.** The public channel must be authentic, or Eve could pretend to be Bob. Real systems use a small pre-shared key.\n"
        "- **Finite keys.** Small samples give uncertain error estimates, which is exactly the gamble you take when you send few wisps.\n\n"
        "The numbers in the rounds (storm levels, spy chances) are made up to teach, not measured."
    )


# ---------- page ----------
phone = bool(qp.get("room") and qp.get("seat"))
if not phone:
    st.markdown('<div class="qc-eyebrow">Session 3 · Cryptography, Cybersecurity &amp; Business</div>', unsafe_allow_html=True)
    st.title("The Messenger Wisps")
    st.markdown(
        '<p class="qc-lede">The Spell of Winged Light releases wisps: single sparks of light that can carry a rune across the land. '
        'Two towers need a secret that cannot be copied, and a Crow may be listening. '
        'Choose your lenses, read the signs and decide: keep the key, or abort?</p>',
        unsafe_allow_html=True,
    )
    st.write("")
    t_play, t_study, t_story = st.tabs(["Play", "Study the craft", "Behind the curtain"])
    with t_play:
        play_tab()
    with t_study:
        study_tab()
    with t_story:
        curtain_tab()
else:
    play_tab()
