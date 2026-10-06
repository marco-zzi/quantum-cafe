import streamlit as st

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Shared Session State Initialization
# Define default state keys here so secondary pages can safely read them on load.
if "shared_data" not in st.session_state:
    st.session_state["shared_data"] = {}

if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False

# 3. Main Landing Page UI
st.title("Main Application")
st.markdown("Welcome! Use the sidebar navigation on the left to switch pages.")

st.divider()

# Example section / Dashboard summary
col1, col2 = st.columns(2)
with col1:
    st.subheader("Quick Start")
    st.write("Select a module from the sidebar to begin.")

with col2:
    st.subheader("System Status")
    st.success("App online")
