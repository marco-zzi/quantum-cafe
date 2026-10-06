import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum RNG - Vilnius Quantum Café", layout="wide")

st.title("🎲 Programmable Quantum RNG")
st.markdown("*Quantum Café Session 1: Adjust the 8 quantum coins directly on the tavern table to alter their superposition states, then measure to generate a true random byte.*")

rng_tavern_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    margin: 0;
    padding: 0;
    background-color: #1a0f08;
    /* Cozy fantasy tavern ambient lighting */
    background-image: radial-gradient(circle at 50% 30%, #3d2314 0%, #120a05 80%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f3e5ab;
    text-align: center;
  }
  .tavern-container {
    perspective: 1000px;
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
  }
  .table-surface {
    background: linear-gradient(135deg, #2c1810, #1b0e08);
    border: 6px solid #4a2e18;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.8), inset 0 0 30px rgba(0,0,0,0.6);
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    justify-items: center;
  }
  .coin-card {
    background: rgba(0, 0, 0, 0.3);
    border: 2px solid #6b4423;
    border-radius: 10px;
    padding: 10px;
    width: 150px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
  }
  .coin-slot {
    width: 90px;
    height: 90px;
    margin: 10px auto;
    perspective: 800px;
    cursor: grab;
  }
  .coin {
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.1s ease-out;
    border-radius: 50%;
    box-shadow: 0 5px 15px rgba(0,0,0,0.6);
  }
  .coin-face {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 20px;
    border: 3px solid #d4af37;
  }
  .coin-front {
    background: radial-gradient(circle, #e6c687 0%, #b8860b 100%);
    color: #2c1810;
  }
  .coin-back {
    background: radial-gradient(circle, #cd7f32 0%, #8b4513 100%);
    color: #f3e5ab;
    transform: rotateY(180deg);
  }
  .stats {
    font-size: 12px;
    margin-top: 5px;
    color: #d4af37;
  }
  .measure-btn {
    margin-top: 25px;
    background: linear-gradient(to bottom, #d4af37, #996515);
    color: #1a0f08;
    border: none;
    padding: 12px 30px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0,0,0,0.4);
    transition: all 0.2s;
  }
  .measure-btn:hover {
    background: linear-gradient(to bottom, #f3e5ab, #d4af37);
    transform: scale(1.05);
  }
  .result-box {
    margin-top: 15px;
    font-size: 24px;
    letter-spacing: 3px;
    color: #00ffcc;
    font-family: monospace;
  }
</style>
</head>
<body>

<div class="tavern-container">
  <h3>Interactive Tavern Table (8 Qubits / 1 Byte)</h3>
  <p style="font-size: 13px; color: #b8975a; margin-top: -5px;">Drag or scroll vertically over each coin to tilt its probability axis ($\theta$)</p>
  
  <div class="table-surface" id="tableSurface">
    <!-- Generated dynamically via JS for 8 coins -->
  </div>

  <button class="measure-btn" onclick="measureByte()">⚡ Measure Quantum Byte</button>
  <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
</div>

<script>
  const numCoins = 8;
  let coinData = [];

  const table = document.getElementById('tableSurface');

  for (let i = 0; i < numCoins; i++) {
    coinData.push({ theta: 0.5 }); // default equal superposition

    const card = document.createElement('div');
    card.className = 'coin-card';
    card.innerHTML = `
      <div>Qubit ${i}</div>
      <div class="coin-slot" id="slot_${i}">
        <div class="coin" id="coin_${i}">
          <div class="coin-face coin-front">0</div>
          <div class="coin-face coin-back">1</div>
        </div>
      </div>
      <div class="stats" id="stat_${i}">P(1): 50%</div>
    `;
    table.appendChild(card);

    setupInteraction(i);
  }

  function setupInteraction(index) {
    const slot = document.getElementById(`slot_${index}`);
    const coin = document.getElementById(`coin_${index}`);
    const stat = document.getElementById(`stat_${index}`);

    let isDragging = false;
    let startY = 0;

    slot.addEventListener('mousedown', (e) => {
      isDragging = true;
      startY = e.clientY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      let deltaY = startY - e.clientY;
      startY = e.clientY;

      let currentTheta = coinData[index].theta + deltaY * 0.01;
      currentTheta = Math.max(0, Math.min(1, currentTheta)); // clamp between 0 and 1
      coinData[index].theta = currentTheta;

      updateCoinVisual(index);
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    // Touch support for mobile devices in the café
    slot.addEventListener('touchstart', (e) => {
      isDragging = true;
      startY = e.touches[0].clientY;
    });
    window.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      let deltaY = startY - e.touches[0].clientY;
      startY = e.touches[0].clientY;

      let currentTheta = coinData[index].theta + deltaY * 0.01;
      currentTheta = Math.max(0, Math.min(1, currentTheta));
      coinData[index].theta = currentTheta;

      updateCoinVisual(index);
    });
    window.addEventListener('touchend', () => { isDragging = false; });
  }

  function updateCoinVisual(index) {
    let theta = coinData[index].theta;
    let coin = document.getElementById(`coin_${index}`);
    let stat = document.getElementById(`stat_${index}`);

    // Map theta (0 to 1) to rotation angles
    let rotateX = theta * 180;
    let rotateY = theta * 360;
    coin.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

    // Calculate quantum probability of measuring state '1' -> sin^2(theta * pi / 2)
    let prob1 = Math.sin((theta * Math.PI) / 2) ** 2;
    stat.innerText = `P(1): ${Math.round(prob1 * 100)}%`;
  }

  function measureByte() {
    let binaryString = "";
    for (let i = 0; i < numCoins; i++) {
      let theta = coinData[i].theta;
      let prob1 = Math.sin((theta * Math.PI) / 2) ** 2;
      let outcome = Math.random() < prob1 ? "1" : "0";
      binaryString += outcome;

      // Quick visual collapse effect
      let coin = document.getElementById(`coin_${i}`);
      coin.style.transition = "transform 0.3s ease";
      if (outcome === "1") {
        coin.style.transform = "rotateX(180deg) rotateY(360deg)";
      } else {
        coin.style.transform = "rotateX(0deg) rotateY(0deg)";
      }
    }

    // Convert binary byte to Hex and Decimal for flavor
    let decimalVal = parseInt(binaryString, 2);
    let hexVal = decimalVal.toString(16).toUpperCase().padStart(2, '0');
    
    document.getElementById('byteResult').innerHTML = `Byte: ${binaryString} (0x${hexVal} | ${decimalVal})`
  }
</script>

</body>
</html>
"""

components.html(rng_tavern_html, height=520)
