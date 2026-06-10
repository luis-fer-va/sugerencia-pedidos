"""Tema visual de la app (dark cálido "carnicería premium").

Replica la estética del prototipo `docs/prototipo_visual.html`:
paleta oxblood + dorado + crema sobre charcoal cálido, tipografía display
serif (Fraunces) + Inter para datos, tarjetas redondeadas y sombras suaves.

Uso:
    from src.app.ui.theme import inyectar_estilos, COLORES
    inyectar_estilos()
"""
from __future__ import annotations

import streamlit as st

# --- Paleta exportada (reutilizable en componentes) ------------------------------
COLORES: dict[str, str] = {
    "bg": "#15100d",
    "bg_2": "#1c1511",
    "panel": "#221913",
    "panel_2": "#2a201a",
    "line": "#3a2c22",
    "line_soft": "#30241c",
    "txt": "#f3e8dc",
    "muted": "#a8978a",
    "faint": "#7c6c5f",
    "ox": "#c0392b",
    "ox_bright": "#e24a3a",
    "ox_deep": "#8c2018",
    "gold": "#e8a33d",
    "gold_bright": "#ffc46b",
    "cream": "#f3ddb8",
    "green": "#3fae6f",
    "green_deep": "#0e3a22",
}


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,800;9..144,900&family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#15100d; --bg-2:#1c1511; --panel:#221913; --panel-2:#2a201a;
  --line:#3a2c22; --line-soft:#30241c;
  --txt:#f3e8dc; --muted:#a8978a; --faint:#7c6c5f;
  --ox:#c0392b; --ox-bright:#e24a3a; --ox-deep:#8c2018;
  --gold:#e8a33d; --gold-bright:#ffc46b; --cream:#f3ddb8;
  --green:#3fae6f; --green-deep:#0e3a22;
  --shadow:0 18px 48px -12px rgba(0,0,0,.7);
}

/* ---- Fondo cálido con halos oxblood/dorado ---- */
.stApp{
  background:
    radial-gradient(900px 480px at 78% -8%, rgba(192,57,43,.20) 0%, transparent 60%),
    radial-gradient(700px 420px at 12% 4%, rgba(232,163,61,.10) 0%, transparent 55%),
    linear-gradient(180deg,#15100d 0%, #120d0a 100%) fixed;
  color:var(--txt);
  font-family:'Inter',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased; letter-spacing:.1px;
}
.block-container{max-width:1180px;padding-top:1.6rem;padding-bottom:3rem;}

/* ---- Ocultar chrome default de Streamlit ---- */
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;height:0;}
div[data-testid="stToolbar"]{display:none;}
div[data-testid="stDecoration"]{display:none;}

/* ---- Tipografía ---- */
h1,h2,h3,h4{font-family:'Fraunces',serif;color:var(--cream);letter-spacing:.2px;}
.stMarkdown,.stText,p,label,span,div{font-family:'Inter',system-ui,sans-serif;}

/* ---- Header custom ---- */
.lr-topbar{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:18px;}
.lr-brand{display:flex;align-items:center;gap:16px;}
.lr-badge{width:66px;height:66px;border-radius:50%;flex:none;position:relative;
  background:radial-gradient(circle at 50% 38%, #f7d9a6, #e9a23c 70%, #c0392b 71%);
  display:grid;place-items:center;overflow:hidden;
  box-shadow:0 0 0 3px var(--ox-deep), 0 8px 22px rgba(192,57,43,.45), inset 0 0 18px rgba(0,0,0,.25);}
.lr-badge img{width:100%;height:100%;object-fit:cover;border-radius:50%;}
.lr-badge .fallback{font-family:'Fraunces',serif;font-weight:900;font-size:24px;color:#3a140d;letter-spacing:-1px;}
.lr-wm .kicker{font-size:10.5px;letter-spacing:3.2px;color:var(--ox-bright);font-weight:700;
  text-transform:uppercase;margin-bottom:5px;}
.lr-wm h1{font-family:'Fraunces',serif;font-weight:800;font-size:25px;line-height:1;
  color:var(--cream);letter-spacing:.3px;margin:0;}
.lr-wm h1 em{font-style:italic;color:var(--gold-bright);}
.lr-wm .sub{font-size:12.5px;color:var(--muted);margin-top:4px;}
.lr-stamp{font-size:12px;color:var(--muted);text-align:right;line-height:1.5;}
.lr-stamp b{display:block;color:var(--gold-bright);font-weight:700;font-size:13px;}
.lr-stamp .live{display:inline-flex;align-items:center;gap:5px;color:var(--green);}
.lr-stamp .live::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--green);
  box-shadow:0 0 0 3px rgba(63,174,111,.2);}
