"""Shared look for every Quantum Café page: one set of design tokens, applied to Streamlit's own widgets.

The interactive areas (assets/*.html) carry the same tokens in their own <style> blocks, because they live in
iframes. If you change a colour or a type rule here, change it there too.
"""
import altair as alt
import streamlit as st

# Design tokens (Apple dark system palette, restrained)
BG = "#0b0b10"
LABEL = "#f5f5f7"
LABEL2 = "rgba(235,235,245,.62)"
LABEL3 = "rgba(235,235,245,.34)"
FILL = "rgba(255,255,255,.07)"
FILL2 = "rgba(255,255,255,.12)"
OK = "#32d74b"
BAD = "#ff453a"
ACCENT = "190,200,255"

SYS = ('-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI Variable Text", "Segoe UI", '
       'system-ui, sans-serif')
DISP = ('-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI Variable Display", "Segoe UI", '
        'system-ui, sans-serif')
SERIF = 'ui-serif, "New York", "Iowan Old Style", Georgia, serif'

CSS = """
:root{
  --bg:#0b0b10; --label:#f5f5f7; --label2:rgba(235,235,245,.62); --label3:rgba(235,235,245,.34);
  --fill:rgba(255,255,255,.07); --fill2:rgba(255,255,255,.12); --sep:rgba(255,255,255,.09);
  --ok:#32d74b; --bad:#ff453a; --acc:__ACCENT__;
  --sys:__SYS__; --disp:__DISP__; --serif:__SERIF__;
}
html, body, .stApp, [data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--label);
  font-family:var(--sys);-webkit-font-smoothing:antialiased}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbarActions"], .stAppDeployButton, #MainMenu, footer, [data-testid="stFooter"],
[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stSidebarCollapseButton"], [data-testid="stHeaderNav"], [data-testid="stSidebarNav"]{
  display:flex!important;visibility:visible!important;z-index:1000000!important}
.block-container{max-width:1120px!important;padding:3.2rem 1.6rem 5rem!important}

/* type: tight tracking on large text, comfortable leading on body */
h1, h2, h3, h4{font-family:var(--disp)!important;color:var(--label)!important}
h1{font-weight:700!important;font-size:clamp(30px,5vw,46px)!important;line-height:1.05!important;letter-spacing:-.025em!important;padding:0 0 .35rem!important}
h2{font-weight:650!important;font-size:28px!important;letter-spacing:-.02em!important}
h3{font-weight:600!important;font-size:21px!important;letter-spacing:-.015em!important;line-height:1.2!important}
h1 a, h2 a, h3 a{display:none!important}
p, li, label, .stMarkdown{font-size:16px;line-height:1.5}
[data-testid="stCaptionContainer"], .stCaption{color:var(--label2)!important;font-size:14px!important}
hr{border-color:var(--sep)!important;margin:2rem 0!important}
a{color:rgb(var(--acc))}
code{background:var(--fill)!important;border-radius:6px;padding:.1em .35em}
.qc-eyebrow{font:600 11.5px/1 var(--sys);letter-spacing:.08em;text-transform:uppercase;color:var(--label3);margin:0 0 10px}
.qc-lede{font-size:19px;line-height:1.45;color:var(--label2);max-width:46ch;margin:18px 0 0!important}
.qc-serif{font-family:var(--serif)!important;letter-spacing:-.015em}

/* sidebar */
[data-testid="stSidebar"]{background:#0e0e14!important;border-right:1px solid var(--sep)}
[data-testid="stSidebarNav"] a{border-radius:12px;padding:.45rem .7rem;font-weight:500}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:var(--fill2)!important}

/* tabs as a segmented control (ARIA roles, so it survives Streamlit upgrades) */
[role="tablist"]{background:var(--fill);border-radius:14px;padding:3px!important;gap:2px!important;width:fit-content;max-width:100%;overflow-x:auto;border:0!important;box-shadow:none!important}
[role="tablist"]::before,[role="tablist"]::after,[role="tab"]::before,[role="tab"]::after,
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"],.react-aria-SelectionIndicator,[role="tablist"] [class*="SelectionIndicator"]{display:none!important}
[role="tab"]{border-radius:11px!important;padding:8px 16px!important;height:auto!important;border:0!important;box-shadow:none;
  background:transparent!important;color:var(--label2)!important;font-weight:600!important;font-size:14.5px!important;transition:background .2s,color .2s}
[role="tab"] *{color:inherit!important;font-weight:600!important;font-size:14.5px!important}
[role="tab"][aria-selected="true"]{background:rgba(255,255,255,.16)!important;color:var(--label)!important;box-shadow:0 1px 3px rgba(0,0,0,.4)}
[role="tab"]:hover{color:var(--label)!important}
[role="tabpanel"]{padding-top:1.4rem!important}

/* metrics as quiet cards */
[data-testid="stMetric"]{background:var(--fill);border-radius:20px;padding:16px 18px}
[data-testid="stMetricLabel"] p{font:600 11.5px/1.2 var(--sys)!important;letter-spacing:.06em;text-transform:uppercase;color:var(--label3)!important;white-space:normal!important;overflow:visible!important;text-overflow:clip!important}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] > div{overflow:visible!important}
[data-testid="stMetricValue"]{font:700 34px/1.1 var(--disp)!important;letter-spacing:-.02em;font-variant-numeric:tabular-nums}

/* controls */
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="base-input"]{background:var(--fill)!important;border:0!important;border-radius:12px!important}
.stButton > button, [data-testid="stPageLink"] a{border-radius:12px;border:0;background:var(--fill2);font-weight:600;transition:transform .1s,background .2s}
.stButton > button:active{transform:scale(.97)}
[data-testid="stSlider"] label p, [data-testid="stSelectbox"] label p, [data-testid="stRadio"] label p, [data-testid="stToggle"] label p{font-size:14px;font-weight:600}
[data-testid="stAlert"]{border:0!important;border-radius:16px!important}
[data-testid="stExpander"]{background:var(--fill);border:0!important;border-radius:18px!important}
[data-testid="stExpander"] summary{font-weight:600}
[data-testid="stDataFrame"], [data-testid="stTable"]{border-radius:16px;overflow:hidden}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th{font:600 11.5px/1.2 var(--sys)!important;letter-spacing:.06em;text-transform:uppercase;color:var(--label3)!important;text-align:left}
th, td{border:0!important;border-bottom:1px solid var(--sep)!important;padding:10px 12px!important}
iframe{border:0!important;border-radius:28px;background:transparent}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.16);border-radius:6px}

/* home page cards */
.qc-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:6px 0 4px}
@media (min-width:1040px){.qc-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:560px){.qc-grid{grid-template-columns:1fr}}
.qc-card{background:var(--fill);border-radius:22px;padding:20px 20px 18px;display:flex;flex-direction:column;gap:6px;
  text-decoration:none!important;color:var(--label)!important;transition:transform .22s cubic-bezier(.2,.8,.2,1),background .22s}
a.qc-card:hover{background:var(--fill2);transform:translateY(-2px)}
a.qc-card:active{transform:scale(.975)}
.qc-card .t{font:600 22px/1.15 var(--serif);letter-spacing:-.01em;margin:4px 0 2px}
.qc-card .d{font-size:14.5px;line-height:1.45;color:var(--label2)}
.qc-chip{align-self:flex-start;margin-top:auto;padding:6px 12px;border-radius:999px;background:rgba(var(--acc),.16);color:rgb(var(--acc));font-weight:600;font-size:13px}
.qc-chip.off{background:var(--fill);color:var(--label3)}
.qc-card .spacer{flex:1}
@media (prefers-reduced-transparency:reduce){[data-testid="stSidebar"]{background:#0e0e14!important}}
@media (prefers-reduced-motion:reduce){.qc-card,.stButton > button,button[data-baseweb="tab"]{transition:none}}
"""


def apply_theme():
    """Inject the shared CSS and register the chart theme. Call once at the top of every page."""
    css = (CSS.replace("__ACCENT__", ACCENT).replace("__SYS__", SYS)
              .replace("__DISP__", DISP).replace("__SERIF__", SERIF))
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    alt.themes.register("qc", _chart_theme)
    alt.themes.enable("qc")


def _chart_theme():
    axis = dict(labelColor="#a1a1a6", titleColor="#a1a1a6", labelFont=SYS, titleFont=SYS,
                titleFontWeight=500, titleFontSize=12, labelFontSize=11.5,
                gridColor="rgba(255,255,255,.08)", domainColor="rgba(255,255,255,.18)", tickColor="rgba(255,255,255,.18)")
    return {"config": {
        "background": "transparent", "view": {"stroke": "transparent"}, "font": SYS,
        "axis": axis,
        "legend": dict(labelColor="#a1a1a6", titleColor="#a1a1a6", labelFont=SYS, titleFont=SYS, symbolType="circle"),
        "range": {"category": ["#bec8ff", "#ffd678", "#8edeff", "#32d74b"]},
    }}


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(rgb)
