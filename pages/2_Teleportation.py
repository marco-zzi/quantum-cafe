import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Quantum Teleportation Protocol", layout="wide")

# Custom CSS for clean layout
st.markdown("""
    <style>
    /* Make top header background transparent */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0) !important;
    }

    /* Hide top-right action buttons (Deploy, main menu) only */
    [data-testid="stToolbarActions"],
    .stAppDeployButton,
    #MainMenu {
        display: none !important;
    }

    /* Hide footer and 'Manage app' bottom-right widget */
    footer,
    [data-testid="stFooter"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Explicitly preserve sidebar toggle arrow and page navigation controls */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stHeaderNav"],
    [data-testid="stSidebarNav"] {
        display: flex !important;
        visibility: visible !important;
        z-index: 1000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Quantum Teleportation Exercise & Protocol Simulator")
st.write(
    r"Learn how quantum teleportation works step-by-step using a pre-shared $|\Phi^+\rangle$ Bell state."
)

# Sidebar Reference / Lookup Table
with st.sidebar:
    st.header("📖 Protocol Lookup Table")
    st.markdown(
        r"""
        Shared Pair: $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$

        | Measured Bell State | Classical Bits | Bob's Gate |
        | :--- | :---: | :---: |
        | $\vert\Phi^+\rangle$ | **00** | $I$ (None) |
        | $\vert\Psi^+\rangle$ | **01** | $X$ (Bit flip) |
        | $\vert\Phi^-\rangle$ | **10** | $Z$ (Phase flip) |
        | $\vert\Psi^-\rangle$ | **11** | $Z \cdot X$ (Both) |
        """
    )

# Session state management
if "step" not in st.session_state:
    st.session_state.step = 1
if "bell_measured" not in st.session_state:
    st.session_state.bell_measured = None

col_main, col_info = st.columns([1.3, 1])

with col_main:
    # STEP 1: State Preparation
    st.markdown(r"### Step 1: Alice Prepares an Arbitrary State $|\psi\rangle$")
    theta = st.slider(r"Polar Angle ($\theta$)", 0.0, 180.0, 60.0, key="t_angle")
    phi = st.slider(r"Phase Angle ($\varphi$)", 0.0, 360.0, 0.0, key="p_angle")
    
    # Calculate state coefficients
    theta_rad = np.radians(theta)
    alpha = np.cos(theta_rad / 2)
    beta = np.sin(theta_rad / 2)
    
    st.latex(fr"|\psi\rangle = {alpha:.2f}|0\rangle + e^{{i{phi:.0f}^\circ}}{beta:.2f}|1\rangle")

    if st.session_state.step == 1:
        if st.button("Lock State & Prepare Entangled Pair"):
            st.session_state.step = 2
            st.rerun()

    # STEP 2: Probabilistic Bell Measurement
    if st.session_state.step >= 2:
        st.markdown("---")
        st.markdown("### Step 2: Alice Performs Bell-State Measurement")
        st.caption("The outcome is inherently probabilistic (25% probability for each Bell state).")
        
        if st.session_state.bell_measured is None:
            if st.button("🎲 Measure Alice's Qubits"):
                bell_outcomes = [
                    (r"$|\Phi^+\rangle$", "00", "Identity (I)"),
                    (r"$|\Psi^+\rangle$", "01", "Pauli-X"),
                    (r"$|\Phi^-\rangle$", "10", "Pauli-Z"),
                    (r"$|\Psi^-\rangle$", "11", "Pauli-Z then Pauli-X")
                ]
                st.session_state.bell_measured = random.choice(bell_outcomes)
                st.session_state.step = 3
                st.rerun()
        else:
            state_str, correct_bits, correct_gate = st.session_state.bell_measured
            st.info(f"Alice's measurement collapsed to: **{state_str}**")

    # STEP 3: Exercise - User selects classical bits and Bob's operation
    if st.session_state.step >= 3:
        st.markdown("---")
        st.markdown("### Step 3: Select Classical Bits & Bob's Correction")
        
        state_str, correct_bits, correct_gate = st.session_state.bell_measured
        
        user_bits = st.radio(
            f"Based on measuring {state_str}, which 2 bits should Alice transmit?",
            ["00", "01", "10", "11"],
            horizontal=True
        )
        
        user_gate = st.selectbox(
            r"Which correction gate must Bob apply to restore $|\psi\rangle$?",
            ["Identity (I)", "Pauli-X", "Pauli-Z", "Pauli-Z then Pauli-X"]
        )

        if st.button("Verify & Apply Correction"):
            if user_bits == correct_bits and user_gate == correct_gate:
                st.success("✅ Correct! The protocol restored Alice's state perfectly at Bob's station.")
                st.session_state.step = 4
            else:
                st.error(
                    f"❌ Incorrect configuration. For {state_str}, the required bits are "
                    f"**{correct_bits}** and Bob's required gate is **{correct_gate}**. Check the sidebar table!"
                )

    if st.session_state.step >= 4:
        if st.button("🔄 Reset Experiment"):
            st.session_state.step = 1
            st.session_state.bell_measured = None
            st.rerun()

with col_info:
    st.subheader("🖥️️ Protocol Monitor")
    
    if st.session_state.step == 1:
        st.warning("Awaiting state preparation...")
    elif st.session_state.step == 2:
        st.info(r"State locked. Entangled $|\Phi^+\rangle$ pair shared between VU Physics and MKIC.")
    elif st.session_state.step >= 3:
        state_str, correct_bits, correct_gate = st.session_state.bell_measured
        st.markdown("#### Live State Telemetry")
        st.markdown(fr"- **Alice's Input State:** $|\psi\rangle = {alpha:.2f}|0\rangle + {beta:.2f}|1\rangle$")
        st.markdown(f"- **Bell Basis Collapse:** {state_str}")
        st.markdown(f"- **Transmitted Channel Bits:** `{correct_bits}`")
        st.markdown(f"- **Bob's Applied Unitary:** {correct_gate}")
        
        if st.session_state.step == 4:
            st.success(
                fr"**Reconstructed Output at Bob's Station:**"
                "\n\n"
                fr"$|\psi\rangle_{{\text{{Bob}}}} = {alpha:.2f}|0\rangle + e^{{i{phi:.0f}^\circ}}{beta:.2f}|1\rangle$"
                "\n\n"
                fr"**Fidelity:** 100%"
            )
