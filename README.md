# Quantum Café: Interactive Apps

Welcome to the open-source repository for the **Quantum Café** interactive visualization suite, developed for Vilnius University (VU) and the Lithuanian Quantum Technologies Association (LKTA).

This repository contains lightweight, interactive web applications built with Python and Streamlit, designed to present quantum concepts during public engagement events and hackathons.
The app hosted on Streamlit can be found at the following address: [https://quantum-cafe.streamlit.app/](https://quantum-cafe.streamlit.app/).

## Applications Included
1. **Programmable Quantum RNG**: An interactive tavern-themed table where users rotate 8 independent quantum coins to generate a random byte.
2. **Quantum Teleportation**: A visualization (theme TBD) tracking entanglement distribution across two locations.
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
   streamlit run app_name.py
