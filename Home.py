import streamlit as st

st.set_page_config(
    page_title="Quantum Café",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean layout
st.markdown("""
<style>
    footer { visibility: hidden; }
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
    .sub-title { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">☕ Quantum Café</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Fireside Chats on Quantum Technologies — A Public Engagement & Capacity-Building Event Series</div>', unsafe_allow_html=True)

st.divider()

# Core Concept
st.subheader("💡 Concept & Objectives")
st.write(
    "Quantum Café is a four-part series of public-facing events designed to demystify "
    "quantum computing and physics for the general public, students, and local innovators. "
    "The series adopts an accessible fireside chat format to bridge cutting-edge research with everyday intuition."
)

st.divider()

# Sessions Grid
st.subheader("📅 Event Series Structure")

col1, col2 = st.columns(2)

with col1:
    with st.expander("Session 1: Demystifying Reality", expanded=True):
        st.write("**Topic:** Superposition and entanglement presented through experiments and accessible explanations.")
        st.code("Notebook: Programmable Quantum Random Number Generator", language="text")

    with st.expander("Session 2: The Hardware Frontier", expanded=True):
        st.write("**Topic:** Building physical quantum platforms in Lithuania and globally.")
        st.code("Notebook: Quantum Teleportation Protocol", language="text")

with col2:
    with st.expander("Session 3: Code, Cryptography & Commerce", expanded=True):
        st.write("**Topic:** Business-oriented dialogue exploring post-quantum security, optimization, and industrial transformation.")
        st.code("Notebook: Superdense Coding Implementation", language="text")

    with st.expander("Session 4: From Theory to Practice", expanded=True):
        st.write("**Topic:** Interactive introductory workshop laying foundational skills for future collaborative problem-solving challenges.")
        st.code("Notebook: Simple Variational Quantum Classifier template", language="text")

st.divider()

# Speakers & Venues
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("👥 Speakers & Stakeholders")
    st.markdown("""
    * **Academic Pioneers:** Quantum physicists and computer scientists from Vilnius University and the Lithuanian Quantum Technologies Association (LKTA).
    * **Industry Leaders:** Executives and engineers from global technology leaders (e.g., IBM, Google) and local high-tech/laser enterprises.
    """)

with right_col:
    st.subheader("📍 Venue Strategy (Vilnius University)")
    st.markdown("""
    * **MKIC (Library Conference Hall):** Large public turnouts & high visibility.
    * **Faculty of Physics (FF):** Hardware sessions near photonics labs.
    * **Faculty of Mathematics and Informatics (MIF):** Algorithmic discussions.
    * **Central VU Building:** Inaugural & business networking panels.
    """)
