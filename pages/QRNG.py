import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum Café - QRNG", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        iframe {
            display: block;
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

def img_to_b64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""

table_desktop_b64 = img_to_b64("./assets/QRNG_table_desktop.jpg")
table_mobile_b64  = img_to_b64("./assets/QRNG_table_mobile.jpg")
front_b64         = img_to_b64("assets/QRNG_0.png")
back_b64          = img_to_b64("assets/QRNG_1.png")
edge_b64          = img_to_b64("assets/QRNG_edge.png")

rng_tavern_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{
    box-sizing: border-box;
  }}

  body {{
    margin: 0;
    padding: 24px 0 16px 0;
    background-color: #0d0704;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f3e5ab;
    text-align: center;
    overflow-x: hidden;
    overflow-y: auto;
  }}

  .coin-3d {{
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.05s linear;
  }}

  .face {{
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    backface-visibility: hidden;
    background-size: cover;
    background-position: center;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.6);
  }}

  .face-front {{
    background-image: url('data:image/png;base64,{front_b64}');
  }}

  .face-back {{
    background-image: url('data:image/png;base64,{back_b64}');
  }}

  .coin-edge-3d {{
    position: absolute;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
  }}

  .edge-facet {{
    position: absolute;
    background-image: url('data:image/png;base64,{edge_b64}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    transform-style: preserve-3d;
  }}

  /* ==========================================================================
     1. DESKTOP MODE ONLY (min-width: 681px)
     ========================================================================== */
  @media (min-width: 681px) {{
    .app-title {{
      font-size: 20px;
      font-style: italic;
      margin: 6px 0 4px 0;
      color: #f3e5ab;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}

    .app-subtitle {{
      font-size: 14px;
      font-style: italic;
      color: #b8975a;
      margin: 0 0 12px 0;
    }}

    .tavern-stage {{
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 15px 35px rgba(0,0,0,0.9);
      background-image: url('data:image/jpeg;base64,{table_desktop_b64}');
      background-size: contain;
      background-repeat: no-repeat;
      background-position: center;
    }}

    .table-overlay {{
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 90%;
      max-width: 760px;
      height: 100%;
    }}

    .coins-grid {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      justify-items: center;
      width: 100%;
    }}

    .coin-card {{
      background: rgba(55, 33, 18, 0.72);
      border: 1px solid #a87944;
      backdrop-filter: blur(6px);
      border-radius: 10px;
      padding: 10px;
      width: 100%;
      max-width: 150px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.6);
    }}

    .card-header {{
      font-size: 14px;
      color: #ffd875;
      font-weight: bold;
    }}

    .coin-slot {{
      --coin-radius: 40px;
      width: 80px;
      height: 80px;
      margin: 8px auto;
      perspective: 600px;
      cursor: ew-resize;
      touch-action: none;
    }}

    .face-front {{ transform: translateZ(4px); }}
    .face-back {{ transform: rotateY(180deg) translateZ(4px); }}

    .edge-facet {{
      height: 8px;
      width: calc(var(--coin-radius) * 0.3978);
      left: calc(50% - (var(--coin-radius) * 0.1989));
      top: calc(50% - 4px);
    }}

    .stats {{
      font-size: 13px;
      margin-top: 4px;
      color: #fce8bd;
      font-weight: bold;
      font-variant-numeric: tabular-nums;
    }}

    .ui-panel {{
      position: absolute;
      bottom: 50px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      width: 100%;
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
      font-size: 15px;
      letter-spacing: 1px;
      color: #00ffcc;
      font-family: monospace;
      background: rgba(0,0,0,0.85);
      padding: 6px 14px;
      border-radius: 6px;
      border: 1px solid #00ffcc44;
    }}
  }}

  /* ==========================================================================
     2. MOBILE MODE ONLY (max-width: 680px)
     ========================================================================== */
  @media (max-width: 680px) {{
    .app-title {{
      font-size: 16px;
      font-style: italic;
      margin: 4px 0 2px 0;
      color: #f3e5ab;
    }}

    .app-subtitle {{
      font-size: 13px;
      font-style: italic;
      color: #b8975a;
      margin: 0 0 14px 0;
      padding: 0 8px;
    }}

    .tavern-stage {{
      position: relative;
      width: 100%;
      aspect-ratio: 9 / 16;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.9);
      background-image: url('data:image/jpeg;base64,{table_mobile_b64}');
      background-size: contain;
      background-repeat: no-repeat;
      background-position: center;
    }}

    .table-overlay {{
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 88%;
      max-width: 280px;
      height: 100%;
    }}

    .coins-grid {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      display: grid;
      grid-template-columns: 1fr;
      gap: 4px;
      justify-items: center;
      width: 100%;
    }}

    .coin-card {{
      background: rgba(40, 22, 10, 0.55);
      border: 1px solid rgba(139, 90, 43, 0.6);
      backdrop-filter: blur(3px);
      border-radius: 6px;
      padding: 3px 8px;
      width: 100%;
      max-width: 260px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 5px rgba(0,0,0,0.4);
    }}

    .card-header {{
      font-size: 12px;
      color: #ffd875;
      font-weight: bold;
      width: 55px;
      flex-shrink: 0;
      text-align: left;
    }}

    .coin-slot {{
      --coin-radius: 24px;
      width: 48px;
      height: 48px;
      margin: 0;
      perspective: 600px;
      cursor: ew-resize;
      touch-action: none;
      flex-shrink: 0;
    }}

    .face-front {{ transform: translateZ(3px); }}
    .face-back {{ transform: rotateY(180deg) translateZ(3px); }}

    .edge-facet {{
      height: 5px;
      width: calc(var(--coin-radius) * 0.3978);
      left: calc(50% - (var(--coin-radius) * 0.1989));
      top: calc(50% - 2.5px);
    }}

    .stats {{
      font-size: 12px;
      margin-top: 0;
      color: #fce8bd;
      font-weight: bold;
      width: 72px;
      flex-shrink: 0;
      text-align: right;
      font-variant-numeric: tabular-nums;
      display: inline-block;
    }}

    .ui-panel {{
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      width: 100%;
    }}

    .measure-btn {{
      background: linear-gradient(to bottom, #d4af37, #8a5a12);
      color: #120a05;
      border: 1px solid #ffe89c;
      padding: 6px 18px;
      font-size: 13px;
      font-weight: bold;
      border-radius: 6px;
      cursor: pointer;
      box-shadow: 0 3px 8px rgba(0,0,0,0.7);
    }}

    .result-box {{
      font-size: 12px;
      letter-spacing: 0.5px;
      color: #00ffcc;
      font-family: monospace;
      background: rgba(0,0,0,0.85);
      padding: 4px 8px;
      border-radius: 4px;
      border: 1px solid #00ffcc44;
    }}
  }}