.lr-divider{height:1px;background:linear-gradient(90deg,var(--line),transparent);margin:6px 0 18px;}

/* ---- KPI cards ---- */
.lr-kpi{position:relative;background:linear-gradient(180deg,var(--panel),var(--bg-2));
  border:1px solid var(--line);border-radius:16px;padding:16px 18px;overflow:hidden;
  box-shadow:var(--shadow);height:100%;}
.lr-kpi::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;}
.lr-kpi.red::before{background:linear-gradient(90deg,var(--ox-bright),transparent);}
.lr-kpi.gold::before{background:linear-gradient(90deg,var(--gold),transparent);}
.lr-kpi.green::before{background:linear-gradient(90deg,var(--green),transparent);}
.lr-kpi.gray::before{background:linear-gradient(90deg,var(--faint),transparent);}
.lr-kpi .v{font-family:'Fraunces',serif;font-size:27px;font-weight:800;letter-spacing:.2px;line-height:1.05;}
.lr-kpi .l{font-size:11.5px;color:var(--muted);margin-top:7px;text-transform:uppercase;
  letter-spacing:.7px;font-weight:600;}
.lr-kpi.red .v{color:var(--ox-bright);} .lr-kpi.gold .v{color:var(--gold-bright);}
.lr-kpi.green .v{color:var(--green);} .lr-kpi.gray .v{color:var(--muted);}
.lr-kpi .h{font-size:10px;color:var(--faint);margin-left:6px;cursor:help;}

/* ---- Sección / títulos de bloque ---- */
.lr-section{font-size:11.5px;text-transform:uppercase;letter-spacing:1.2px;color:var(--faint);
  font-weight:700;margin:18px 0 8px;}

/* ---- Inputs / selects / toggles ---- */
div[data-baseweb="select"] > div{background:var(--bg-2)!important;border-color:var(--line)!important;
  border-radius:11px!important;color:var(--txt)!important;}
.stTextInput input{background:var(--bg-2)!important;border:1px solid var(--line)!important;
  border-radius:11px!important;color:var(--txt)!important;}
.stTextInput input:focus,div[data-baseweb="select"] > div:focus-within{
  border-color:var(--gold)!important;box-shadow:0 0 0 3px rgba(232,163,61,.14)!important;}
label,.stCheckbox label,.stToggle label{color:var(--cream)!important;}

/* ---- Botones ---- */
.stButton button{background:var(--panel-2);border:1px solid var(--line);color:var(--gold);
  border-radius:13px;font-family:'Inter',sans-serif;font-weight:700;transition:.18s;}
.stButton button:hover{border-color:var(--gold);color:var(--gold-bright);
  box-shadow:0 0 0 4px rgba(232,163,61,.12);}
.stLinkButton a,a[data-testid="stBaseLinkButton-secondary"]{
  background:linear-gradient(135deg,#25d366,#117a3d)!important;color:#06210f!important;
  font-weight:800!important;border:none!important;border-radius:13px!important;
  box-shadow:0 8px 22px rgba(37,211,102,.28)!important;}

/* ---- Tablas / data_editor ---- */
div[data-testid="stDataFrame"],div[data-testid="stDataEditor"]{
  border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:var(--shadow);
  background:linear-gradient(180deg,var(--panel),var(--bg-2));}

/* ---- Code block (mensaje WhatsApp) ---- */
div[data-testid="stCode"]{border:1px solid #1f6d43;border-radius:16px;overflow:hidden;}
div[data-testid="stCode"] pre{background:#0c2c1b!important;color:#d8ffe9!important;
  font-family:'Inter',sans-serif!important;}

/* ---- Avisos ---- */
div[data-testid="stAlert"]{border-radius:13px;border:1px solid var(--gold);
  background:rgba(232,163,61,.10);}
</style>
"""


def inyectar_estilos() -> None:
    """Inyecta el CSS global del tema. Llamar una vez tras set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)
