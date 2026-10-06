import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum RNG - Vilnius Quantum Café", layout="wide")

st.title("🎲 Programmable Quantum RNG")
st.markdown("*Quantum Café Session 1: Rotate the 3D tavern coins along their vertical axis to change superposition probabilities, then measure to generate a random byte.*")

rng_tavern_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    margin: 0;
    padding: 0;
    background-color: #1a0f08;
    background-image: radial-gradient(circle at 50% 30%, #3d2314 0%, #120a05 80%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f3e5ab;
    text-align: center;
  }
  .tavern-container {
    perspective: 1000px;
    padding: 10px;
    max-width: 950px;
    margin: 0 auto;
  }
  .table-surface {
    background: linear-gradient(135deg, #2c1810, #1b0e08);
    border: 6px solid #4a2e18;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.8), inset 0 0 30px rgba(0,0,0,0.6);
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    justify-items: center;
  }
  .coin-card {
    background: rgba(0, 0, 0, 0.3);
    border: 2px solid #6b4423;
    border-radius: 10px;
    padding: 8px;
    width: 140px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
  }
  .coin-slot {
    width: 80px;
    height: 80px;
    margin: 15px auto;
    perspective: 800px;
    cursor: ew-resize;
  }
  
  /* True 3D CSS Coin Construction */
  .coin-3d {
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.05s linear;
  }
  .face {
    position: absolute;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 22px;
    backface-visibility: hidden;
    border: 3px solid #d4af37;
  }
  .face-front {
    background: radial-gradient(circle, #f3e5ab 0%, #d4af37 70%, #996515 100%);
    color: #1a0f08;
    transform: translateZ(6px);
  }
  .face-back {
    background: radial-gradient(circle, #cd7f32 0%, #a0522d 70%, #5c2c16 100%);
    color: #f3e5ab;
    transform: rotateY(180deg) translateZ(6px);
  }
  /* 3D Edge / Thickness with dented/ribbed illusion */
  .coin-edge {
    position: absolute;
    width: 80px;
    height: 12px;
    top: 34px;
    left: 0;
    background: repeating-linear-gradient(
      90deg,
      #8b6508,
      #8b6508 3px,
      #4a3504 3px,
      #4a3504 6px
    );
    transform-style: preserve-3d;
  }

  .stats {
    font-size: 11px;
    margin-top: 8px;
    color: #d4af37;
  }
  .measure-btn {
    margin-top: 20px;
    background: linear-gradient(to bottom, #d4af37, #996515);
    color: #1a0f08;
    border: none;
    px: 25px; padding: 10px 25px;
    font-size: 16px;
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
    margin-top: 10px;
    font-size: 20px;
    letter-spacing: 2px;
    color: #00ffcc;
    font-family: monospace;
  }
</style>
</head>
<body>

<div class="tavern-container">
  <h3>Interactive Tavern Table (8 Qubits / 1 Byte)</h3>
  <p style="font-size: 12px; color: #b8975a; margin-top: -5px;">Drag horizontally across each coin to rotate it along its vertical axis</p>
  
  <div class="table-surface" id="tableSurface"></div>

  <button class="measure-btn" onclick="measureByte()">⚡ Measure Quantum Byte</button>
  <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
</div>

<script>
  const numCoins = 8;
  let coinData = [];
  const table = document.getElementById('tableSurface');

  for (let i = 0; i < numCoins; i++) {
    coinData.push({ angle: 0 }); // 0 degrees rotation

    const card = document.createElement('div');
    card.className = 'coin-card';
    card.innerHTML = `
      <div style="font-size: 12px;">Qubit ${i}</div>
      <div class="coin-slot" id="slot_${i}">
        <div class="coin-3d" id="coin_${i}">
          <div class="face face-front">0</div>
          <div class="face face-back">1</div>
          <div class="coin-edge" id="edge_${i}"></div>
        </div>
      </div>
      <div class="stats" id="stat_${i}">P(1): 50%</div>
    `;
    table.appendChild(card);
    setupInteraction(i);
  }

  function setupInteraction(index) {
    const slot = document.getElementById(`slot_${index}`);
    let isDragging = false;
    let startX = 0;

    slot.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.clientX;
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      let deltaX = e.clientX - startX;
      startX = e.clientX;

      coinData[index].angle += deltaX * 1.5; // Rotate along Y axis
      updateCoinVisual(index);
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    // Touch support
    slot.addEventListener('touchstart', (e) => {
      isDragging = true;
      startX = e.touches[0].clientX;
    });
    window.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      let deltaX = e.touches[0].clientX - startX;
      startX = e.touches[0].clientX;

      coinData[index].angle += deltaX * 1.5;
      updateCoinVisual(index);
    });
    window.addEventListener('touchend', () => { isDragging = false; });
  }

  function updateCoinVisual(index) {
    let angle = coinData[index].angle;
    let coin = document.getElementById(`coin_${index}`);
    let stat = document.getElementById(`stat_${index}`);

    // Restrict rotation strictly to Y axis
    coin.style.transform = `rotateY(${angle}deg)`;

    // Calculate probability based on normalized angle cycle (0 to 360 deg maps to quantum phase/probability)
    let normalizedAngle = (angle % 360 + 360) % 360;
    let rad = (normalizedAngle * Math.PI) / 180;
    let prob1 = Math.sin(rad / 2) ** 2;
    stat.innerText = `P(1): ${Math.round(prob1 * 100)}%`;
  }

  function measureByte() {
    let binaryString = "";
    for (let i = 0; i < numCoins; i++) {
      let angle = coinData[i].angle;
      let normalizedAngle = (angle % 360 + 360) % 360;
      let prob1 = Math.sin((normalizedAngle * Math.PI) / 180) ** 2;
      
      let outcome = Math.random() < prob1 ? "1" : "0";
      binaryString += outcome;

      // Snap visual to nearest definitive state (0 deg or 180 deg) on collapse
      let coin = document.getElementById(`coin_${i}`);
      coin.style.transition = "transform 0.4s ease";
      let targetAngle = outcome === "1" ? 180 : 0;
      coinData[i].angle = targetAngle;
      coin.style.transform = `rotateY(${targetAngle}deg)`;
      document.getElementById(`stat_${i}`).innerText = `P(1): ${outcome === "1" ? "100%" : "0%"}`;
    }

    let decimalVal = parseInt(binaryString, 2);
    let hexVal = decimalVal.toString(16).toUpperCase().padStart(2, '0');
    document.getElementById('byteResult').innerHTML = `Byte: ${binaryString} (0x${hexVal} | ${decimalVal})`;
  }
</script>

</body>
</html>
"""

components.html(rng_tavern_html, height=480)
