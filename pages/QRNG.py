import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum RNG - Vilnius Quantum Café", layout="wide")

st.title("🎲 Programmable Quantum RNG")
st.markdown("*Quantum Café Session 1: Rotate the 3D coins on the tavern table to set superposition probabilities ($\theta$), then measure to generate a random byte.*")

rng_tavern_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    margin: 0;
    padding: 0;
    background-color: #0d0704;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f3e5ab;
    text-align: center;
    overflow-x: hidden;
  }
  
  /* 2.5D Tavern Canvas Container */
  .tavern-stage {
    position: relative;
    width: 950px;
    height: 520px;
    margin: 0 auto;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0,0,0,0.9);
    background: #110905;
  }

  /* Embedded 2.5D Isometric SVG Tavern Illustration */
  .tavern-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }

  /* Interactive Table Overlay Grid */
  .table-overlay {
    position: absolute;
    top: 140px;
    left: 75px;
    width: 800px;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    justify-items: center;
  }

  .coin-card {
    background: rgba(20, 10, 5, 0.65);
    border: 1px solid #7a4f26;
    backdrop-filter: blur(4px);
    border-radius: 10px;
    padding: 8px;
    width: 150px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.7);
  }

  .coin-slot {
    width: 75px;
    height: 75px;
    margin: 10px auto;
    perspective: 600px;
    cursor: ew-resize;
  }
  
  /* 3D Coin Construction */
  .coin-3d {
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.05s linear;
  }
  .face {
    position: absolute;
    width: 75px;
    height: 75px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 20px;
    backface-visibility: hidden;
    border: 3px solid #d4af37;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
  }
  .face-front {
    background: radial-gradient(circle, #f3e5ab 0%, #d4af37 70%, #8a5a12 100%);
    color: #1a0f08;
    transform: translateZ(5px);
  }
  .face-back {
    background: radial-gradient(circle, #cd7f32 0%, #a0522d 70%, #4a210d 100%);
    color: #f3e5ab;
    transform: rotateY(180deg) translateZ(5px);
  }

  .stats {
    font-size: 11px;
    margin-top: 4px;
    color: #d4af37;
    font-weight: bold;
  }

  .ui-panel {
    position: absolute;
    bottom: 15px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 3;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .measure-btn {
    background: linear-gradient(to bottom, #d4af37, #8a5a12);
    color: #120a05;
    border: 1px solid #ffe89c;
    padding: 10px 28px;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0,0,0,0.6);
    transition: all 0.2s;
  }
  .measure-btn:hover {
    background: linear-gradient(to bottom, #f3e5ab, #d4af37);
    transform: scale(1.04);
  }

  .result-box {
    font-size: 18px;
    letter-spacing: 2px;
    color: #00ffcc;
    font-family: monospace;
    background: rgba(0,0,0,0.8);
    padding: 6px 16px;
    border-radius: 6px;
    border: 1px solid #00ffcc44;
  }
</style>
</head>
<body>

<div class="tavern-stage">
  <!-- 2.5D Isometric Tavern Background Vector -->
  <svg class="tavern-bg" viewBox="0 0 950 520" preserveAspectRatio="none">
    <defs>
      <!-- Warm Ambient Lighting -->
      <radialGradient id="lanternGlow" cx="20%" cy="20%" r="60%">
        <stop offset="0%" stop-color="#ffaa33" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#0d0704" stop-opacity="0"/>
      </radialGradient>
      <!-- Wood Plank Pattern -->
      <linearGradient id="woodTexture" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#3a2012"/>
        <stop offset="50%" stop-color="#26140a"/>
        <stop offset="100%" stop-color="#190d06"/>
      </linearGradient>
      <linearGradient id="tableTop" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#54331a"/>
        <stop offset="100%" stop-color="#2d1a0d"/>
      </linearGradient>
    </defs>

    <!-- Tavern Floor Planks -->
    <rect width="950" height="520" fill="url(#woodTexture)"/>
    <path d="M 0 100 L 950 100 M 0 200 L 950 200 M 0 300 L 950 300 M 0 400 L 950 400" stroke="#120904" stroke-width="3"/>
    
    <!-- 2.5D Isometric Table Base & Surface -->
    <polygon points="50,110 900,110 850,420 100,420" fill="#1f1108" stroke="#0a0502" stroke-width="4"/>
    <polygon points="60,115 890,115 843,410 107,410" fill="url(#tableTop)" stroke="#7a4f26" stroke-width="3"/>
    
    <!-- Carved Table Details / Inlays -->
    <polygon points="80,130 870,130 830,395 120,395" fill="none" stroke="#3d2312" stroke-width="2" stroke-dasharray="8,4"/>
    
    <!-- Decorative Lanterns in Corners -->
    <circle cx="80" cy="70" r="100" fill="url(#lanternGlow)"/>
    <circle cx="870" cy="70" r="100" fill="url(#lanternGlow)"/>
    <circle cx="80" cy="70" r="8" fill="#ffcc44"/>
    <circle cx="870" cy="70" r="8" fill="#ffcc44"/>
  </svg>

  <!-- Interactive 8 Qubit Overlay -->
  <div class="table-overlay" id="tableSurface"></div>

  <!-- Bottom Action Panel -->
  <div class="ui-panel">
    <button class="measure-btn" onclick="measureByte()">⚡ Measure Quantum Byte</button>
    <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
  </div>
</div>

<script>
  const numCoins = 8;
  let coinData = [];
  const table = document.getElementById('tableSurface');

  for (let i = 0; i < numCoins; i++) {
    coinData.push({ angle: 0 });

    const card = document.createElement('div');
    card.className = 'coin-card';
    card.innerHTML = `
      <div style="font-size: 11px; color: #b8975a;">Qubit ${i}</div>
      <div class="coin-slot" id="slot_${i}">
        <div class="coin-3d" id="coin_${i}">
          <div class="face face-front">0</div>
          <div class="face face-back">1</div>
        </div>
      </div>
      <div class="stats" id="stat_${i}">P(1): 0%</div>
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

      coinData[index].angle += deltaX * 1.5;
      updateCoinVisual(index);
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    // Touch support for mobile devices
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

    coin.style.transform = `rotateY(${angle}deg)`;

    let normalizedAngle = (angle % 360 + 360) % 360;
    let prob1 = Math.sin((normalizedAngle * Math.PI) / 360) ** 2;
    stat.innerText = `P(1): ${Math.round(prob1 * 100)}%`;
  }

  function measureByte() {
    let binaryString = "";
    for (let i = 0; i < numCoins; i++) {
      let angle = coinData[i].angle;
      let normalizedAngle = (angle % 360 + 360) % 360;
      let prob1 = Math.sin((normalizedAngle * Math.PI) / 360) ** 2;
      
      let outcome = Math.random() < prob1 ? "1" : "0";
      binaryString += outcome;

      let coin = document.getElementById(`coin_${i}`);
      coin.style.transition = "transform 0.3s ease";
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

components.html(rng_tavern_html, height=550)
