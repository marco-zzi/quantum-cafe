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
    padding: 0 0 16px 0;
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

  .face-front {{ background-image: url('data:image/png;base64,{front_b64}'); }}
  .face-back  {{ background-image: url('data:image/png;base64,{back_b64}'); }}

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

  /* Control Panel for Entanglement Selection */
  .mode-bar {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin: 10px auto 12px auto;
    flex-wrap: wrap;
    max-width: 720px;
  }}

  .mode-btn {{
    background: #1e110a;
    color: #b8975a;
    border: 1px solid #5a3c1e;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: bold;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }}

  .mode-btn:hover {{
    background: #382112;
    color: #ffd875;
  }}

  .mode-btn.active {{
    background: #8a5a12;
    color: #ffffff;
    border-color: #ffd875;
    box-shadow: 0 0 8px rgba(212, 175, 55, 0.5);
  }}

  .mode-btn.reset {{
    background: #3a1212;
    color: #ff8888;
    border-color: #772222;
  }}

  .mode-btn.reset:hover {{
    background: #551818;
    color: #ffaaaa;
  }}

  .status-text {{
    font-size: 13px;
    color: #00e5ff;
    margin: 4px 0 10px 0;
    min-height: 18px;
  }}

  .entangle-badge {{
    font-size: 10px;
    font-weight: bold;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
    margin-top: 2px;
    display: inline-block;
  }}

  /* Locked / Pending States */
  .coin-card.pending {{
    border: 2px dashed #00e5ff !important;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.6) !important;
  }}

  .coin-card.locked .coin-slot {{
    cursor: not-allowed !important;
  }}

  /* ==========================================================================
     1. DESKTOP MODE ONLY (min-width: 681px)
     ========================================================================== */
  @media (min-width: 681px) {{
    .app-title {{
      font-size: 24px;
      margin: 6px 0 4px 0;
      color: #f3e5ab;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}

    .app-subtitle {{
      font-size: 13px;
      font-style: italic;
      color: #b8975a;
      margin: 10px 0 16px 0;
    }}

    .tavern-stage {{
      position: relative;
      width: 100%;
      max-height: 540px;
      aspect-ratio: 16 / 9;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 15px 35px rgba(0,0,0,0.9);
      background-image: url('data:image/jpeg;base64,{table_desktop_b64}');
      background-size: cover;
      background-position: center;
    }}

    .table-overlay {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 90%;
      max-width: 720px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      justify-items: center;
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
      cursor: pointer;
      transition: all 0.2s;
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
      margin: 6px auto;
      perspective: 600px;
      cursor: ew-resize;
      touch-action: none;
    }}

    .face-front {{ transform: translateZ(4px); }}
    .face-back  {{ transform: rotateY(180deg) translateZ(4px); }}

    .edge-facet {{
      height: 8px;
      width: calc(var(--coin-radius) * 0.3978);
      left: calc(50% - (var(--coin-radius) * 0.1989));
      top: calc(50% - 4px);
    }}

    .stats {{
      font-size: 13px;
      margin-top: 2px;
      color: #fce8bd;
      font-weight: bold;
    }}

    .ui-panel {{
      position: relative;
      margin: 14px auto 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      width: 90%;
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
    .app-title {{ display: none !important; }}

    .app-subtitle {{
      font-size: 11px;
      font-style: italic;
      color: #b8975a;
      margin: 8px 0 10px 0;
    }}

    .tavern-stage {{
      position: relative;
      width: 100%;
      aspect-ratio: 9 / 16;
      max-height: 480px;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.9);
      background-image: url('data:image/jpeg;base64,{table_mobile_b64}');
      background-size: cover;
      background-position: center;
    }}

    .table-overlay {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 92%;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      justify-items: center;
    }}

    .coin-card {{
      background: rgba(40, 22, 10, 0.78);
      border: 1px solid #8b5a2b;
      backdrop-filter: blur(4px);
      border-radius: 8px;
      padding: 6px;
      width: 100%;
      box-shadow: 0 4px 10px rgba(0,0,0,0.6);
      cursor: pointer;
    }}

    .card-header {{
      font-size: 12px;
      color: #ffd875;
      font-weight: bold;
    }}

    .coin-slot {{
      --coin-radius: 28px;
      width: 56px;
      height: 56px;
      margin: 4px auto;
      perspective: 600px;
      cursor: ew-resize;
      touch-action: none;
    }}

    .face-front {{ transform: translateZ(3px); }}
    .face-back  {{ transform: rotateY(180deg) translateZ(3px); }}

    .edge-facet {{
      height: 6px;
      width: calc(var(--coin-radius) * 0.3978);
      left: calc(50% - (var(--coin-radius) * 0.1989));
      top: calc(50% - 3px);
    }}

    .stats {{
      font-size: 11px;
      margin-top: 2px;
      color: #fce8bd;
      font-weight: bold;
    }}

    .ui-panel {{
      position: relative;
      margin: 10px auto 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      width: 95%;
    }}

    .measure-btn {{
      background: linear-gradient(to bottom, #d4af37, #8a5a12);
      color: #120a05;
      border: 1px solid #ffe89c;
      padding: 8px 22px;
      font-size: 14px;
      font-weight: bold;
      border-radius: 8px;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(0,0,0,0.7);
    }}

    .result-box {{
      font-size: 13px;
      letter-spacing: 1px;
      color: #00ffcc;
      font-family: monospace;
      background: rgba(0,0,0,0.85);
      padding: 5px 10px;
      border-radius: 6px;
      border: 1px solid #00ffcc44;
    }}
  }}
</style>
</head>
<body>

  <h1 class="app-title">🎲 Quantum Random Number Generator</h1>

  <!-- Entanglement Mode Selection Bar -->
  <div class="mode-bar">
    <button class="mode-btn active" id="btnModeSingle" onclick="setMode('single')">Single Rotation</button>
    <button class="mode-btn" id="btnModeBell" onclick="setMode('bell')">🔗 Bell State (Pairs)</button>
    <button class="mode-btn" id="btnModeGHZ" onclick="setMode('ghz')">🌐 GHZ State (Triplets)</button>
    <button class="mode-btn reset" onclick="clearEntanglements()">Clear Entanglements</button>
  </div>

  <div class="status-text" id="statusMessage">Mode: Single Qubit (Drag coins to set superposition)</div>

  <!-- Game Table Stage -->
  <div class="tavern-stage">
    <div class="table-overlay" id="tableSurface"></div>
  </div>

  <!-- External Measure Panel -->
  <div class="ui-panel">
    <button class="measure-btn" onclick="measureByte()">⚡ Measure</button>
    <div class="result-box" id="byteResult">Result: [ Unmeasured ]</div>
  </div>

  <p class="app-subtitle">Drag coins to rotate or select Bell/GHZ modes to create correlated quantum entanglement.</p>

<script>
  const numCoins = 8;
  const numFacets = 16;
  const table = document.getElementById('tableSurface');

  let currentMode = 'single'; // 'single', 'bell', 'ghz'
  let pendingSelection = [];
  let groups = []; 
  const groupColors = ['#00e5ff', '#ff007f', '#00ff66', '#ffbe00', '#a100ff'];

  let coinData = Array.from({{ length: numCoins }}, () => ({{
    angle: 0,
    locked: false,
    groupId: null
  }}));

  // Initialize Qubit Cards
  for (let i = 0; i < numCoins; i++) {{
    const card = document.createElement('div');
    card.className = 'coin-card';
    card.id = `card_${{i}}`;
    
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
      <div id="badge_${{i}}"></div>
    `;

    card.addEventListener('click', (e) => handleCardClick(i, e));
    table.appendChild(card);
    setupInteraction(i);
  }}

  function setMode(mode) {{
    currentMode = mode;
    pendingSelection = [];
    
    document.getElementById('btnModeSingle').classList.toggle('active', mode === 'single');
    document.getElementById('btnModeBell').classList.toggle('active', mode === 'bell');
    document.getElementById('btnModeGHZ').classList.toggle('active', mode === 'ghz');

    updateUIStatus();
    updateCardVisuals();
  }}

  function updateUIStatus() {{
    const msg = document.getElementById('statusMessage');
    if (currentMode === 'single') {{
      msg.innerText = "Mode: Single Qubit (Drag coins horizontally)";
    }} else if (currentMode === 'bell') {{
      msg.innerText = `Mode: Bell State | Click 2 qubits to entangle (${{pendingSelection.length}}/2 selected)`;
    }} else if (currentMode === 'ghz') {{
      msg.innerText = `Mode: GHZ State | Click 3 qubits to entangle (${{pendingSelection.length}}/3 selected)`;
    }}
  }}

  function handleCardClick(index, e) {{
    // If clicking directly on drag area in single mode, skip mode selection
    if (currentMode === 'single') return;

    // Disband group if user clicks an already entangled card
    if (coinData[index].groupId) {{
      const gId = coinData[index].groupId;
      groups = groups.filter(g => g.id !== gId);
      coinData.forEach((c, idx) => {{
        if (c.groupId === gId) {{
          c.locked = false;
          c.groupId = null;
          c.angle = 0;
          updateCoinVisual(idx);
        }}
      }});
      pendingSelection = pendingSelection.filter(id => id !== index);
      updateCardVisuals();
      updateUIStatus();
      return;
    }}

    const targetSize = currentMode === 'bell' ? 2 : 3;
    const pIdx = pendingSelection.indexOf(index);

    if (pIdx !== -1) {{
      pendingSelection.splice(pIdx, 1);
    }} else {{
      pendingSelection.push(index);
      if (pendingSelection.length === targetSize) {{
        // Create Entanglement Group
        const groupColor = groupColors[groups.length % groupColors.length];
        const newGroupId = 'group_' + Date.now();
        const newGroup = {{
          id: newGroupId,
          type: currentMode.toUpperCase(),
          members: [...pendingSelection],
          color: groupColor
        }};
        groups.push(newGroup);

        // Lock entangled qubits to 50% superposition (|0> + |1>) / sqrt(2)
        newGroup.members.forEach(m => {{
          coinData[m].locked = true;
          coinData[m].groupId = newGroupId;
          coinData[m].angle = 90; 
          updateCoinVisual(m);
        }});

        pendingSelection = [];
      }}
    }}

    updateCardVisuals();
    updateUIStatus();
  }}

  function clearEntanglements() {{
    groups = [];
    pendingSelection = [];
    coinData.forEach((c, i) => {{
      c.locked = false;
      c.groupId = null;
      c.angle = 0;
      updateCoinVisual(i);
    }});
    updateCardVisuals();
    updateUIStatus();
  }}

  function updateCardVisuals() {{
    for (let i = 0; i < numCoins; i++) {{
      const card = document.getElementById(`card_${{i}}`);
      const badge = document.getElementById(`badge_${{i}}`);
      const isPending = pendingSelection.includes(i);
      const group = groups.find(g => g.members.includes(i));

      card.classList.toggle('pending', isPending);
      card.classList.toggle('locked', coinData[i].locked);

      if (group) {{
        card.style.borderColor = group.color;
        card.style.boxShadow = `0 0 12px ${{group.color}}66`;
        badge.innerHTML = `<span class="entangle-badge" style="background:${{group.color}}33; color:${{group.color}}; border: 1px solid ${{group.color}};">${{group.type}}</span>`;
      }} else {{
        card.style.borderColor = '';
        card.style.boxShadow = '';
        badge.innerHTML = '';
      }}
    }}
  }}

  function setupInteraction(index) {{
    const slot = document.getElementById(`slot_${{index}}`);
    let isDragging = false;
    let startX = 0;

    slot.addEventListener('mousedown', (e) => {{
      if (coinData[index].locked) return;
      isDragging = true;
      startX = e.clientX;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (!isDragging || coinData[index].locked) return;
      let deltaX = e.clientX - startX;
      startX = e.clientX;

      coinData[index].angle += deltaX * 1.5;
      updateCoinVisual(index);
    }});

    window.addEventListener('mouseup', () => {{ isDragging = false; }});

    slot.addEventListener('touchstart', (e) => {{
      if (coinData[index].locked) return;
      isDragging = true;
      startX = e.touches[0].clientX;
    }}, {{ passive: true }});

    window.addEventListener('touchmove', (e) => {{
      if (!isDragging || coinData[index].locked) return;
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
    let results = new Array(numCoins);

    // 1. Measure Entangled Groups (Correlated Outcomes)
    groups.forEach(group => {{
      let groupOutcome = Math.random() < 0.5 ? "1" : "0";
      group.members.forEach(m => {{
        results[m] = groupOutcome;
      }});
    }});

    // 2. Measure Independent Unentangled Qubits
    for (let i = 0; i < numCoins; i++) {{
      if (results[i] === undefined) {{
        let angle = coinData[i].angle;
        let normalizedAngle = (angle % 360 + 360) % 360;
        let prob1 = Math.sin((normalizedAngle * Math.PI) / 360) ** 2;
        results[i] = Math.random() < prob1 ? "1" : "0";
      }}
    }}

    // 3. Apply Visual Collapse & Transitions
    let binaryString = "";
    for (let i = 0; i < numCoins; i++) {{
      let outcome = results[i];
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

components.html(rng_tavern_html, height=1050)
