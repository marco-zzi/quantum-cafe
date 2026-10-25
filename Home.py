import streamlit as st

from qc_theme import apply_theme

st.set_page_config(
    page_title="Quantum Café",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

# Hero
st.markdown('<div class="qc-eyebrow">A public engagement and capacity-building event series</div>', unsafe_allow_html=True)
st.markdown('<h1 class="qc-serif">Quantum Café</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="qc-lede">Fireside chats on quantum technologies. Four public events that demystify quantum '
    'computing and physics for the general public, students and local innovators, from February to May 2027.</p>',
    unsafe_allow_html=True,
)
st.write("")


def card(eyebrow, title, text, chip, href=None):
    chip_html = f'<span class="qc-chip{"" if href else " off"}">{chip}</span>'
    inner = (f'<div class="qc-eyebrow" style="margin:0">{eyebrow}</div><div class="t">{title}</div>'
             f'<div class="d">{text}</div><div class="spacer"></div>{chip_html}')
    if href:
        return f'<a class="qc-card" href="{href}" target="_self">{inner}</a>'
    return f'<div class="qc-card">{inner}</div>'


# The series, with the interactive app that closes each session
st.markdown('<div class="qc-eyebrow">The series</div>', unsafe_allow_html=True)
st.subheader("Four sessions, four things to try")
cards = "".join([
    card("Session 1 · 18 February 2027", "Demystifying Reality",
         "Quantum theories and phenomena presented through experiments and accessible explanations.",
         "Play: Sorcerer's coins", "Sorcerers_Coins"),
    card("Session 2 · 18 March 2027", "The Hardware Frontier",
         "Building physical quantum platforms in Lithuania and globally.",
         "Play: Keep the Magic Alive", "Keep_the_Magic_Alive"),
    card("Session 3 · 14 April 2027", "Cryptography, Cybersecurity &amp; Business",
         "A business-oriented dialogue exploring post-quantum security, quantum networks and industrial transformation.",
         "Coming: quantum key distribution"),
    card("Session 4 · 13 May 2027", "From Theory to Practice",
         "An interactive introductory workshop laying the foundational skills for future collaborative problem-solving challenges.",
         "Coming: quantum machine learning"),
])
st.markdown(f'<div class="qc-grid">{cards}</div>', unsafe_allow_html=True)
st.caption("Each session closes with a hands-on app, and the same ideas continue in take-home notebooks. "
           "A quantum hackathon on 21-22 May 2027 ends the series.")

st.write("")

# Speakers and venues
left, right = st.columns(2, gap="large")
with left:
    st.markdown('<div class="qc-eyebrow">Who joins the conversation</div>', unsafe_allow_html=True)
    st.subheader("Speakers and stakeholders")
    st.markdown(
        "**Academic pioneers.** Quantum physicists and computer scientists from Vilnius University and the "
        "Lithuanian Quantum Technologies Association (LKTA).\n\n"
        "**Industry leaders.** Executives and engineers from global technology leaders and local high-tech "
        "and laser enterprises."
    )
with right:
    st.markdown('<div class="qc-eyebrow">Where it happens</div>', unsafe_allow_html=True)
    st.subheader("Venues at Vilnius University")
    st.markdown(
        "**MKIC, Library Conference Hall.** Large public turnouts and high visibility.\n\n"
        "**Faculty of Physics.** Hardware sessions near the photonics labs.\n\n"
        "**Faculty of Mathematics and Informatics.** Algorithmic discussions.\n\n"
        "**Central VU Building.** Inaugural and business networking panels."
    )
