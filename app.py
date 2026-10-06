import streamlit as st
import streamlit.components.v1 as components

st.title("Vilnius Quantum Café: Interactive Visualizations")
st.subheader("1. Programmable Quantum RNG (Isometric View)")

# Embedded HTML/CSS/JS 2.5D Component
rng_isometric_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { background-color: #0f172a; color: white; font-family: sans-serif; text-align: center; }
  .isometric-container {
    perspective: 800px;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 250px;
  }
  .coin {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #38bdf8, #2563eb);
    border-radius: 50%;
    transform-style: preserve-3d;
    transition: transform 1s ease-in-out;
    box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    margin: 0 auto;
  }
  .controls { margin-top: 15px; }
  input[type=range] { width: 60%; }
</style>
</head>
<body>

  <div class="isometric-container">
    <div class="coin" id="quantumCoin">V</div>
  </div>

  <div class="controls">
    <label>Superposition Tilt ($\theta$): <span id="val">0.5</span></label><br>
    <input type="range" id="tiltSlider" min="0" max="1" step="0.05" value="0.5" oninput="updateTilt(this.value)">
  </div>

  <script>
    function updateTilt(val) {
      document.getElementById('val').innerText = val;
      let rotateDeg = val * 360;
      document.getElementById('quantumCoin').style.transform = `rotateX(${rotateDeg}deg) rotateY(${rotateDeg}deg)`;
    }
  </script>

</body>
</html>
"""

# Render the 2.5D component inside Streamlit with fixed dimensions
components.html(rng_isometric_html, height=350)
