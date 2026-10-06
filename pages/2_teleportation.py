import streamlit as st
import time

st.set_page_config(page_title="Quantum Teleportation Link", layout="wide")

st.title("🚀 Quantum Teleportation: Vilnius Lab to MKIC")
st.write("Prepare a qubit state at Alice's lab, entangle it across the city link, and measure it on Bob's rack screen.")

# Layout: Two columns for controls (Alice vs Bob) and a central visual container
col_alice, col_visual, col_bob = st.columns([1, 2, 1])

with col_alice:
    st.subheader("👩‍🔬 Alice's Origin Station")
    st.markdown("*VU Faculty of Physics*")
    
    # Rack knobs for state preparation
    theta_knob = st.slider("Rack Knob 1: Polar Angle (θ)", 0.0, 180.0, 45.0, key="alice_theta")
    phi_knob = st.slider("Rack Knob 2: Phase Angle (φ)", 0.0, 360.0, 0.0, key="alice_phi")
    
    prepare_btn = st.button("Prepare & Send Qubit State")

with col_bob:
    st.subheader("👨‍💻 Bob's Destination Station")
    st.markdown("*VU Library / MKIC*")
    
    # Bob selects measurement basis
    bob_basis = st.selectbox("Bob's Basis Selection", ["Rectilinear (Z)", "Diagonal (X)"])
    
    st.markdown("---")
    st.markdown("### 🖥️ Rack-Mounted Screen")
    screen_placeholder = st.empty()
    screen_placeholder.info("Awaiting incoming transmission...")

with col_visual:
    st.subheader("🌐 Isometric Quantum Network Link")
    
    # Visual simulation container using 2.5D styled HTML/CSS
    visual_placeholder = st.empty()
    
    def render_isometric_view(status, packet_class=""):
        html_code = f"""
        <div style="
            background: linear-gradient(135deg, #1e1e2f, #2a2a40);
            border-radius: 12px;
            padding: 20px;
            color: white;
            font-family: monospace;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            text-align: center;
        ">
            <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px;">
                <div style="background: #3b3b5c; padding: 10px; border-radius: 8px; border: 1px solid #575785;">
                    🏛️ <b>ALICE</b><br><span style="font-size: 11px; color: #aaa;">State: θ={theta_knob}°</span>
                </div>
                <div style="font-size: 20px; color: #00ffcc;" class="{packet_class}">⚡ === 🔄 === ⚡</div>
                <div style="background: #3b3b5c; padding: 10px; border-radius: 8px; border: 1px solid #575785;">
                    🏛️ <b>BOB</b><br><span style="font-size: 11px; color: #aaa;">Basis: {bob_basis[:3]}</span>
                </div>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; font-size: 12px; color: #00ffcc;">
                Status: {status}
            </div>
        </div>
        """
        visual_placeholder.markdown(html_code, unsafe_allow_html=True)

    render_isometric_view("Systems Ready. Entangled Bell pair active across fiber link.")

# Execution flow when Alice triggers transmission
if prepare_btn:
    with st.spinner("Establishing entanglement channel..."):
        render_isometric_view("Generating Bell pair ($\Phi^+$) between labs...", "pulse")
        time.sleep(0.8)
        
        render_isometric_view("Alice interacts qubit with local Bell state & measures...", "pulse")
        time.sleep(0.8)
        
        render_isometric_view("Transmitting 2 classical bits over Vilnius dark fiber...", "pulse")
        time.sleep(0.8)
        
        # Final outcome calculation based on knobs
        result_state = "|0⟩" if theta_knob < 90 else "|1⟩"
        if 40 <= theta_knob <= 50:
            result_state = "Superposition (|0⟩ + |1⟩)/√2"
            
        render_isometric_view("Teleportation complete! State reconstructed at destination.", "")
        
        screen_placeholder.success(f"State Reconstructed Successfully!\n\nMeasured State: **{result_state}**\nFidelity: **99.8%**")
