import json
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Quantum Café - Keep the Qubit Alive", layout="wide")

# Custom CSS for clean layout
st.markdown("""
    <style>
    /* Make top header background transparent */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0) !important;
    }

    /* Hide top-right action buttons (Deploy, main menu) only */
    [data-testid="stToolbarActions"],
    .stAppDeployButton,
    #MainMenu {
        display: none !important;
    }

    /* Hide footer and 'Manage app' bottom-right widget */
    footer,
    [data-testid="stFooter"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Explicitly preserve sidebar toggle arrow and page navigation controls */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stHeaderNav"],
    [data-testid="stSidebarNav"] {
        display: flex !important;
        visibility: visible !important;
        z-index: 1000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
H_OVER_K = 4.799e-11          # h / k_B in K*s  (so h*f/(k_B*T) = H_OVER_K * f / T)
FIDELITY_LOST = 0.9           # the qubit counts as "lost" below this fidelity
X_LOST = 2 * FIDELITY_LOST - 1  # equivalent Bloch-vector length (0.8)

# ILLUSTRATIVE orders of magnitude, not vendor specifications.
# One "operation" = one typical gate slot on that platform.
PRESETS = {
    "Superconducting circuit": dict(
        kind="decoherence", T1=150e-6, T2=100e-6, t_gate=100e-9, eps=1e-3,
        f=5e9, T_ref=0.02, thermal=True,
        blurb="Artificial atoms on a chip, cooled to ~20 mK. Very fast gates, but "
              "the qubit only lives for ~100 microseconds.",
        temp_note="Fridge temperature. Warmer means thermal photons and faster decay.",
    ),
    "Trapped ion": dict(
        kind="decoherence", T1=10.0, T2=1.0, t_gate=50e-6, eps=1e-4,
        f=12.6e9, T_ref=300.0, thermal=False,
        blurb="Single atoms held by electric fields in vacuum. Extremely long-lived, "
              "but each gate takes a long time.",
        temp_note="Apparatus temperature. Heating shakes the ion and spoils its phase.",
    ),
    "Neutral atom": dict(
        kind="decoherence", T1=10.0, T2=1.0, t_gate=500e-9, eps=1e-3,
        f=6.8e9, T_ref=1e-5, thermal=False,
        blurb="Atoms in arrays of laser tweezers. Long-lived and easy to scale up, "
              "but laser noise limits the gates.",
        temp_note="Atom temperature in the tweezer. Hotter atoms dephase faster.",
    ),
    "Photonic": dict(
        kind="loss", loss_dB=0.05, vis_err=2e-3, t_gate=1e-9,
        blurb="Qubits carried by light. Photons barely interact with the environment, "
              "so they do not decohere - they get lost instead.",
        temp_note="Optical photons are not affected by room temperature at all.",
    ),
}

CODES = {
    "3-qubit repetition code (fixes dephasing only)": dict(
        n_phys=3, overhead=4, covers_all=False),
    "9-qubit Shor code (fixes any single error)": dict(
        n_phys=9, overhead=12, covers_all=True),
}


def knob_factor(v):
    """Slider 0-100 -> factor 0.1x ... 10x, with 50 = the preset's typical lab."""
    return 10 ** ((v - 50) / 50)


def platform_model(p, iso, noise, temp):
    """Per-operation decay numbers for a preset and the three knob positions."""
    F_iso, F_noise, F_T = knob_factor(iso), knob_factor(noise), knob_factor(temp)
    if p["kind"] == "loss":
        d_loss = np.log(10) / 10 * p["loss_dB"] / F_iso      # lost photon, per component
        d_vis = p["vis_err"] * F_noise                      # phase jitter / imperfect interference
        return dict(d_relax=d_loss, d_phase=d_vis, rate1=0.0, z_eq=0.0, p_th=0.0,
                    T=None, T2=None, t_gate=p["t_gate"], kind="loss")
    G1 = 1 / p["T1"] * F_T / F_iso
    Gphi0 = max(1 / p["T2"] - 1 / (2 * p["T1"]), 0.05 / p["T2"])
    Gphi = Gphi0 * F_noise * F_T / F_iso
    eps = p["eps"] * F_noise
    T = p["T_ref"] * F_T
    p_th = 1 / (1 + np.exp(H_OVER_K * p["f"] / T)) if p["thermal"] else 0.0
    return dict(
        d_relax=p["t_gate"] * G1 / 2,                 # energy relaxation (T1) share
        d_phase=p["t_gate"] * Gphi + 4 * eps / 3,     # dephasing + control error share
        rate1=p["t_gate"] * G1,                       # z relaxes toward z_eq at this rate per op
        z_eq=1 - 2 * p_th, p_th=p_th, T=T, T2=1 / (G1 / 2 + Gphi),
        t_gate=p["t_gate"], kind="decoherence",
    )


def ops_until_lost(delta):
    return np.log(1 / X_LOST) / delta


def qec_cycle(m, k, code):
    """Return (per-cycle logical Bloch decay factor) for the chosen code."""
    s = code["overhead"]
    if code["covers_all"]:
        delta_corr, delta_left, expo = m["d_relax"] + m["d_phase"], 0.0, 0
    else:
        delta_corr, delta_left, expo = m["d_phase"], m["d_relax"], code["n_phys"]
    p = (1 - np.exp(-(k + s) * delta_corr)) / 2           # flip probability per data qubit per cycle
    if code["covers_all"]:
        p_b = (1 - (1 - 2 * p) ** 3) / 2                  # phase flip of a whole 3-qubit block
        p_L = 3 * p_b**2 - 2 * p_b**3 + 9 * p**2
    else:
        p_L = 3 * p**2 - 2 * p**3
    p_L = min(p_L, 0.5)
    return (1 - 2 * p_L) * np.exp(-max(expo, 1) * (k + s) * delta_left), p_L


def fmt_ops(n):
    if n >= 1e6:
        return f"{n/1e6:.1f} million"
    if n >= 1e4:
        return f"{n:,.0f}"
    if n >= 100:
        return f"{n:,.0f}"
    return f"{n:.0f}" if n >= 10 else f"{n:.1f}"


def fmt_time(s):
    for unit, scale in (("s", 1), ("ms", 1e-3), ("µs", 1e-6), ("ns", 1e-9), ("ps", 1e-12)):
        if s >= scale:
            return f"{s/scale:.3g} {unit}"
    return f"{s:.2g} s"


def fmt_temp(T):
    for unit, scale in (("K", 1), ("mK", 1e-3), ("µK", 1e-6)):
        if T >= scale:
            return f"{T/scale:.3g} {unit}"
    return f"{T:.2g} K"


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("🫀 Keep the Qubit Alive")
st.write(
    "A qubit stores information in a delicate quantum state. The environment slowly "
    "scrambles it. **How many operations can you perform before the information is lost?** "
    "Pick a hardware platform, turn the noise, temperature and isolation knobs, and watch it fade."
)

DEFAULT_KNOBS = dict(iso=50, noise=50, temp=50)


def reset_knobs():
    for k, v in DEFAULT_KNOBS.items():
        st.session_state[k] = v


for k, v in DEFAULT_KNOBS.items():
    st.session_state.setdefault(k, v)

col_ctrl, col_view = st.columns([1, 1.7], gap="large")

with col_ctrl:
    st.subheader("🎛️ Controls")
    preset_name = st.selectbox("Hardware platform", list(PRESETS), key="preset", on_change=reset_knobs)
    preset = PRESETS[preset_name]
    st.caption(preset["blurb"])

    iso = st.slider("🛡️ Isolation (shielding, vacuum, vibration damping)", 0, 100, key="iso",
                    help="Higher isolation slows every decay process by up to 10x.")
    noise = st.slider("📣 Noise (stray fields, laser or control jitter)", 0, 100, key="noise",
                      help="More noise speeds up dephasing and adds control errors, by up to 10x.")
    temp = st.slider("🌡️ Temperature", 0, 100, key="temp", help=preset["temp_note"])
    st.caption("Sliders: **50 = typical lab conditions for this platform**. "
               "Every 25 steps changes the effect by about 3x (range 0.1x to 10x).")

    st.markdown("---")
    use_qec = st.toggle("🩹 Add error correction", value=False,
                        disabled=preset["kind"] == "loss",
                        help="Encode the qubit in several physical qubits and repair errors every few operations.")
    if preset["kind"] == "loss":
        st.caption("Photon loss is not fixed by these codes (it needs special loss-tolerant codes), "
                   "so the correction option is off for photonics.")
    code_name = k_cycle = None
    if use_qec:
        code_name = st.radio("Code", list(CODES), index=0)
        k_cycle = st.slider("Operations between correction rounds", 1, 20, 5)

model = platform_model(preset, iso, noise, temp)
delta = model["d_relax"] + model["d_phase"]
n_lost = ops_until_lost(delta)

qec = None
if use_qec:
    code = CODES[code_name]
    x_cycle, p_L = qec_cycle(model, k_cycle, code)
    if x_cycle > 0:
        qec = dict(code=code, x_cycle=x_cycle, p_L=p_L,
                   n_lost=k_cycle * np.log(X_LOST) / np.log(x_cycle),
                   ln_per_op=np.log(x_cycle) / k_cycle)

with col_view:
    # Headline number
    c1, c2, c3 = st.columns(3)
    c1.metric("Operations until lost", fmt_ops(n_lost),
              help=f"Fidelity with the original state drops below {FIDELITY_LOST:.0%}.")
    if model["kind"] == "decoherence":
        c2.metric("Coherence time (T2)", fmt_time(model["T2"]))
        c3.metric("Time until lost", fmt_time(n_lost * model["t_gate"]))
    else:
        c2.metric("Loss per component", f"{(1 - np.exp(-model['d_relax'])):.1%}")
        c3.metric("Interference error per op", f"{model['d_phase']:.2%}")
    if qec:
        gain = qec["n_lost"] / n_lost
        if gain > 1.05:
            st.success(f"🩹 With error correction: **{fmt_ops(qec['n_lost'])} operations** "
                       f"({gain:.1f}x more). Errors are rare enough that fixing them beats making them.")
        else:
            st.error(f"🩹 With error correction: **{fmt_ops(qec['n_lost'])} operations** "
                     f"({gain:.2f}x). The correction itself adds too many errors. "
                     "Lower the noise or raise isolation to get below the threshold.")

    # Animated Bloch-vector widget
    n_view = max(40.0, 3 * n_lost)
    cfg = dict(
        delta=float(delta), rate1=float(model["rate1"]), z_eq=float(model["z_eq"]),
        n_lost=float(n_lost), n_view=float(n_view), t_gate=float(model["t_gate"]),
        show_time=model["kind"] == "decoherence", f_lost=FIDELITY_LOST, x_lost=X_LOST,
        qec_per_op=float(qec["ln_per_op"]) if qec else None,
    )
    html = """
<style>
  body{margin:0;font-family:'Segoe UI',Tahoma,sans-serif;background:transparent;}
  .card{background:#1c0a14;border-radius:12px;padding:12px;color:#f3dbe4;text-align:center;}
  canvas{width:100%;max-width:520px;height:auto;aspect-ratio:520/340;display:block;margin:0 auto;}
  .row{display:flex;gap:8px;align-items:center;justify-content:center;flex-wrap:wrap;margin-top:6px;}
  button{background:#7b003e;color:#fff;border:1px solid #e8466a;border-radius:6px;padding:6px 14px;
         font-weight:bold;cursor:pointer;}
  button:hover{background:#a3004f;}
  input[type=range]{flex:1;min-width:140px;accent-color:#e8466a;}
  .stat{font-size:14px;margin-top:4px;}
  .lost{color:#ff6b6b;font-weight:bold;}
  .ok{color:#8be9a8;}
</style>
<div class="card">
  <canvas id="c" width="1040" height="680"></canvas>
  <div class="stat" id="stat"></div>
  <div class="row">
    <button id="play">Pause</button><button id="restart">Restart</button>
    <input type="range" id="scrub" min="0" max="1000" value="0">
  </div>
</div>
<script>
const C = __CFG__;
const cv = document.getElementById('c'), g = cv.getContext('2d');
const W = cv.width, H = cv.height, cx = W*0.5, cy = H*0.52, R = H*0.36;
let u = 0, playing = true, last = null;
const stat = document.getElementById('stat'), scrub = document.getElementById('scrub');
const playBtn = document.getElementById('play');
const trail = [];

function state(n){
  const x = Math.exp(-n*C.delta);
  const z = C.z_eq*(1-Math.exp(-n*C.rate1));
  const xp = C.qec_per_op===null ? null : Math.exp(n*C.qec_per_op);
  return {x, z, xp};
}
function pt(x,z){ return [cx + x*R, cy - z*R]; }
function arrow(x,z,col,w){
  const [px,py] = pt(x,z);
  g.strokeStyle = col; g.fillStyle = col; g.lineWidth = w;
  g.beginPath(); g.moveTo(cx,cy); g.lineTo(px,py); g.stroke();
  g.beginPath(); g.arc(px,py,w*1.8,0,7); g.fill();
}
function label(t,x,y,col){ g.fillStyle=col||'#c9a6b6'; g.font='26px Segoe UI'; g.textAlign='center'; g.fillText(t,x,y); }

function draw(){
  const n = u*C.n_view, s = state(n);
  g.clearRect(0,0,W,H);
  // sphere outline and axes
  g.strokeStyle='#5c2b42'; g.lineWidth=3;
  g.beginPath(); g.arc(cx,cy,R,0,7); g.stroke();
  g.lineWidth=1.5; g.setLineDash([8,8]);
  g.beginPath(); g.moveTo(cx-R,cy); g.lineTo(cx+R,cy); g.moveTo(cx,cy-R); g.lineTo(cx,cy+R); g.stroke();
  // "lost" boundary: vector shorter than x_lost along the |+> axis
  g.strokeStyle='#ff6b6b'; g.beginPath(); g.moveTo(cx+C.x_lost*R,cy-R*0.45); g.lineTo(cx+C.x_lost*R,cy+R*0.45); g.stroke();
  g.setLineDash([]);
  label('|0>',cx,cy-R-14); label('|1>',cx,cy+R+34); label('|+>',cx+R+34,cy+8); label('|->',cx-R-34,cy+8);
  label('fully mixed (information gone)',cx,cy+R*0.62,'#7e5468');
  // thermal equilibrium marker
  if (Math.abs(C.z_eq-1)>0.02){ const [ex,ey]=pt(0,C.z_eq); g.fillStyle='#6ab0ff'; g.beginPath(); g.arc(ex,ey,8,0,7); g.fill();
    g.font='22px Segoe UI'; g.textAlign='left'; g.fillText('thermal',ex+14,ey+7); }
  // trail
  trail.push(pt(s.x,s.z)); if(trail.length>160) trail.shift();
  g.strokeStyle='rgba(232,70,106,0.35)'; g.lineWidth=4; g.beginPath();
  trail.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1])); g.stroke();
  if (s.xp!==null) arrow(s.xp,0,'#8be9a8',6);
  const F = (1+s.x)/2, lost = F < C.f_lost;
  arrow(s.x,s.z,lost?'#ff6b6b':'#e8466a',8);
  // fidelity bar
  g.fillStyle='#331424'; g.fillRect(20,H-34,W-40,16);
  g.fillStyle=lost?'#ff6b6b':'#e8466a'; g.fillRect(20,H-34,(W-40)*Math.max(0,(F-0.5)/0.5),16);
  g.fillStyle='#fff'; g.fillRect(20+(W-40)*((C.f_lost-0.5)/0.5)-2,H-40,4,28);

  let txt = 'Operations: <b>'+Math.round(n).toLocaleString()+'</b>';
  if (C.show_time) txt += ' &nbsp;·&nbsp; time: <b>'+fmtT(n*C.t_gate)+'</b>';
  txt += ' &nbsp;·&nbsp; fidelity: <b>'+(F*100).toFixed(1)+'%</b> &nbsp; ';
  txt += lost ? '<span class="lost">QUBIT LOST</span>' : '<span class="ok">alive</span>';
  if (s.xp!==null){ const Fp=(1+s.xp)/2; txt += '<br><span style="color:#8be9a8">green arrow: error-corrected qubit, fidelity '+(Fp*100).toFixed(1)+'%</span>'; }
  stat.innerHTML = txt;
  scrub.value = Math.round(u*1000);
}
function fmtT(t){ const U=[['s',1],['ms',1e-3],['µs',1e-6],['ns',1e-9],['ps',1e-12]];
  for (const [n,k] of U) if (t>=k) return (t/k).toPrecision(3)+' '+n; return t.toExponential(1)+' s'; }
function loop(ts){
  if(last===null) last=ts; const dt=(ts-last)/1000; last=ts;
  if(playing){ u += dt/14; if(u>=1){u=1; playing=false; playBtn.textContent='Play';} }
  draw(); requestAnimationFrame(loop);
}
playBtn.onclick=()=>{ if(u>=1) u=0; playing=!playing; playBtn.textContent=playing?'Pause':'Play'; };
document.getElementById('restart').onclick=()=>{u=0;trail.length=0;playing=true;playBtn.textContent='Pause';};
scrub.oninput=()=>{u=scrub.value/1000; playing=false; trail.length=0; playBtn.textContent='Play';};
requestAnimationFrame(loop);
</script>
""".replace("__CFG__", json.dumps(cfg))
    components.html(html, height=540)

    # Fidelity versus operations
    ops = np.unique(np.geomspace(1, max(100.0, 8 * n_lost), 300))
    frames = [pd.DataFrame(dict(ops=ops, fidelity=(1 + np.exp(-ops * delta)) / 2, curve="No correction"))]
    if qec:
        frames.append(pd.DataFrame(dict(ops=ops, fidelity=(1 + np.exp(ops * qec["ln_per_op"])) / 2,
                                        curve="With error correction")))
    df = pd.concat(frames)
    line = alt.Chart(df).mark_line(strokeWidth=3).encode(
        x=alt.X("ops:Q", scale=alt.Scale(type="log"), title="Operations performed (log scale)"),
        y=alt.Y("fidelity:Q", scale=alt.Scale(domain=[0.5, 1.0]), title="Fidelity with the original state"),
        color=alt.Color("curve:N", title=None, scale=alt.Scale(
            domain=["No correction", "With error correction"], range=["#e8466a", "#2fa66a"])),
    )
    rule = alt.Chart(pd.DataFrame(dict(y=[FIDELITY_LOST]))).mark_rule(
        strokeDash=[6, 4], color="#999").encode(y="y:Q")
    st.altair_chart((line + rule).properties(height=260), width="stretch")
    st.caption(f"Dashed line: the qubit counts as lost when fidelity drops below {FIDELITY_LOST:.0%}.")

# ---------------------------------------------------------------------------
# Platform comparison and explanations
# ---------------------------------------------------------------------------
st.divider()
st.subheader("⚖️ How many operations fit? Platforms side by side")
rows = []
for name, p in PRESETS.items():
    m = platform_model(p, iso, noise, temp)
    d = m["d_relax"] + m["d_phase"]
    rows.append(dict(platform=name, ops=ops_until_lost(d), time=m["t_gate"] * ops_until_lost(d)))
cmp_df = pd.DataFrame(rows)
cmp_df["one"] = 1.0                                   # log axes need a baseline above zero
bar = alt.Chart(cmp_df).mark_bar().encode(
    y=alt.Y("platform:N", sort="-x", title=None),
    x=alt.X("ops:Q", scale=alt.Scale(type="log", domain=[1, float(cmp_df["ops"].max()) * 2]),
            title="Operations before the qubit is lost (log scale)"),
    x2="one:Q",
    color=alt.Color("platform:N", legend=None, scale=alt.Scale(
        range=["#7b003e", "#e8466a", "#b07a92", "#4a4a4a"])),
    tooltip=["platform", alt.Tooltip("ops:Q", format=",.0f")],
)
st.altair_chart(bar.properties(height=200), width="stretch")
st.caption("The same knob positions are applied to every platform, each relative to its own typical lab. "
           "Note that the longest-lived qubit is not always the one that runs the most operations: "
           "a slow gate wastes a long lifetime.")

with st.expander("📐 What the sliders do, and what this model is (and is not)"):
    st.markdown(
        r"""
**The idea.** We start the qubit in $|+\rangle$, an equal superposition of 0 and 1, which is the most fragile
case because the information sits in the *phase*. In the picture, the pink arrow is the qubit's state.
As the environment acts, the arrow shrinks towards the centre (the fully mixed state, which carries no
information) and may also drift towards the thermal state.

**Two kinds of decay.**
- **Relaxation ($T_1$)**: the qubit loses energy and falls towards its ground state. Higher temperature makes this faster.
- **Dephasing ($T_2$)**: the phase relationship between 0 and 1 is scrambled by stray fields and jitter. Noise makes this faster.

**Operations before lost** $\approx \ln(1/0.8)\,/\,\delta$, where $\delta$ is the decay per operation:
$\delta \approx t_\text{gate}\left(\tfrac{1}{2T_1}+\tfrac{1}{T_\varphi}\right)+\tfrac{4}{3}\varepsilon$, with $\varepsilon$ the control error per gate.
This is where the speed of the gates meets the lifetime of the qubit.

**The sliders** (50 = typical lab; ×0.1 to ×10 across the range):
isolation divides all decay rates; noise multiplies dephasing and control error; temperature multiplies both
decay rates and, for superconducting qubits, sets the thermal excited population through $h f / k_B T$.

**Photonics** is different: photons hardly decohere, they get absorbed or scattered. Each component loses a
fraction of the light (in dB) and imperfect interference adds phase errors. Temperature has no effect on optical photons.

⚠️ *All platform numbers are illustrative orders of magnitude chosen for teaching, not vendor specifications.
Real devices vary by a factor of 10 or more between labs and years.*
"""
    )

with st.expander("🩹 Can we rescue the information? Error correction explained"):
    st.markdown(
        r"""
Yes, partly. The trick is **redundancy without copying** (quantum states cannot be copied):
spread one logical qubit over several physical qubits, then regularly measure *parities* (syndromes) that
reveal *where* an error happened without revealing the stored information, and undo it.

- **3-qubit repetition code.** Protects against one type of error (here: phase flips, i.e. dephasing). One flip among three qubits is outvoted.
  If a single physical qubit fails with probability $p$, the logical qubit fails with probability about $3p^2 - 2p^3$, much smaller when $p$ is small.
- **9-qubit Shor code.** Combines a phase-flip and a bit-flip layer so that any single error is repaired.

**The catch: a threshold.** Checking the qubits takes extra operations, and those operations add their own errors.
If the physical error rate is low enough, correction wins. If it is too high, the repair does more damage than it prevents.
Move the noise slider with the correction switched on and find the crossover on the graph.

**Reality check.** Real machines use codes such as the surface code, needing tens to thousands of physical qubits per
logical qubit. That overhead is the reason today's devices are called *noisy*, and why platform
quality (long coherence, fast and accurate gates) matters so much.

*Simplifications here: errors are modelled as independent, syndrome extraction is a fixed number of extra
noisy operation slots (4 for the 3-qubit code, 12 for the 9-qubit code), and measurement errors and fault-tolerant details are ignored.
The 3-qubit code does not protect against energy relaxation, which is counted as uncorrected damage on all three qubits.*
"""
    )
