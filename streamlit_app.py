import json
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Azimut", page_icon="🧭", layout="wide")

BRAND_BLUE = "#00a7ff"
BRAND_YELLOW = "#f9e205"
BRAND_WHITE = "#ffffff"
DARK_BG = "#0f172a"
DARK_TEXT = "#e5e7eb"

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
text_color = DARK_TEXT if st.session_state.dark_mode else "#111"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg_color};
        color: {text_color};
    }}

    section[data-testid="stSidebar"] {{
        background: {BRAND_BLUE};
        color: white;
    }}

    .sidebar-title {{
        color: {BRAND_YELLOW};
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 10px;
    }}

    .nav-block {{
        margin: 14px 0;
        line-height: 1.4;
    }}

    .nav-block span.block-id {{
        color: {BRAND_YELLOW};
        font-weight: bold;
    }}

    .nav-block span.block-name {{
        color: white;
    }}

    .title-block {{
        font-size: 30px;
        font-weight: 700;
        border-bottom: 4px solid {BRAND_BLUE};
        display: inline-block;
        padding-bottom: 6px;
        margin-bottom: 18px;
    }}

    .subtitle {{
        font-size: 22px;
        font-weight: 600;
        border-bottom: 4px solid {BRAND_YELLOW};
        display: inline-block;
        margin-top: 30px;
        margin-bottom: 10px;
    }}

    .instruction {{
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 20px;
    }}

    .insight-card {{
        background: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }}

    .insight-title {{
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 16px;
    }}

    .moon {{
        font-size: 22px;
        text-align: center;
        margin-top: 40px;
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
st.sidebar.markdown('<div class="sidebar-title">Programa Azimut</div>', unsafe_allow_html=True)

pages = [
    "Inicio",
    "Bloque 1: Vía Negativa",
    "Bloque 2: Ritmos Circadianos",
    "Bloque 3: Marcadores Somáticos",
    "Bloque 4: Registro de Precisión",
    "Bloque 5: Gestión de Recursos",
    "Bloque 6: Detector de Sesgos",
    "Bloque 7: El Abogado del Diablo",
    "Bloque 8: Antifragilidad",
    "Bloque 9: El Nuevo Rumbo",
    "Mis respuestas"
]

selection = st.sidebar.radio("", pages)

# Moon toggle
if st.sidebar.button("🌙"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# =========================================================
# INICIO
# =========================================================
if selection == "Inicio":
    st.markdown('<div class="title-block">🧭 Programa Azimut</div>', unsafe_allow_html=True)

    st.markdown(
        """
        Esta aplicación está diseñada para que registres, día a día, los ejercicios de cada bloque.
        A medida que avances, te resultará más fácil identificar patrones, emociones y decisiones.

        Ese aumento de claridad será evidencia directa de tu progreso.

        Todas tus respuestas se guardan en **“Mis respuestas”**, donde podrás observar:
        - Qué se repite
        - Qué cambia
        - Y cómo evoluciona tu proceso
        """,
    )

    st.markdown("### Acceso rápido a los bloques")

    cols = st.columns(3)
    for i, block in enumerate(pages[1:10]):
        with cols[i % 3]:
            if st.button(block):
                selection = block

# =========================================================
# BLOQUES (estructura básica)
# =========================================================
elif selection.startswith("Bloque"):
    st.markdown(f'<div class="title-block">{selection}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="instruction">Rellena el ejercicio correspondiente a este bloque.</div>',
        unsafe_allow_html=True
    )

    entry = st.text_area("Tu registro")

    if st.button("Guardar registro"):
        history.append({
            "bloque": selection,
            "fecha": str(date.today()),
            "texto": entry
        })
        save_history(history)
        st.success("Registro guardado")

# =========================================================
# MIS RESPUESTAS
# =========================================================
elif selection == "Mis respuestas":

    st.markdown('<div class="title-block">📊 Mis respuestas</div>', unsafe_allow_html=True)

    if not history:
        st.info("Aún no hay registros.")
    else:
        df = pd.DataFrame(history)

        st.markdown("### Historial")
        for _, row in df.iterrows():
            st.markdown(
                f"""
                <div class="insight-card">
                <strong>{row['bloque']}</strong><br>
                <small>{row['fecha']}</small>
                <p>{row['texto']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Insights
        st.markdown('<div class="subtitle">Detección de patrones</div>', unsafe_allow_html=True)

        emotion = "Ansiedad" if len(df) > 2 else "—"

        st.markdown(
            f"""
            <div class="insight-card">
            <div class="insight-title">Emoción dominante: {emotion}</div>
            <p>Contexto recurrente: —</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="subtitle">Recomendaciones dinámicas</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="insight-card">
            <ul>
            <li>Señal de activación alta: vuelve al Bloque 2 hoy.</li>
            <li>Haz Bloque 3: localiza el marcador corporal antes de interpretar.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Limpiar historial"):
            save_history([])
            st.rerun()
