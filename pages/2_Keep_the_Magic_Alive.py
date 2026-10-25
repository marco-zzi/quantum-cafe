import json
from pathlib import Path

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import streamlit.components.v1 as components

from qc_model import (
    PRESETS, CODES, CRAFTS, ASSISTANTS, FIDELITY_LOST, X_LOST,
    platform_model, ops_until_lost, qec_cycle, rite_config,
)
from qc_theme import apply_theme, rgb_hex

st.set_page_config(page_title="Quantum Café - Keep the Magic Alive", layout="wide")
apply_theme()

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def read_asset(name):
    return (ASSETS / name).read_text(encoding="utf-8")


def fmt_ops(n):
    if n >= 1e6:
        return f"{n/1e6:.1f} million"
    if n >= 100:
        return f"{n:,.0f}"
    return f"{n:.0f}" if n >= 10 else f"{n:.1f}"


def fmt_time(s):
    for unit, scale in (("s", 1), ("ms", 1e-3), ("µs", 1e-6), ("ns", 1e-9), ("ps", 1e-12)):
        if s >= scale:
            return f"{s/scale:.3g} {unit}"
    return f"{s:.2g} s"


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.markdown('<div class="qc-eyebrow">Session 2 · The Hardware Frontier</div>', unsafe_allow_html=True)
st.title("Keep the Magic Alive")
st.markdown(
    '<p class="qc-lede">Every spell, potion and ritual has one enemy: the world around it. '
    'In a quantum computer that enemy is called decoherence. How many steps can you finish before the magic is lost?</p>',
    unsafe_allow_html=True,
)
st.write("")

tab_play, tab_study, tab_story = st.tabs(["Play the rite", "Study the craft", "Behind the curtain"])

# ---------------------------------------------------------------------------
# Tab 1: the game
# ---------------------------------------------------------------------------
with tab_play:
    st.markdown(
        "You are a spell-crafter. Choose a craft and cast it step by step. Three forces keep drifting "
        "against you and mana is limited, so decide what to protect: **drag a force to the right** to push it "
        "back, or tap it for a quick boost. You can also hire a helper, a quantum error-correcting code. "
        "It costs mana every step and can keep the magic steady, but when the world is too wild it makes things worse."
    )
    # The game keeps all its state in the browser, so using a widget elsewhere on the page never resets it.
    game_html = (
        read_asset("rite_ui.html")
        .replace("__ENGINE__", read_asset("rite_engine.js"))
        .replace("__CFG__", json.dumps(rite_config()))
    )
    components.html(game_html, height=1000, scrolling=True)
    st.caption("All platform numbers are illustrative orders of magnitude chosen for teaching, "
               "not vendor specifications.")

# ---------------------------------------------------------------------------
# Tab 2: the sandbox
# ---------------------------------------------------------------------------
DEFAULT_KNOBS = dict(iso=50, noise=50, temp=50)


def reset_knobs():
    for key, v in DEFAULT_KNOBS.items():
        st.session_state[key] = v


for key, v in DEFAULT_KNOBS.items():
    st.session_state.setdefault(key, v)


def craft_label(name):
    return f"{CRAFTS[name]['name']}  ·  {name}"


