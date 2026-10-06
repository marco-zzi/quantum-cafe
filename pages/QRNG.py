import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum RNG - Vilnius Quantum Café", layout="wide")

def img_to_b64(file_path):
    """Converts a local image file to a Base64 string for HTML embedding."""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""

# Load cropped image assets
table_b64 = img_to_b64("./assets/QRNG_table.jpg")
front_b64 = img_to_b64("assets/QRNG_0.png")
back_b64 = img_to_b64("assets/QRNG_1.png")
edge_b64 = img_to_b64("assets/QRNG_edge.png")

st.title("🎲 Programmable Quantum RNG")
st.markdown("*Quantum Café Session 1: Drag coins horizontally to alter superposition states ($\theta$), then measure to generate a random byte.*")

rng_tavern_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    padding: 0;
    background-color: #0d0704;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f3e5ab;
    text-align: center;
    overflow-x: hidden;
  }}
  
  /* 2.5D Table Stage with Custom Background */
  .tavern-stage {{
    position: relative;
    width: 900px;
    height: 600px;
    margin: 0 auto;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0,0,0,0.9);
    background-image: url('data:image/jpeg;base64,{table_b64}');
    background-size: cover;
    background-position: center;
  }}

  /* Grid overlay aligned to central wooden board */
  .table-overlay {{
    position: absolute;
    top: 100px;
    left: 100px;
    width: 700px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    justify-items: center;
  }}

  .coin-card {{
    background: rgba(15, 8, 4, 0.7);
    border: 1px solid #8b5a2b;
    backdrop-filter: blur(4px);
    border-radius: 10px;
    padding: 8px;
    width: 135px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.8);
  }}

  .coin-slot {{
    width: 80px;
    height: 80px;
    margin: 10px auto;
    perspective: 600px;
    cursor: ew-resize;
  }}
  
  /* 3D Coin with Image Textures */
  .coin-3d {{
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.05s linear;
  }}

  .face {{
    position: absolute;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    backface-visibility: hidden;
    background-size: cover;
    background-position: center;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.6);
  }}

  .face-front {{
    background-image: url('data:image/jpeg;base64,{front_b64}');
    transform: translateZ(5px);
  }}

  .face-back {{
    background-image: url('data:image/jpeg;base64,{back_b64}');
    transform: rotateY(180deg) translateZ(5px);
  }}

  /* Ribbed Edge Texture Cylinder */
  .coin-edge {{
    position: absolute;
    width: 80px;
    height: 10px;
    top: 35px;
    left: 0;
    background-image: url('data:image/jpeg;base64,{edge_b64}');
    background-size: auto 100%;
    transform-style: preserve-3d;
  }}

  .stats {{
    font-size: 11px;
    margin-top: 4px;
    color: #e6c687;
    font-weight: bold;
  }}

  .ui-panel {{
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }}

  .measure-btn {{
    background: linear-gradient(to bottom, #d4af37, #8a5a12);
    color: #120a05;
    border: 1px solid #ffe89c;
    padding: 10px 28px;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0,0,0,0.7);
    transition: all 0.2s;
  }}

  .measure-btn:hover {{
    background: linear-gradient(to bottom, #f3e5ab, #d4af37);
    transform: scale(1.04);
  }}

  .result-box {{
    font-size: 18px;
    letter-spacing: 2px;
    color: #00ffcc;
    font-family: monospace;
    background: rgba(0,0,0,0.85);
    padding: 6px 16px;
    border-radius: 6px;
    border: 1px solid #00ffcc44;
  }}
</style>
</head>
<body>

<div class="tavern-stage">
  <div class="table-overlay" id="tableSurface"></div>

  <div class="ui-panel">
    <button class="measure-btn" onclick="measureByte()">⚡ Measure Quantum Byte</button>
    <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
  </div>
</div>

<script>
  const numCoins = 8;
  let coinData = [];
  const table = document.getElementById('tableSurface');

  for (let i = 0; i < numCoins; i++) {{
    coinData.push({{ angle: 0 }});

    const card = document.createElement('div');
    card.className = 'coin-card';
    card.innerHTML = `
      <div style="font-size: 11px; color: #d4af37;">Qubit ${{i}}</div>
      <div class="coin-slot" id="slot_${{i}}">
        <div class="coin-3d" id="coin_${{i}}">
          <div class="face face-front"></div>
          <div class="face face-back"></div>
          <div class="coin-edge"></div>
        </div>
      </div>
      <div class="stats" id="stat_${{i}}">P(1): 0%</div>
    `;
    table.appendChild(card);
    setupInteraction(i);
  }}

  function setupInteraction(index) {{
    const slot = document.getElementById(`slot_${{index}}`);
    let isDragging = false;
    let startX = 0;

    slot.addEventListener('mousedown', (e) => {{
      isDragging = true;
      startX = e.clientX;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      let deltaX = e.clientX - startX;
      startX = e.clientX;

      coinData[index].angle += deltaX * 1.5;
      updateCoinVisual(index);
    }});

    window.addEventListener('mouseup', () => {{ isDragging = false; }});

    slot.addEventListener('touchstart', (e) => {{
      isDragging = true;
      startX = e.touches[0].clientX;
    }});
    window.addEventListener('touchmove', (e) => {{
      if (!isDragging) return;
      let deltaX = e.touches[0].clientX - startX;
      startX = e.touches[0].clientX;

      coinData[index].angle += deltaX * 1.5;
      updateCoinVisual(index);
    }});
    window.addEventListener('touchend', () => {{ isDragging = false; }});
  }}

  function updateCoinVisual(index) {{
    let angle = coinData[index].angle;
    let coin = document.getElementById(`coin_${{index}}`);
    let stat = document.getElementById(`stat_${{index}}`);

    coin.style.transform = `rotateY(${{angle}}deg)`;

    let normalizedAngle = (angle % 360 + 360) % 360;
    let prob1 = Math.sin((normalizedAngle * Math.PI) / 360) ** 2;
    stat.innerText = `P(1): ${{Math.round(prob1 * 100)}}%`;
  }}

  function measureByte() {{
    let binaryString = "";
    for (let i = 0; i < numCoins; i++) {{
      let angle = coinData[i].angle;
      let normalizedAngle = (angle % 360 + 360) % 360;
      let prob1 = Math.sin((normalizedAngle * Math.PI) / 360) ** 2;
      
      let outcome = Math.random() < prob1 ? "1" : "0";
      binaryString += outcome;

      let coin = document.getElementById(`coin_${{i}}`);
      coin.style.transition = "transform 0.3s ease";
      let targetAngle = outcome === "1" ? 180 : 0;
      coinData[i].angle = targetAngle;
      coin.style.transform = `rotateY(${{targetAngle}}deg)`;
      document.getElementById(`stat_${{i}}`).innerText = `P(1): ${{outcome === "1" ? "100%" : "0%"}}`;
    }}

    let decimalVal = parseInt(binaryString, 2);
    let hexVal = decimalVal.toString(16).toUpperCase().padStart(2, '0');
    document.getElementById('byteResult').innerHTML = `Byte: ${{binaryString}} (0x${{hexVal}} | ${{decimalVal}})`;
  }}
</script>

</body>
</html>
"""

components.html(rng_tavern_html, height=620)
