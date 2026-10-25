# Quantum Café: Interactive Apps

Welcome to the open-source repository for the **Quantum Café** interactive visualization suite, developed for Vilnius University (VU) and the Lithuanian Quantum Technologies Association (LKTA).

This repository contains lightweight, interactive web applications built with Python and Streamlit, designed to present quantum concepts during public engagement events and hackathons.
The app hosted on Streamlit can be found at the following address: [https://quantum-cafe.streamlit.app/](https://quantum-cafe.streamlit.app/).

## Applications Included
1. **Sorcerer's coins**: A duel against a rival sorcerer about entanglement. Eight fair quantum coins hide a vault pattern; you cannot tilt them, but you can link them into Bell pairs and GHZ states of up to eight coins. Links cost mana, each one can fail, and the rival gets sharper every round. The run ends when you lose a duel, and you keep your score.
2. **Keep the Magic Alive**: A fantasy game about decoherence. Each hardware platform is a craft (superconducting circuit = frostbrewed potion, trapped ion = ritual of bound spirits, neutral atom = star-weaving, photonic = spell of winged light). Manage wards (isolation), chaos (noise) and heat (temperature) with limited mana, and optionally hire a helper (an error-correcting code) that costs mana but can keep the magic steady. A second tab is a sandbox with exact numbers. All platform numbers are illustrative.
3. **Quantum Key Distribution**: An orbital LEO satellite link demonstrating QKD with a simulated eavesdropper.
4. **Quantum Machine Learning task**: TBD.

## Setup and Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/marco-zzi/quantum-cafe.git
   cd quantum-cafe
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the Streamlit app:
   ```bash
   streamlit run Home.py
