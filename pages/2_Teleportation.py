import streamlit as st
import time
import numpy as np

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

st.title("🚀 Quantum Teleportation: Step-by-Step Protocol")
st.write("Follow the exact quantum mechanics workflow: State Preparation $\rightarrow$ Bell Measurement $\rightarrow$ Classical Bit Transmission $\rightarrow$ Bob's Correction Gates.")

# Session state initialization to track the steps
if "step" not in st.session_state:
    st.session_state.step = 1

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("🔬 Step-by-Step Interactive Workflow")
    
    # STEP 1: Alice selects state
    if st.session_state.step >= 1:
        st.markdown("### Step 1: Alice Prepares the Qubit")
        theta = st.slider("Polar Angle ($\theta$)", 0.0, 180.0, 60.0, key="t_angle")
        phi = st.slider("Phase Angle ($\varphi$)", 0.0, 360.0, 0.0, key="p_angle")
        
        if st.session_state.step == 1:
            if st.button("Lock State & Proceed to Step 2"):
                st.session_state.step = 2
                st.rerun()

    # STEP 2: Bell Measurement
    if st.session_state.step >= 2:
        st.markdown("---")
        st.markdown("### Step 2: Bell-State Measurement (VU Lab)")
        st.write("Alice interacts her qubit with her half of the shared entangled Bell pair and measures.")
        
        # User can select or simulate Alice's measurement outcome (which yields 2 classical bits)
        bell_outcome = st.selectbox("Alice's Measurement Outcome", ["00 (Φ+)", "01 (Ψ+)", "10 (Φ-)", "11 (Ψ-)"])
        
        if st.session_state.step == 2:
            if st.button("Perform Measurement & Send Bits"):
                st.session_state.step = 3
                st.rerun()

    # STEP 3 & 4: Transmission and Bob's Correction
    if st.session_state.step >= 3:
        st.markdown("---")
        st.markdown("### Step 3 & 4: Transmission & Bob's Correction (MKIC)")
        
        # Extract the 2 classical bits from Alice's outcome string
        bits = bell_outcome[:2]
        
        # Determine Bob's required correction gates based on standard teleportation rules
        correction_gate = "Identity ($I$)"
        if bits == "01":
            correction_gate = "Pauli-$X$ ($\sigma_x$)"
        elif bits == "10":
            correction_gate = "Pauli-$Z$ ($\sigma_z$)"
        elif bits == "11":
            correction_gate = "Pauli-$X$ and Pauli-$Z$"

        st.info(f"📡 Transmitted 2 classical bits: **{bits}** across Vilnius fiber link.")
        st.success(f"🛠️ Bob applies correction gate: **{correction_gate}**")
        
        if st.button("Reset Protocol"):
            st.session_state.step = 1
            st.rerun()

with col_right:
    st.subheader("🖥️ Protocol Status & Visualizer")
    
    # Calculate target coefficients
    theta_rad = np.radians(st.session_state.get("t_angle", 60.0))
    phi_deg = st.session_state.get("p_angle", 0.0)
    c0 = np.cos(theta_rad / 2)
    c1 = np.sin(theta_rad / 2)
    
    status_box = st.empty()
    
    if st.session_state.step == 1:
        status_box.warning("Status: Waiting for Alice to prepare the initial state.")
    elif st.session_state.step == 2:
        status_box.info("Status: State ready. Entangled pair active. Awaiting Bell measurement.")
    elif st.session_state.step >= 3:
        status_box.success(
            f"**Teleportation Successful!**\n\n"
            f"Original State (Alice):\n$|\\psi\\rangle = {c0:.2f}|0\\rangle + e^{{i{phi_deg}^\\circ}}{c1:.2f}|1\\rangle$\n\n"
            f"Reconstructed State (Bob):\n$|\\psi_{\\text{recalled}}\\rangle = {c0:.2f}|0\\rangle + e^{{i{phi_deg}^\\circ}}{c1:.2f}|1\\rangle$\n\n"
            f"Fidelity: **100%**"
        )