</style>
</head>
<body>

  <p class="app-title">Drag coins horizontally to alter superposition states, then measure to generate a random byte.</p>

  <div class="tavern-stage">
    <div class="table-overlay">
      <div class="coins-grid" id="tableSurface"></div>
      
      <div class="ui-panel">
        <button class="measure-btn" onclick="measureByte()">⚡ Measure ⚡</button>
        <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
      </div>
    </div>
  </div>

<script>
  const numCoins = 8;
  let coinData = [];
  const table = document.getElementById('tableSurface');
  const numFacets = 16;

  for (let i = 0; i < numCoins; i++) {{
    coinData.push({{ angle: 0 }});

    const card = document.createElement('div');
    card.className = 'coin-card';
    
    let edgeFacetsHTML = '<div class="coin-edge-3d">';
    for (let f = 0; f < numFacets; f++) {{
      let phi = f * (360 / numFacets);
      edgeFacetsHTML += `<div class="edge-facet" style="
        transform: rotateZ(${{phi}}deg) translateY(calc(-1 * var(--coin-radius))) rotateX(90deg);
      "></div>`;
    }}
    edgeFacetsHTML += '</div>';

    card.innerHTML = `
      <div class="card-header">Qubit ${{i}}</div>
      <div class="coin-slot" id="slot_${{i}}">
        <div class="coin-3d" id="coin_${{i}}">
          <div class="face face-front"></div>
          <div class="face face-back"></div>
          ${{edgeFacetsHTML}}
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
    }}, {{ passive: true }});

    window.addEventListener('touchmove', (e) => {{
      if (!isDragging) return;
      let deltaX = e.touches[0].clientX - startX;
      startX = e.touches[0].clientX;

      coinData[index].angle += deltaX * 1.5;
      updateCoinVisual(index);
    }}, {{ passive: true }});

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

components.html(rng_tavern_html, height=1200)
