import json
import re
import hashlib
from datetime import datetime, date
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

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# =========================================================
# IDENTIDAD DE USUARIO
# =========================================================
def normalize_email(s: str) -> str:
    return (s or "").strip().lower()


def normalize_key(s: str) -> str:
    return (s or "").strip()


def has_identity() -> bool:
    email = normalize_email(st.session_state.get("user_email", ""))
    key = normalize_key(st.session_state.get("user_key", ""))
    return bool(email) and bool(key)


def _hash_identity(email: str, user_key: str) -> str:
    raw = f"{normalize_email(email)}:{normalize_key(user_key)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def get_user_history_file():
    if not has_identity():
        return None
    uid = _hash_identity(st.session_state.user_email, st.session_state.user_key)
    return DATA_DIR / f"history_{uid}.json"


# =========================================================
# HISTORIAL
# =========================================================
def load_history():
    path = get_user_history_file()
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def save_history(hist):
    path = get_user_history_file()
    if path:
        path.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


if "historial" not in st.session_state:
    st.session_state.historial = []


# =========================================================
# ESTILOS
# =========================================================
st.markdown(
    f"""
<style>
.stApp {{
    background: {BRAND_WHITE};
}}

section[data-testid="stSidebar"] {{
    background: {BRAND_BLUE};
}}

section[data-testid="stSidebar"] * {{
    color: white !important;
}}

input, textarea {{
    color: black !important;
}}

.az-card {{
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(0,0,0,0.08);
}}

.az-important {{
    border: 2px solid {BRAND_BLUE};
    border-radius: 16px;
    padding: 16px;
    margin-top: 15px;
}}

.az-important-title {{
    font-weight: 900;
    margin-bottom: 10px;
}}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Azimut")

with st.sidebar.expander("Privacidad", expanded=True):
    st.session_state.user_email = st.text_input("Email")
    st.session_state.user_key = st.text_input("Clave privada", type="password")

if has_identity():
    st.session_state.historial = load_history()

menu = st.sidebar.radio(
    "Ir a:",
    [
        "INICIO",
        "Bloque 1",
        "Bloque 2",
        "Bloque 3",
        "Bloque 4",
        "Bloque 5",
        "Bloque 6",
        "Bloque 7",
        "Bloque 8",
        "Bloque 9",
        "📊 MIS RESPUESTAS",
    ],
)

# =========================================================
# FUNCIONES
# =========================================================
def guardar_respuesta(bloque, fecha, texto):
    if not has_identity():
        st.warning("Introduce tu email y clave primero.")
        return
    entry = {
        "bloque": bloque,
        "fecha": fecha,
        "texto": texto,
        "timestamp": datetime.now().isoformat(),
    }
    st.session_state.historial.append(entry)
    save_history(st.session_state.historial)
    st.success("Guardado.")


def fecha_input():
    return st.date_input("Fecha", value=date.today()).strftime("%d/%m/%Y")


# =========================================================
# PANTALLAS
# =========================================================
if menu == "INICIO":
    st.markdown('<div class="az-card">', unsafe_allow_html=True)
    st.markdown("### **Cuaderno de navegación: no es para pensar más, es para pensar mejor.**")

    st.write(
        """
Azimut está diseñado para que avances a tu ritmo.  
No se trata de hacerlo rápido, sino de darte el tiempo que necesites para entrenar habilidades, ganar recursos y aprender a responder de forma diferente a lo que te ocurre.

Con esfuerzo y constancia, lo que cambia no es solo lo que escribes: cambia cómo te observas y qué decisiones puedes sostener.

Esta app te da una estructura clara para registrar tu proceso sin depender de papel y boli, manteniendo tus reflexiones ordenadas y accesibles.
"""
    )

    st.markdown(
        """
<div class="az-important">
<div class="az-important-title">IMPORTANTE</div>
Para que tus respuestas se guarden en tu cuaderno privado:

<b>1. Escribe tu email y tu clave en la barra lateral.</b><br>
<b>2. No tienes que pulsar Enter ni ningún botón.</b><br>
<b>3. Después, simplemente usa los bloques y pulsa "Guardar".</b><br><br>

Tu historial quedará asociado a ese email + clave.  
Cuando vuelvas a entrar, introduce los mismos datos y verás tus registros.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# BLOQUES
# =========================================================
elif menu.startswith("Bloque"):
    bloque = int(menu.split(" ")[1])
    st.header(menu)

    fecha = fecha_input()
    texto = st.text_area("Escribe tu registro", height=150)

    if st.button("Guardar"):
        guardar_respuesta(bloque, fecha, texto)

# =========================================================
# MIS RESPUESTAS
# =========================================================
elif menu == "📊 MIS RESPUESTAS":
    st.title("Mis respuestas")

    if not has_identity():
        st.warning("Introduce tu email y clave para ver tus registros.")
        st.stop()

    if not st.session_state.historial:
        st.write("Aún no hay registros.")
    else:
        for r in reversed(st.session_state.historial):
            st.markdown('<div class="az-card">', unsafe_allow_html=True)
            st.write(f"**Bloque {r['bloque']} — {r['fecha']}**")
            st.write(r["texto"])
            st.markdown("</div>", unsafe_allow_html=True)
