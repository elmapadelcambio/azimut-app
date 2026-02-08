import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Azimut", page_icon="🧭", layout="wide")

BRAND_BLUE = "#00a7ff"
BRAND_YELLOW = "#f9e205"
BRAND_WHITE = "#ffffff"
DARK_BG = "#0e1117"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

# =========================================================
# SESSION STATE
# =========================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# =========================================================
# STYLES
# =========================================================
bg_color = DARK_BG if st.session_state.dark_mode else BRAND_WHITE
text_color = "white" if st.session_state.dark_mode else "black"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg_color};
        color: {text_color};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {BRAND_BLUE};
        padding-top: 20px;
    }}

    .sidebar-title {{
        color: {BRAND_YELLOW};
        font-weight: bold;
        margin-bottom: 20px;
        font-size: 20px;
    }}

    .nav-block {{
        margin-bottom: 18px;
        line-height: 1.2;
    }}

    .nav-block-number {{
        color: {BRAND_YELLOW};
        font-weight: bold;
    }}

    .nav-block-name {{
        color: white;
        margin-left: 4px;
    }}

    .title-block {{
        font-size: 34px;
        font-weight: 700;
        color: black;
        border-bottom: 4px solid {BRAND_BLUE};
        display: inline-block;
        padding-bottom: 6px;
        margin-bottom: 25px;
    }}

    .section-title {{
        font-size: 22px;
        font-weight: 600;
        color: black;
        border-bottom: 3px solid {BRAND_YELLOW};
        display: inline-block;
        padding-bottom: 4px;
        margin-top: 30px;
        margin-bottom: 10px;
    }}

    .instruction {{
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        color: black;
    }}

    .card {{
        background: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}

    .big-insight {{
        background: #f5fbff;
        padding: 20px;
        border-radius: 14px;
        border-left: 6px solid {BRAND_BLUE};
        margin-bottom: 20px;
    }}

    .moon-btn {{
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: {BRAND_YELLOW};
        border-radius: 50%;
        padding: 10px;
        font-size: 18px;
        cursor: pointer;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# DATA
# =========================================================
def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


history = load_history()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown(
    "<div class='sidebar-title'>🧭 Programa Azimut</div>",
    unsafe_allow_html=True,
)

pages = [
    ("Inicio", "Inicio"),
    ("Bloque 1", "Vía negativa"),
    ("Bloque 2", "Ritmos circadianos"),
    ("Bloque 3", "Marcadores somáticos"),
    ("Bloque 4", "Registro de precisión"),
    ("Bloque 5", "Gestión de recursos"),
    ("Bloque 6", "Detector de sesgos"),
    ("Bloque 7", "El abogado del diablo"),
    ("Bloque 8", "Antifragilidad"),
    ("Bloque 9", "El nuevo rumbo"),
    ("Mis respuestas", ""),
]

page_names = [p[0] for p in pages]
page = st.sidebar.radio("", page_names)

# Moon toggle
if st.sidebar.button("🌙"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# =========================================================
# PAGES
# =========================================================
def page_inicio():
    st.markdown("<div class='title-block'>Inicio</div>", unsafe_allow_html=True)

    st.markdown(
        """
Esta app es tu cuaderno de trabajo dentro del programa Azimut.

Cada día puedes ir rellenando los bloques que correspondan.  
Con el paso del tiempo verás que identificas mejor lo que te ocurre, y tus respuestas se vuelven más precisas. Esa mayor claridad será evidencia de tu progreso.

Todas tus respuestas se guardan en **“Mis respuestas”**, donde podrás observar patrones, repeticiones y evolución.

El Bloque 9 está pensado para el final del recorrido.
"""
    )

    st.markdown("### Acceso rápido a bloques")

    cols = st.columns(3)
    for i in range(1, 9):
        with cols[(i - 1) % 3]:
            if st.button(f"Ir a Bloque {i}"):
                st.session_state.page = f"Bloque {i}"


def page_bloque(titulo):
    st.markdown(f"<div class='title-block'>{titulo}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='instruction'>Completa el registro correspondiente a este bloque.</div>",
        unsafe_allow_html=True,
    )

    fecha = st.date_input("Fecha", date.today())
    texto = st.text_area("Escribe tu registro")

    if st.button("Guardar registro"):
        history.append(
            {
                "fecha": str(fecha),
                "bloque": titulo,
                "texto": texto,
            }
        )
        save_history(history)
        st.toast("Registro guardado")


def page_respuestas():
    st.markdown("<div class='title-block'>📊 Mis respuestas</div>", unsafe_allow_html=True)

    if not history:
        st.info("Aún no hay registros.")
        return

    df = pd.DataFrame(history)
    df["fecha"] = pd.to_datetime(df["fecha"])

    st.markdown("<div class='section-title'>Gráficos</div>", unsafe_allow_html=True)
    counts = df.groupby("fecha").size().reset_index(name="registros")
    fig = px.line(counts, x="fecha", y="registros")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Historial</div>", unsafe_allow_html=True)

    for _, row in df.sort_values("fecha", ascending=False).iterrows():
        st.markdown(
            f"""
            <div class='card'>
                <strong>{row['fecha'].date()}</strong> — {row['bloque']}<br>
                {row['texto']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class='big-insight'>
        <h4>Detección de patrones</h4>
        <p><strong>Emoción dominante:</strong> Ansiedad</p>
        <p><strong>Contexto recurrente:</strong> —</p>
        </div>

        <div class='big-insight'>
        <h4>Recomendaciones dinámicas</h4>
        <ul>
        <li>Vuelve al Bloque 2 hoy.</li>
        <li>Haz Bloque 3 para reducir ruido corporal.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ROUTER
# =========================================================
if page == "Inicio":
    page_inicio()
elif page == "Mis respuestas":
    page_respuestas()
else:
    page_bloque(page)
