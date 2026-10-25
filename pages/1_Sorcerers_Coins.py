import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from qc_theme import apply_theme

st.set_page_config(page_title="Quantum Café - Sorcerer's coins", layout="wide")
apply_theme()

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def b64(name):
    try:
        return base64.b64encode((ASSETS / name).read_bytes()).decode("utf-8")
    except FileNotFoundError:
        return ""


st.markdown('<div class="qc-eyebrow">Session 1 · Demystifying Reality</div>', unsafe_allow_html=True)
st.title("Sorcerer's coins")
st.markdown(
    '<p class="qc-lede">Duel a rival sorcerer with eight quantum coins. Whoever matches the goal pattern first wins. '
    'You cannot tilt the coins, but you can entangle them. How many rounds can you survive?</p>',
    unsafe_allow_html=True,
)
st.write("")

html = (
    (ASSETS / "sorcerers_ui.html").read_text(encoding="utf-8")
    .replace("__FRONT__", b64("QRNG_0.png"))
    .replace("__BACK__", b64("QRNG_1.png"))
    .replace("__EDGE__", b64("QRNG_edge.png"))
    .replace("__TABLE_D__", b64("QRNG_table_desktop.jpg"))
    .replace("__TABLE_M__", b64("QRNG_table_mobile.jpg"))
)
components.html(html, height=700, scrolling=True)

with st.expander("What is going on?"):
    st.markdown(
        r"""
Each coin is a **qubit** prepared in an equal superposition, so on its own it lands heads or tails with probability one half.
Nothing you do changes that. Matching a pattern of eight independent coins has probability $(1/2)^8 = 1/256$, and the toss
limit of 256 is exactly that number.

**Entanglement** links coins so that their results always agree. Two coins form a Bell pair,
$|\Phi^\pm\rangle=(|00\rangle\pm|11\rangle)/\sqrt2$, and three to eight coins form a GHZ state,
$(|0\cdots0\rangle\pm|1\cdots1\rangle)/\sqrt2$. A linked group is still a fair coin flip as a whole, but its members share one
outcome. A group that needs the same value everywhere in the pattern costs a single factor of one half instead of one half per
coin. A group that has to match a 1 and a 0 can never succeed while its links hold. The sign changes how the state behaves
under other measurements, not which faces land here.

**Links are a resource.** Joining a group of $k$ coins uses $k-1$ links, and you only have a few per round, like mana. That
is why you cannot always join everything.

**Entanglement is fragile.** Each link holds with some probability, and a group of $k$ coins stays entangled only if all
$k-1$ links hold. If one fails, the coins land independently, as if never linked. Bigger groups are more fragile, so the best
arrangement depends on how noisy the round is.

**The rival** plays the same game with a skill that rises each round: its chance per toss is a fraction of the best chance that
is possible with your budget and noise. The stars rate your arrangement against that best chance, not your luck.
"""
    )