with tab_study:
    st.write("No game here. Set the three forces yourself and read the numbers.")
    col_ctrl, col_view = st.columns([1, 1.7], gap="large")

    with col_ctrl:
        st.markdown('<div class="qc-eyebrow" style="margin-top:6px">Controls</div>', unsafe_allow_html=True)
        preset_name = st.selectbox("Craft (hardware platform)", list(PRESETS), key="preset",
                                   on_change=reset_knobs, format_func=craft_label)
        preset = PRESETS[preset_name]
        craft = CRAFTS[preset_name]
        accent_hex = rgb_hex(craft["accent"])
        st.caption(craft["why"])

        iso = st.slider(f"Wards: {craft['wards'].lower()}", 0, 100, key="iso",
                        help="Isolation. Higher slows every decay process by up to 10x.")
        noise = st.slider(f"Chaos: {craft['chaos'].lower()}", 0, 100, key="noise",
                          help="Noise. More speeds up dephasing and adds control errors, by up to 10x.")
        temp = st.slider(f"Heat: {craft['heat'].lower()}", 0, 100, key="temp",
                         help="Temperature. " + preset["temp_note"])
        st.caption("50 is typical lab conditions for this platform. Every 25 steps changes the effect "
                   "by about 3x, across a range of 0.1x to 10x.")

        st.divider()
        use_qec = st.toggle("Hire a helper (error correction)", value=False,
                            disabled=preset["kind"] == "loss",
                            help="Encode the qubit in several physical qubits and repair errors every few operations.")
        if preset["kind"] == "loss":
            st.caption("Lost light cannot be mended by these helpers (photon loss needs special "
                       "loss-tolerant codes), so the option is off for this craft.")
        code_name = k_cycle = None
        if use_qec:
            code_name = st.radio("Helper", list(CODES), index=0,
                                 format_func=lambda c: f"{ASSISTANTS[c]['name']}: {c}")
            k_cycle = st.slider("Operations between correction rounds", 1, 20, 5)

    model = platform_model(preset, iso, noise, temp)
    delta = model["d_relax"] + model["d_phase"]
    n_lost = ops_until_lost(delta)

    qec = None
    if use_qec:
        code = CODES[code_name]
        x_cycle, p_L = qec_cycle(model, k_cycle, code)
        if x_cycle > 0:
            qec = dict(code=code, x_cycle=x_cycle, p_L=p_L,
                       n_lost=k_cycle * np.log(X_LOST) / np.log(x_cycle),
                       ln_per_op=np.log(x_cycle) / k_cycle)

    with col_view:
        c1, c2, c3 = st.columns(3)
        c1.metric("Operations until lost", fmt_ops(n_lost),
                  help=f"Fidelity with the original state drops below {FIDELITY_LOST:.0%}.")
        if model["kind"] == "decoherence":
            c2.metric("Coherence time (T2)", fmt_time(model["T2"]))
            c3.metric("Time until lost", fmt_time(n_lost * model["t_gate"]))
        else:
            c2.metric("Loss per component", f"{(1 - np.exp(-model['d_relax'])):.1%}")
            c3.metric("Interference error", f"{model['d_phase']:.2%}")
        if qec:
            gain = qec["n_lost"] / n_lost
            if gain > 1.05:
                st.success(f"With a helper: **{fmt_ops(qec['n_lost'])} operations** ({gain:.1f}x more). "
                           "Errors are rare enough that fixing them beats making them.")
            else:
                st.error(f"With a helper: **{fmt_ops(qec['n_lost'])} operations** ({gain:.2f}x). "
                         "The helper itself adds too many errors. Calm the chaos or strengthen the wards "
                         "to get below the threshold.")

        # Animated Bloch-vector widget (the "scrying glass")
        n_view = max(40.0, 3 * n_lost)
        cfg = dict(
            delta=float(delta), rate1=float(model["rate1"]), z_eq=float(model["z_eq"]),
            n_lost=float(n_lost), n_view=float(n_view), t_gate=float(model["t_gate"]),
            show_time=model["kind"] == "decoherence", f_lost=FIDELITY_LOST, x_lost=X_LOST,
            qec_per_op=float(qec["ln_per_op"]) if qec else None, accent=craft["accent"],
        )
        st.caption("The scrying glass: the arrow is the qubit's state. As it shrinks to the centre, the information is gone.")
        components.html(
            read_asset("bloch.html").replace("__CFG__", json.dumps(cfg)).replace("__ACC__", ",".join(map(str, craft["accent"]))),
            height=520,
        )

        ops = np.unique(np.geomspace(1, max(100.0, 8 * n_lost), 300))
        frames = [pd.DataFrame(dict(ops=ops, fidelity=(1 + np.exp(-ops * delta)) / 2, curve="No helper"))]
        colours = [accent_hex]
        domain = ["No helper"]
        if qec:
            frames.append(pd.DataFrame(dict(ops=ops, fidelity=(1 + np.exp(ops * qec["ln_per_op"])) / 2,
                                            curve="With helper")))
            colours.append("#32d74b")
            domain.append("With helper")
        df = pd.concat(frames)
        line = alt.Chart(df).mark_line(strokeWidth=3, strokeCap="round").encode(
            x=alt.X("ops:Q", scale=alt.Scale(type="log"), title="Operations performed (log scale)"),
            y=alt.Y("fidelity:Q", scale=alt.Scale(domain=[0.5, 1.0]), title="Fidelity with the original state"),
            color=alt.Color("curve:N", title=None, scale=alt.Scale(domain=domain, range=colours)),
        )
        rule = alt.Chart(pd.DataFrame(dict(y=[FIDELITY_LOST]))).mark_rule(
            strokeDash=[4, 4], color="#ff453a", opacity=.7).encode(y="y:Q")
        st.altair_chart((line + rule).properties(height=250), theme=None, width="stretch")
        st.caption(f"The dashed line marks the point where the magic counts as lost: fidelity below {FIDELITY_LOST:.0%}.")

    st.divider()
    st.markdown('<div class="qc-eyebrow">Side by side</div>', unsafe_allow_html=True)
    st.subheader("How many operations fit?")
    rows = []
    for name, p in PRESETS.items():
        m = platform_model(p, iso, noise, temp)
        d = m["d_relax"] + m["d_phase"]
        rows.append(dict(craft=CRAFTS[name]["name"], ops=ops_until_lost(d), colour=rgb_hex(CRAFTS[name]["accent"])))
    cmp_df = pd.DataFrame(rows)
    cmp_df["one"] = 1.0                                   # log axes need a baseline above zero
    bar = alt.Chart(cmp_df).mark_bar(cornerRadiusEnd=6, height=26).encode(
        y=alt.Y("craft:N", sort="-x", title=None),
        x=alt.X("ops:Q", scale=alt.Scale(type="log", domain=[1, float(cmp_df["ops"].max()) * 2]),
                title="Operations before the magic is lost (log scale)"),
        x2="one:Q",
        color=alt.Color("craft:N", legend=None, scale=alt.Scale(domain=list(cmp_df["craft"]), range=list(cmp_df["colour"]))),
        tooltip=["craft", alt.Tooltip("ops:Q", format=",.0f")],
    )
    st.altair_chart(bar.properties(height=190), theme=None, width="stretch")
    st.caption("The same force settings are applied to every craft, each relative to its own typical conditions. "
               "The craft that lives longest is not always the one that fits the most steps: "
               "slow chants waste a long lifetime.")

