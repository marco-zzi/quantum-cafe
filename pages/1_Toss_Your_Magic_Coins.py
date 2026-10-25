import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from qc_theme import apply_theme

st.set_page_config(page_title="Quantum Café - Toss your magic coins", layout="wide")
apply_theme()

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def b64(name):
    try:
        return base64.b64encode((ASSETS / name).read_bytes()).decode("utf-8")
    except FileNotFoundError:
        return ""


st.markdown('<div class="qc-eyebrow">Session 1 · Demystifying Reality</div>', unsafe_allow_html=True)
st.title("Toss your magic coins")
st.markdown(
    '<p class="qc-lede">Each coin is a qubit. Tilt it to change the odds, entangle a few, then measure '
    'to read out a truly random byte.</p>',
    unsafe_allow_html=True,
)
st.write("")

html = (
    (ASSETS / "coins_ui.html").read_text(encoding="utf-8")
    .replace("__FRONT__", b64("QRNG_0.png"))
    .replace("__BACK__", b64("QRNG_1.png"))
    .replace("__EDGE__", b64("QRNG_edge.png"))
    .replace("__TABLE_D__", b64("QRNG_table_desktop.jpg"))
    .replace("__TABLE_M__", b64("QRNG_table_mobile.jpg"))
)
components.html(html, height=900, scrolling=True)

with st.expander("What am I looking at?"):
    st.markdown(
        r"""
Each coin stands for one **qubit**. Its tilt sets the probability of reading a 1: a coin turned a quarter of the way
is a superposition of 0 and 1, and the label shows $P(1)=\sin^2(\theta/2)$.

**Measuring** forces every coin to land heads or tails, and the eight results form a byte. Because the outcome of a
quantum measurement is not decided beforehand, the byte is genuinely random.

**Bell pair and GHZ triple** link coins by entanglement: their results always agree, even though each one on its
own is still a fair coin flip.
"""
    )
