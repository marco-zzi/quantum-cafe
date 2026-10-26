# Quantum Café: Interactive Apps

Welcome to the open-source repository for the **Quantum Café** interactive visualization suite, developed for Vilnius University (VU) and the Lithuanian Quantum Technologies Association (LKTA).

This repository contains lightweight, interactive web applications built with Python and Streamlit, designed to present quantum concepts during public engagement events and hackathons.
The app hosted on Streamlit can be found at the following address: [https://quantumcafe.streamlit.app/](https://quantumcafe.streamlit.app/).

## Applications Included
1. **Sorcerer's coins**: A duel against a rival sorcerer about entanglement. Eight fair quantum coins race to match a goal pattern of heads and tails; you cannot tilt them, but you can link them into Bell pairs and GHZ states of up to eight coins. Links cost mana, each one can fail, and the rival gets sharper every round. The run ends when you lose a duel, and you keep your score.
2. **Keep the Magic Alive**: A fantasy game about decoherence. Each hardware platform is a craft (superconducting circuit = frostbrewed potion, trapped ion = ritual of bound spirits, neutral atom = star-weaving, photonic = spell of winged light). Manage wards (isolation), chaos (noise) and heat (temperature) with limited mana, and optionally hire a helper (an error-correcting code) that costs mana but can keep the magic steady. A second tab is a sandbox with exact numbers. All platform numbers are illustrative.
3. **The Messenger Wisps**: A fantasy game about quantum key distribution (BB84). The Spell of Winged Light releases wisps; each carries a rune through a Sun or Moon lens. Play solo as Bob (choose lenses, then keep the key or abort) or as Eve (tap wisps without being caught), or host a game: the host screen shows up to three QR codes, one per role (Alice, Bob, Eve), and the roles without a phone are played by bots. Study tab: error correction and privacy amplification on your own key. Round settings are illustrative.
4. **The Gates of Kvantyus**: A fantasy game about quantum machine learning. You guard a city against Nobbubys with a sentinel that is a real variational quantum classifier (one qubit per trait, simulated in the browser). Pick which traits it looks at, spend mana to examine travellers from a fixed 80-card deck, watch it train, then let it judge everyone else at the gate. The city is lost if more than 15% of those who enter are Nobbubys or fewer than 75% of the Kvantyonis are let in. The engine is `assets/gate_engine.js` (pure JS, checked against a numpy reference).

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