# ---------------------------------------------------------------------------
# Tab 3: how the story maps to the science
# ---------------------------------------------------------------------------
with tab_story:
    st.markdown('<div class="qc-eyebrow">The mapping</div>', unsafe_allow_html=True)
    st.subheader("Which craft is which quantum computer?")
    rows = "".join(
        f"<tr><td><b>{c['name']}</b></td><td>{name}</td><td>{c['why']}</td></tr>" for name, c in CRAFTS.items()
    )
    st.markdown(f"<table><tr><th>Craft</th><th>Hardware</th><th>Why</th></tr>{rows}</table>", unsafe_allow_html=True)

    st.write("")
    st.subheader("What the forces and the helper really are")
    st.markdown(
        r"""
| In the story | In the lab |
| :--- | :--- |
| **Wards** | **Isolation**: shielding, vacuum, vibration damping, polished optics. Slows every decay process. |
| **Chaos** | **Noise**: stray electromagnetic fields, laser and control jitter. Scrambles the phase of the qubit and adds control errors. |
| **Heat** | **Temperature**: warmer means faster energy loss (relaxation, $T_1$) and faster dephasing. Light is the exception: optical photons do not care. |
| **Mana** | **Engineering effort and budget**: every cooling, shielding or calibration improvement costs resources, and the lab drifts back to its usual state without constant care. |
| **Helper** | **Quantum error correction**: the logical qubit is spread over several physical qubits, and errors are detected and repaired every few operations. It costs extra qubits and extra operations. |
| **Spoiled** | The state's fidelity with what you wanted has fallen below 90%: the stored information is no longer trustworthy. |
"""
    )
    st.write("")
    st.subheader("Why the helper sometimes makes things worse")
    st.markdown(
        "Checking the qubits takes extra operations, and those operations add their own errors. If the physical "
        "error rate is below a *threshold*, the repairs win. Above it, the helper does more damage than it prevents. "
        "The label under each helper in the game shows this live."
    )
    st.subheader("Why the Apprentice fails the frozen potion")
    st.markdown(
        "The 3-qubit code only repairs dephasing. A superconducting qubit mostly dies from energy loss, which this code "
        "cannot fix. A bigger code (the Circle of Nine) can, but only in calm conditions, and its upkeep eats your mana. "
        "Real machines use codes such as the surface code, with tens to thousands of physical qubits per logical qubit. "
        "That is why quality hardware matters so much."
    )
    st.subheader("Why light is different")
    st.markdown(
        "Photons barely interact with their surroundings, so they hardly decohere. They are lost instead, absorbed or "
        "scattered. A lost photon cannot be repaired by a simple helper."
    )
    st.write("")
    st.markdown(
        r"""
**The numbers behind a step.** The qubit starts in $|+\rangle$, the most fragile state. After $n$ operations its
Bloch vector has length $e^{-n\delta}$, with $\delta \approx t_\text{gate}\left(\tfrac{1}{2T_1}+\tfrac{1}{T_\varphi}\right)+\tfrac{4}{3}\varepsilon$
per operation. The magic is lost when the fidelity $(1+e^{-n\delta})/2$ drops below 0.9, which happens after about $\ln(1/0.8)/\delta$ operations.
"""
    )
    st.caption("Simplifications: errors are independent, each correction round costs a fixed number of extra noisy "
               "operation slots (4 for the 3-qubit code, 12 for the 9-qubit code), and measurement errors and "
               "fault-tolerant details are ignored. All platform numbers are illustrative orders of magnitude, not specifications.")
