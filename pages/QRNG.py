import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum Café - QRNG", layout="wide")

# Reduce Streamlit default padding
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
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
    padding: 0;
    background-color: #0d0704;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f3e5ab;
    text-align: center;
    overflow-x: hidden;
  }}

  .app-title {{
    font-size: 22px;
    margin: 4px 0 6px 0;
    color: #f3e5ab;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
  }}

  .app-subtitle {{
    font-size: 12px;
    font-style: italic;
    color: #b8975a;
    margin: 6px 0 0 0;
  }}
  
  /* 2.5D Table Stage - Fluid width scaling for desktop */
  .tavern-stage {{
    position: relative;
    width: 100%;
    max-width: 900px;
    aspect-ratio: 860 / 500;
    margin: 0 auto;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0,0,0,0.9);
    background-image: url('data:image/jpeg;base64,{table_b64}');
    background-size: cover;
    background-position: center;
  }}

  .table-overlay {{
    position: absolute;
    top: 13%;
    left: 9%;
    width: 82%;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    justify-items: center;
  }}

  .coin-card {{
    background: rgba(15, 8, 4, 0.75);
    border: 1px solid #8b5a2b;
    backdrop-filter: blur(4px);
    border-radius: 10px;
    padding: 6px;
    width: 100%;
    max-width: 125px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.8);
  }}

  .coin-slot {{
    width: 68px;
    height: 68px;
    margin: 4px auto;
    perspective: 600px;
    cursor: ew-resize;
    touch-action: none;
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
    width: 68px;
    height: 68px;
    border-radius: 50%;
    backface-visibility: hidden;
    background-size: cover;
    background-position: center;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.6);
  }}

  .face-front {{
    background-image: url('data:image/png;base64,{front_b64}');
    transform: translateZ(5px);
  }}

  .face-back {{
    background-image: url('data:image/png;base64,{back_b64}');
    transform: rotateY(180deg) translateZ(5px);
  }}

  .coin-edge-3d {{
    position: absolute;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
  }}

  .edge-facet {{
    position: absolute;
    height: 10px;
    background-image: url('data:image/png;base64,{edge_b64}');
    background-repeat: no-repeat;
    transform-style: preserve-3d;
  }}

  .stats {{
    font-size: 11px;
    margin-top: 2px;
    color: #e6c687;
    font-weight: bold;
  }}

  .ui-panel {{
    position: absolute;
    bottom: 3%;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: 90%;
  }}

  .measure-btn {{
    background: linear-gradient(to bottom, #d4af37, #8a5a12);
    color: #120a05;
    border: 1px solid #ffe89c;
    padding: 8px 24px;
    font-size: 15px;
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
    padding: 4px 12px;
    border-radius: 6px;
    border: 1px solid #00ffcc44;
  }}

  /* Mobile Adaptation Rules */
  @media (max-width: 680px) {{
    .app-title {{
      display: none; /* Hide title on mobile */
    }}
    .tavern-stage {{
      aspect-ratio: auto;
      height: 510px; /* Fixed height accommodating 4 rows + UI panel */
      width: 100%;
    }}
    .table-overlay {{
      top: 15px;
      left: 5%;
      width: 90%;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
    }}
    .coin-card {{
      max-width: 110px;
      padding: 3px;
    }}
    .coin-slot, .face {{
      width: 52px;
      height: 52px;
    }}
    .ui-panel {{
      bottom: 10px;
    }}
    .measure-btn {{
      padding: 6px 18px;
      font-size: 13px;
    }}
    .result-box {{
      font-size: 12px;
      padding: 3px 8px;
    }}
    .app-subtitle {{
      font-size: 11px;
      margin-top: 4px;
    }}
  }}
</style>
</head>
<body>

  <h1 class="app-title">🎲 Quantum Random Number Generator</h1>

  <div class="tavern-stage">
    <div class="table-overlay" id="tableSurface"></div>

    <div class="ui-panel">
      <button class="measure-btn" onclick="measureByte()">⚡ Measure</button>
      <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
    </div>
  </div>

  <p class="app-subtitle">Drag coins horizontally to alter superposition states (&theta;), then measure to generate a random byte.</p>

<script>
  const numCoins = 8;
  let coinData = [];
  const table = document.getElementById('tableSurface');

  const numFacets = 16;
  const radius = 33.5;
  const facetWidth = (2 * radius * Math.tan(Math.PI / numFacets)).toFixed(2);
  const facetLeft = (34 - facetWidth / 2).toFixed(2);

  for (let i = 0; i < numCoins; i++) {{
    coinData.push({{ angle: 0 }});

    const card = document.createElement('div');
    card.className = 'coin-card';
    
    let edgeFacetsHTML = '<div class="coin-edge-3d">';
    for (let f = 0; f < numFacets; f++) {{
      let phi = f * (360 / numFacets);
      edgeFacetsHTML += `<div class="edge-facet" style="
        width: ${{facetWidth}}px;
        left: ${{facetLeft}}px;
        top: 29px;
        background-size: ${{numFacets * 100}}% 100%;
        background-position: -${{f * 100}}% 0;
        transform: rotateZ(${{phi}}deg) translateY(-${{radius}}px) rotateX(90deg);
      "></div>`;
    }}
    edgeFacetsHTML += '</div>';

    card.innerHTML = `
      <div style="font-size: 11px; color: #d4af37;">Qubit ${{i}}</div>
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

components.html(rng_tavern_html, height=600)
