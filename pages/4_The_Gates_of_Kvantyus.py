import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from qc_theme import apply_theme

st.set_page_config(page_title="Quantum Café - The Gates of Kvantyus", layout="wide")
apply_theme()

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Game settings. The numbers come from balance simulations of assets/gate_engine.js on the fixed deck
# (balanced picks of examined creatures: good trait choices save the city about two games in three,
# a skin-only or noise-heavy sentinel rarely does).
GATE_CONFIG = dict(
    budget=36,          # mana; examining one creature costs one mana per trait the sentinel looks at
    steps=80,           # training steps
    maxFoes=0.15,       # the city is lost if more than this share of those who enter are Nobbubys ...
    minFriends=0.75,    # ... or if fewer than this share of the Kvantyonis are let in
    names=dict(skin="Skin tone", hair="Hair colour", ears="Ear length",
               horns="Horn length", glow="Eye glow", strength="Strength"),
)


def read_asset(name):
    return (ASSETS / name).read_text(encoding="utf-8")


st.markdown('<div class="qc-eyebrow">Session 4 · From Theory to Practice</div>', unsafe_allow_html=True)
st.title("The Gates of Kvantyus")
st.markdown(
    '<p class="qc-lede">Guard the city with a sentinel that learns. You cannot examine every traveller, '
    'so choose what to look at, show it a few examples, and let a quantum classifier judge the rest.</p>',
    unsafe_allow_html=True,
)
st.write("")

html = (
    read_asset("gate_ui.html")
    .replace("__ENGINE__", read_asset("gate_engine.js"))
    .replace("__DECK__", read_asset("gate_deck.json"))
    .replace("__CFG__", json.dumps(GATE_CONFIG))
)
components.html(html, height=900, scrolling=False)
st.caption("The travellers are made up for the game. The sentinel is a real variational quantum circuit, "
           "simulated in your browser.")

with st.expander("What is going on?"):
    st.markdown(
        r"""
**This is a classification task.** Each traveller is described by up to six numbers (skin tone, hair colour, ear length, horn
length, eye glow, strength), each squeezed into an angle between $0$ and $\pi$. Some travellers are friends, some are foes.
You show the sentinel a few labelled examples (the *training set*) and it must label everyone else (the *test set*).

**Encoding.** Each trait you pick gets one qubit. A trait value $x$ becomes a rotation $R_y(x)$, which tilts the qubit from
$|0\rangle$ ($x=0$) to $|1\rangle$ ($x=\pi$). Because the range stops at $\pi$, different values always give different
states. This step is called a *feature map*.

**The learnable circuit.** After the data are loaded, every qubit gets two rotations whose angles are free parameters, and a
ring of controlled-Z gates entangles neighbouring qubits, so the sentinel can use *combinations* of traits (for example
"horned **and** glowing"). The data are loaded again for a second layer (*data re-uploading*), which makes the decision
boundary more flexible. In total there are $2nL+1$ parameters for $n$ qubits and $L=2$ layers.

**The verdict.** The circuit is measured and the average of $\langle Z\rangle$ over all qubits, plus a learnable offset, is the
sentinel's opinion: positive means friend, negative means foe.

**Training.** The parameters are tuned to shrink the squared error between the opinion and the true label of your examined
creatures. The gradient of each parameter is obtained by running the circuit twice with that rotation shifted by $\pm\pi/2$
(the *parameter-shift rule*), the same trick used on real quantum hardware. The optimiser is Adam.

**Why the game is about the data.**
- *More traits means more qubits and more parameters*, which need more examples. Mana buys either many examples of few traits
  or few examples of many traits.
- Some traits carry no information at all. They add parameters that learn nothing and can mislead the sentinel.
- Some traits are only informative **together**, which is where entanglement helps the sentinel.
- A sentinel that **remembers** its training creatures perfectly can still fail on strangers. That is overfitting, and the
  difference between the two percentages in the final sheet shows it.

*Simplifications:* the quantum circuit is simulated exactly, with no hardware noise and no sampling error; the deck is fixed, so
you can compare strategies with other players.
"""
    )
