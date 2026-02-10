import json
import re
import hashlib
from datetime import datetime, date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================
# Plotly opcional (NO rompe si falta)
# =========================
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px  # type: ignore

    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Azimut", page_icon="🧭", layout="wide")

BRAND_BLUE = "#00a7ff"
BRAND_YELLOW = "#f9e205"
BRAND_WHITE = "#ffffff"

AZIMUT_FILE = Path("azimutrenovadocompleto.txt")
NEWSLETTERS_FILE = Path("AA-TODAS las newsletters publicadas .txt")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# =========================================================
# IDENTIDAD DE USUARIO (email + clave → archivo aislado)
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


def get_user_storage_paths():
    if not has_identity():
        return None, None
    uid = _hash_identity(st.session_state.user_email, st.session_state.user_key)
    history_file = DATA_DIR / f"history_{uid}.json"
    export_file = DATA_DIR / f"history_export_{uid}.csv"
    return history_file, export_file


# =========================================================
# HISTORIAL (por usuario)
# =========================================================
def load_history():
    history_file, _ = get_user_storage_paths()
    if history_file is None:
        return []
    if history_file.exists():
        try:
            return json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_history(hist):
    history_file, _ = get_user_storage_paths()
    if history_file is None:
        return
    history_file.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


if "historial" not in st.session_state:
    st.session_state.historial = load_history()

# =========================================================
# TEXTO (corpus) — cacheado para que Streamlit Cloud cargue rápido
# =========================================================
@st.cache_data(show_spinner=False)
def load_text_cached(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


AZIMUT_TEXT = load_text_cached(str(AZIMUT_FILE))
NEWS_TEXT = load_text_cached(str(NEWSLETTERS_FILE))


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def unique_preserve(seq):
    seen = set()
    out = []
    for x in seq:
        k = x.strip().lower()
        if k and k not in seen:
            out.append(x.strip())
            seen.add(k)
    return out


@st.cache_data(show_spinner=False)
def extract_emotions_from_azimut_cached(text: str) -> list[str]:
    if not text:
        return []

    emotions = []
    primary_candidates = [
        "Amor",
        "Miedo",
        "Tristeza",
        "Ira",
        "Alegría",
        "Vergüenza",
        "Asco",
        "Sorpresa",
        "Calma",
        "Ilusión",
        "Culpa",
    ]
    for e in primary_candidates:
        if re.search(rf"\b{re.escape(e)}\b", text, flags=re.IGNORECASE):
            emotions.append(e)

    for line in text.splitlines():
        line = line.strip()
        if "," in line and len(line) < 150 and re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line):
            parts = [normalize_space(p) for p in line.split(",")]
            for p in parts:
                if 2 <= len(p) <= 26 and re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$", p):
                    low = p.lower()
                    if low not in {"emoción primaria", "matices", "emociones", "bloque", "semana"}:
                        emotions.append(p[0].upper() + p[1:] if p else p)

    return unique_preserve(emotions)


@st.cache_data(show_spinner=False)
def biases_cached() -> list[str]:
    return unique_preserve(
        [
            "Sesgo de confirmación",
            "Sesgo de negatividad",
            "Sesgo de supervivencia",
            "Falacia de los costes hundidos",
            "Heurística de autoridad",
            "Heurística de disponibilidad",
            "Heurística de representatividad",
            "Heurística de representatividad",
            "Efecto halo",
            "Efecto anclaje",
            "Efecto bandwagon / efecto manada",
            "Disonancia cognitiva",
            "Efecto Dunning-Kruger",
            "Efecto Gell-Mann (amnesia)",
            "Atención selectiva",
            "Sesgo retrospectivo (hindsight bias)",
            "Ilusión de control",
        ]
    )


EMOTIONS = extract_emotions_from_azimut_cached(AZIMUT_TEXT)
BIASES = biases_cached()

# =========================================================
# BRAND / THEME (solo modo claro)
# =========================================================
def apply_theme():
    bg = BRAND_WHITE
    text = "#0b0f1a"
    muted = "#4b5563"
    card_bg = "#ffffff"
    border = "rgba(10,20,40,0.10)"
    input_bg = "rgba(10,20,40,0.03)"

    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {bg};
            color: {text};
          }}

          /* Sidebar azul */
          section[data-testid="stSidebar"] {{
            background: {BRAND_BLUE};
          }}

          /* Título "Azimut" (blanco + subrayado amarillo) */
          .az-sidebar-title {{
            color: #ffffff;
            font-weight: 900;
            font-size: 22px;
            margin: 8px 0 14px 0;
            display: inline-block;
            padding-bottom: 6px;
            border-bottom: 4px solid {BRAND_YELLOW};
            letter-spacing: 0.2px;
          }}

          /* Texto en sidebar por defecto en blanco */
          section[data-testid="stSidebar"] * {{
            color: #ffffff !important;
            font-weight: 600 !important;
          }}

          /* Inputs del sidebar con texto NEGRO */
          section[data-testid="stSidebar"] input,
          section[data-testid="stSidebar"] textarea {{
            color: {text} !important;
            -webkit-text-fill-color: {text} !important;
            caret-color: {text} !important;
          }}
          section[data-testid="stSidebar"] input::placeholder,
          section[data-testid="stSidebar"] textarea::placeholder {{
            color: rgba(11,15,26,0.55) !important;
            -webkit-text-fill-color: rgba(11,15,26,0.55) !important;
          }}

          /* Inputs global */
          input, textarea {{
            color: {text} !important;
            -webkit-text-fill-color: {text} !important;
            caret-color: {text} !important;
          }}

          /* Radio labels */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
            padding: 12px 10px !important;
            margin: 10px 0px !important;
            border-radius: 12px !important;
          }}

          /* Item seleccionado en amarillo */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) span {{
            color: {BRAND_YELLOW} !important;
            font-weight: 900 !important;
          }}

          /* Dot del radio en amarillo */
          section[data-testid="stSidebar"] input[type="radio"] {{
            accent-color: {BRAND_YELLOW} !important;
          }}

          /* Tipografía general */
          .stMarkdown, p, li, span, label, div {{
            color: {text};
          }}

          /* Título de bloque + subrayado */
          h1, h2 {{
            color: {text} !important;
          }}
          h1::after, h2::after {{
            content: "";
            display: block;
            width: 120px;
            height: 4px;
            background: {BRAND_BLUE};
            border-radius: 99px;
            margin-top: 10px;
          }}

          /* Subtítulos internos + subrayado amarillo */
          h3 {{
            color: {text} !important;
            margin-bottom: 10px !important;
          }}
          h3::after {{
            content: "";
            display: block;
            width: 90px;
            height: 4px;
            background: {BRAND_YELLOW};
            border-radius: 99px;
            margin-top: 10px;
          }}

          /* Párrafos con más aire */
          .stMarkdown p {{
            margin-bottom: 18px !important;
            line-height: 1.55 !important;
          }}

          .az-card {{
            background: {card_bg};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 18px 18px 16px 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
          }}
          .az-muted {{
            color: {muted} !important;
          }}
          .az-enunciado {{
            font-weight: 900;
            font-size: 1.02rem;
            margin-top: 10px;
            margin-bottom: 12px;
            color: {text} !important;
          }}
          .az-gap {{
            height: 10px;
          }}

          /* Inputs */
          textarea, input, .stTextInput > div > div > input {{
            background: {input_bg} !important;
          }}

          /* Botones */
          div.stButton > button {{
            background-color: {BRAND_BLUE} !important;
            color: #ffffff !important;
            border: 0px !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            padding: 0.70rem 1.05rem !important;
          }}

          /* Tabs */
          .stTabs [data-baseweb="tab-highlight"] {{
            background-color: {BRAND_BLUE} !important;
          }}
          .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: {text} !important;
          }}

          /* Multiselect tags */
          .stMultiSelect span[data-baseweb="tag"] {{
            background-color: {BRAND_BLUE} !important;
            color: #ffffff !important;
            border: 0px !important;
          }}

          hr {{
            border-color: {border} !important;
          }}

          /* Caja IMPORTANTE en Inicio */
          .az-important {{
            border: 2px solid {BRAND_BLUE};
            border-radius: 16px;
            padding: 14px 16px;
            background: rgba(0, 167, 255, 0.04);
          }}
          .az-important-title {{
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
          }}

          /* ✅ Eliminación agresiva de “bloques vacíos” que aparecen como tarjetas blancas */
          div:empty {{
            display: none !important;
          }}
          section.main > div:empty {{
            display: none !important;
          }}
          [data-testid="stVerticalBlock"] > div:empty {{
            display: none !important;
          }}
          [data-testid="stVerticalBlock"] > div:has(> div:empty) {{
            margin: 0 !important;
            padding: 0 !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme()

# =========================================================
# DF
# =========================================================
def history_df():
    hist = st.session_state.historial
    if not hist:
        return pd.DataFrame(columns=["timestamp", "bloque", "fecha", "concepto", "respuesta", "meta"])
    df = pd.DataFrame(hist)
    for col in ["timestamp", "bloque", "fecha", "concepto", "respuesta", "meta"]:
        if col not in df.columns:
            df[col] = None
    return df


def to_sortable_date(d):
    try:
        return datetime.strptime(d, "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception:
        return None


# =========================================================
# GUARDADO
# =========================================================
def guardar_respuesta(bloque: int, fecha_str: str, concepto: str, respuesta: str, meta: dict | None = None):
    if not has_identity():
        st.warning("Para guardar y ver un historial privado, introduce tu **email** y tu **clave privada** en la barra lateral.")
        return

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": ts,
        "bloque": int(bloque),
        "fecha": fecha_str if fecha_str else "",
        "concepto": concepto,
        "respuesta": respuesta if respuesta else "",
        "meta": meta or {},
    }
    st.session_state.historial.append(entry)
    save_history(st.session_state.historial)
    st.toast(f"✅ Guardado — Bloque {bloque}")


# =========================================================
# UI: navegación + identidad
# =========================================================
st.sidebar.markdown('<div class="az-sidebar-title">Azimut</div>', unsafe_allow_html=True)

with st.sidebar.expander("Privacidad", expanded=True):
    st.markdown("Tu historial es **privado** y depende de tu **email + clave**.")
    user_email_in = st.text_input(
        "Email",
        value=st.session_state.get("user_email", ""),
        help="Email + clave crean tu cuaderno. No enviamos correos: es un identificador local.",
    )
    user_key_in = st.text_input(
        "Clave privada",
        type="password",
        value=st.session_state.get("user_key", ""),
        help="Usa una frase/código difícil de adivinar. Sin esto no se guarda nada.",
    )

st.session_state.user_email = user_email_in
st.session_state.user_key = user_key_in.strip()

current_identity = f"{normalize_email(st.session_state.user_email)}|{normalize_key(st.session_state.user_key)}"
if "last_identity" not in st.session_state:
    st.session_state.last_identity = current_identity

if current_identity != st.session_state.last_identity:
    st.session_state.historial = load_history()
    st.session_state.last_identity = current_identity
    st.rerun()

if not has_identity():
    st.sidebar.info("Introduce **email + clave** para activar tu historial privado.")

MENU_ITEMS = [
    "INICIO",
    "Bloque 1: Vía Negativa",
    "Bloque 2: Aproximación/Retirada",
    "Bloque 3: Arquitectura Emocional",
    "Bloque 4: Raíz y Rama",
    "Bloque 5: Precisión Emocional",
    "Bloque 6: Detector de Sesgos",
    "Bloque 7: El Abogado del Diablo",
    "Bloque 8: Antifragilidad",
    "Bloque 9: El Nuevo Rumbo",
    "📊 MIS RESPUESTAS",
]
menu = st.sidebar.radio("Ir a:", MENU_ITEMS, key="nav_menu")

# =========================================================
# UI helpers
# =========================================================
def card(title: str, subtitle: str | None = None, enunciado: str | None = None):
    st.markdown('<div class="az-card">', unsafe_allow_html=True)
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<div class='az-muted'>{subtitle}</div>", unsafe_allow_html=True)
    if enunciado:
        st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='az-enunciado'>{enunciado}</div>", unsafe_allow_html=True)
        st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def fecha_bloque(bloque: int):
    st.caption("Fecha del registro (manual, para tu seguimiento):")
    key = f"fecha_bloque_{bloque}"
    default = st.session_state.get(key, date.today())
    d = st.date_input("Fecha", value=default, key=key)
    return d.strftime("%d/%m/%Y")


# =========================================================
# PANTALLAS
# =========================================================
df_all = history_df()

if menu == "INICIO":
    card("Azimut", "<b>Cuaderno de navegación: no es para pensar más, es para pensar mejor.</b>")
    st.markdown(
        """
        <p>
        Azimut está diseñado para que avances <b>a tu ritmo</b>: no se trata de hacerlo “rápido” ni de recortar el proceso,
        sino de darte el tiempo que necesites para <b>entrenar habilidades</b>, fortalecer recursos y ensayar formas nuevas
        de afrontar lo que te ocurre.
        </p>

        <p>
        Con esfuerzo y constancia, lo que cambia no es solo lo que escribes: cambia <b>cómo te observas</b>, cómo te regulas
        y qué decisiones eres capaz de sostener cuando el día aprieta.
        </p>

        <p>
        Esta app te aporta una estructura clara para registrar tu proceso con orden (sin depender de papel y boli, sin perder lo que escribiste ayer),
        y para que tus respuestas queden agrupadas por bloques y fechas en <b>“📊 MIS RESPUESTAS”</b>.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="az-important">
          <div class="az-important-title">IMPORTANTE</div>
          <div>
            Para que tu registro sea <b>personal y privado</b>, introduce tu <b>email</b> y una <b>clave privada</b> en la barra lateral.<br><br>

            <b>Paso a paso (sin dudas):</b><br>
            1) Escribe tu <b>email</b> y tu <b>clave privada</b> (solo escribirlos ya sirve; <b>no</b> hace falta pulsar Enter).<br>
            2) Luego completa cualquier bloque y pulsa <b>“Guardar…”</b> (ese botón es lo que guarda tus respuestas).<br>
            3) Ve a <b>“📊 MIS RESPUESTAS”</b> para ver tu historial y evolución.<br><br>

            - Si entras otro día, usa el <b>mismo email</b> y la <b>misma clave</b> para recuperar tu cuaderno.<br>
            - <b>Sin email + clave:</b> la app <u>no guarda</u> y <u>no muestra</u> “Mis respuestas”.<br><br>
            Consejo: usa una frase larga (difícil de adivinar) y guárdala en tu gestor de contraseñas.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    card_end()

elif menu == "Bloque 1: Vía Negativa":
    st.header("Bloque 1: Vía negativa")
    st.write("Antes de añadir soluciones, quita lo que empeora la situación.")
    f = fecha_bloque(1)

    card("Registro del día", subtitle="Menos, pero con impacto.", enunciado="Una frase clara. Sin negociación.")
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?")
    card_end()

    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)

elif menu == "Bloque 2: Aproximación/Retirada":
    st.header("Bloque 2: Aproximación o retirada")
    st.write("Tu cerebro decide primero si acercarse o alejarse.")
    f = fecha_bloque(2)

    card("Registro", subtitle="Dirección conductual del día.", enunciado="Detecta la dirección antes de justificarla.")
    situacion = st.text_input("Situación relevante del día")
    direccion = st.selectbox("¿Te acercaste o te alejaste?", ["Aproximación", "Retirada"])
    utilidad = st.text_area("¿Fue útil esa respuesta? (por qué sí / por qué no)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"situacion": situacion, "utilidad": utilidad}
        guardar_respuesta(2, f, f"Dirección conductual — {direccion}", direccion, meta=meta)

elif menu == "Bloque 3: Arquitectura Emocional":
    st.header("Bloque 3: Arquitectura emocional")
    st.write("No todo lo que sientes es lo mismo. Distinguir capas te da palanca.")
    f = fecha_bloque(3)

    card("Mapa emocional", subtitle="Emoción → sentimiento → clima.", enunciado="Separa capas internas, sin moralina.")
    situacion = st.text_input("Situación del día")
    emocion = st.text_input("Emoción automática (rápida)")
    sentimiento = st.text_input("Sentimiento consciente (cuando lo nombraste)")
    estado = st.text_input("Estado de ánimo de fondo (clima)")
    energia = st.selectbox("Nivel de energía", ["Alto", "Medio", "Bajo"])
    card_end()

    if st.button("Guardar registro"):
        meta = {
            "emocion_automatica": emocion,
            "sentimiento": sentimiento,
            "estado_animo": estado,
            "energia": energia,
        }
        guardar_respuesta(3, f, "Arquitectura emocional — Registro", situacion, meta=meta)

elif menu == "Bloque 4: Raíz y Rama":
    st.header("Bloque 4: Raíz y rama")
    st.write("Toda emoción compleja suele tener una base más simple.")
    f = fecha_bloque(4)

    card(
        "Registro",
        subtitle="Raíz (primaria) → Rama (secundaria).",
        enunciado="Separa la reacción automática de la historia mental.",
    )
    situacion = st.text_input("Situación")
    primaria = st.text_input("Emoción primaria (raíz)")
    secundaria = st.text_input("Emoción secundaria (rama)")
    pensamiento = st.text_area("Pensamiento asociado (la frase interna)", height=90)
    reflexion = st.text_area("Reflexión breve (qué cambió al verlo así)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"primaria": primaria, "secundaria": secundaria, "pensamiento": pensamiento}
        guardar_respuesta(4, f, f"Raíz y rama — {situacion}", reflexion, meta=meta)

elif menu == "Bloque 5: Precisión Emocional":
    st.header("Bloque 5: Precisión emocional")
    st.write("Lo que se nombra, se puede regular.")
    f = fecha_bloque(5)

    card("Registro", subtitle="De ‘mal’ a matiz.", enunciado="Pasa de etiqueta vaga a emoción concreta.")
    situacion = st.text_input("Situación")
    antes = st.text_input("Antes decía que me sentía…")
    precisas = st.text_input("Emociones más precisas (2–5, separadas por comas)")
    cuerpo = st.text_input("¿Dónde lo sentiste en el cuerpo?")
    frase = st.text_area("Frase final de integración (1–3 líneas)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"antes": antes, "precisas": precisas, "cuerpo": cuerpo}
        guardar_respuesta(5, f, f"Precisión emocional — {situacion}", frase, meta=meta)

elif menu == "Bloque 6: Detector de Sesgos":
    st.header("Bloque 6: Detector de sesgos")
    st.write("El piloto automático es eficiente… y a veces tramposo.")
    f = fecha_bloque(6)

    card("Registro", subtitle="Sesgo → pensamiento → alternativa.", enunciado="Detecta el sesgo antes de actuar.")
    sesgo = st.selectbox(
        "Sesgo detectado hoy:",
        BIASES if BIASES else ["Sesgo de confirmación", "Heurística de disponibilidad"],
    )
    situacion = st.text_input("Situación")
    pensamiento = st.text_area("Pensamiento automático", height=90)
    alternativa = st.text_area("Alternativa más realista (o más falsable)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"situacion": situacion, "pensamiento": pensamiento, "alternativa": alternativa}
        guardar_respuesta(6, f, f"Sesgo — {sesgo}", alternativa, meta=meta)

elif menu == "Bloque 7: El Abogado del Diablo":
    st.header("Bloque 7: El abogado del diablo")
    st.write("No es autoataque: es higiene mental.")
    f = fecha_bloque(7)

    card(
        "Registro",
        subtitle="Frase literal → evidencia → nueva formulación.",
        enunciado="Cuando el relato se vuelve dogma, se pincha el globo.",
    )
    creencia = st.text_input("Creencia limitante (literal)")
    evidencia = st.text_area("Evidencia que la contradice (hechos, no deseo)", height=110)
    nueva = st.text_area("Nueva formulación (más realista / más útil)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"evidencia": evidencia}
        guardar_respuesta(7, f, f"Abogado del diablo — {creencia}", nueva, meta=meta)

elif menu == "Bloque 8: Antifragilidad":
    st.header("Bloque 8: Antifragilidad")
    st.write("No romantizamos el caos: lo convertimos en información.")
    f = fecha_bloque(8)

    card("Registro", subtitle="Evento → aprendizaje.", enunciado="El imprevisto ya ocurrió; ahora que te pague en datos.")
    evento = st.text_input("Imprevisto ocurrido")
    habilidad = st.text_input("Qué habilidad entrenaste (aunque no quisieras)")
    distinto = st.text_area("Qué harías distinto si se repite", height=90)
    aprendizaje = st.text_area("Aprendizaje principal (una idea operativa)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"habilidad": habilidad, "distinto": distinto}
        guardar_respuesta(8, f, f"Antifragilidad — {evento}", aprendizaje, meta=meta)

elif menu == "Bloque 9: El Nuevo Rumbo":
    st.header("Bloque 9: El nuevo rumbo")
    st.write("Cierre del recorrido. Integración: pocas ideas, mucha verdad.")
    f = fecha_bloque(9)

    card("¿Qué me llevo de esto?")
    st.write(
        "- Nombrar mis emociones con más precisión (menos niebla).\n"
        "- Detectar antes cuándo entro en piloto automático.\n"
        "- Separar hechos de interpretaciones con más facilidad.\n"
        "- Identificar patrones repetidos (y no discutir con ellos: intervenir).\n"
        "- Regular mejor mi respuesta al estrés (más margen entre estímulo y reacción).\n"
        "- Reconocer creencias rígidas y desactivarlas con evidencia.\n"
        "- Convertir imprevistos en aprendizaje utilizable (antifragilidad práctica).\n"
        "- Tomar decisiones con menos impulsividad y más claridad.\n"
        "- Sostener hábitos pequeños con más consistencia.\n"
        "- Tener un mapa personal de lo que me pasa y cómo lo gestiono."
    )
    card_end()

    card("Integración", subtitle="Síntesis final.", enunciado="Qué cambió, qué aprendiste, qué rumbo sigue.")
    cambio = st.text_area("Qué ha cambiado (concreto)", height=90)
    util = st.text_input("Qué bloque fue más útil")
    dificil = st.text_input("Qué te costó más")
    mejor = st.text_input("Qué gestionas mejor ahora")
    rumbo = st.text_area("Próximo rumbo (una decisión o una regla)", height=90)
    card_end()

    if st.button("Guardar integración"):
        meta = {"bloque_util": util, "dificil": dificil, "mejor": mejor, "rumbo": rumbo}
        guardar_respuesta(9, f, "Integración — Cierre", cambio, meta=meta)
        st.balloons()

elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Mis respuestas")

    if not has_identity():
        st.warning("Introduce tu **email** y tu **clave privada** en la barra lateral para ver tu historial privado.")
        st.stop()

    df = history_df()
    if df.empty:
        st.write("Aún no tienes registros guardados.")
    else:
        df["fecha_sort"] = df["fecha"].apply(lambda x: to_sortable_date(x) if isinstance(x, str) else None)
        df["ts_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["ts_date"] = df["ts_dt"].dt.date

        min_d = df["ts_date"].dropna().min()
        max_d = df["ts_date"].dropna().max()
        if pd.isna(min_d) or pd.isna(max_d):
            min_d = date.today()
            max_d = date.today()

        st.markdown("### Filtros")
        f1, f2, f3 = st.columns([0.5, 0.5, 1.0])
        with f1:
            start = st.date_input("Desde", value=min_d)
        with f2:
            end = st.date_input("Hasta", value=max_d)
        with f3:
            bloques_sel = st.multiselect(
                "Bloques",
                sorted(df["bloque"].dropna().unique().tolist()),
                default=sorted(df["bloque"].dropna().unique().tolist()),
            )

        dff = df[df["bloque"].isin(bloques_sel)].copy()
        dff = dff[(dff["ts_date"].notna()) & (dff["ts_date"] >= start) & (dff["ts_date"] <= end)]

        tab1, tab2, tab3 = st.tabs(["Historial", "Gráficos", "Insights"])

        with tab1:
            st.markdown("### Historial por bloque → por fecha")
            dff2 = dff.sort_values(by=["bloque", "fecha_sort", "timestamp"], ascending=[True, True, True])

            for bloque in sorted(dff2["bloque"].unique()):
                st.subheader(f"Bloque {bloque}")
                bdf = dff2[dff2["bloque"] == bloque].copy()

                bdf["group_date"] = bdf["fecha"].where(bdf["fecha"].astype(str).str.strip() != "", None)
                bdf["group_date"] = bdf["group_date"].fillna(bdf["ts_date"].astype(str))

                for gd in bdf["group_date"].unique():
                    st.markdown(f"#### {gd}")
                    gdf = bdf[bdf["group_date"] == gd]
                    for _, row in gdf.iterrows():
                        card(row.get("concepto", "") or "Registro", subtitle=None)
                        resp = row.get("respuesta", "")
                        if isinstance(resp, str) and resp.strip():
                            st.write(resp)
                        meta = row.get("meta", {})
                        if isinstance(meta, dict) and meta:
                            st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
                            st.caption("Detalles")
                            for k, v in meta.items():
                                if str(v).strip():
                                    st.write(f"**{k.replace('_',' ').capitalize()}:** {v}")
                        card_end()
                        st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("### Visualización de datos")

            daily = dff.dropna(subset=["ts_date"]).groupby("ts_date").size().reset_index(name="registros")
            daily = daily.sort_values("ts_date")

            if PLOTLY_AVAILABLE:
                fig_line = px.line(daily, x="ts_date", y="registros", markers=True, title="Constancia (registros/día)")
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                if len(daily):
                    st.line_chart(daily.set_index("ts_date"))

            by_block = dff.groupby("bloque").size().reindex(range(1, 10), fill_value=0).reset_index(name="registros")
            if PLOTLY_AVAILABLE:
                fig_bar = px.bar(by_block, x="bloque", y="registros", title="Distribución por bloque")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.bar_chart(by_block.set_index("bloque"))

        with tab3:
            st.markdown("### Insights")
            if not dff.empty:
                top_block = int(dff["bloque"].value_counts().index[0])
                top_day = dff.groupby("ts_date").size().sort_values(ascending=False).head(1)
                top_day_str = str(top_day.index[0]) if len(top_day) else "—"

                c1, c2 = st.columns(2)
                with c1:
                    card("Patrones", enunciado="Lo que se repite, manda.")
                    st.write(f"**Bloque más usado:** {top_block}")
                    st.write(f"**Día más activo:** {top_day_str}")
                    card_end()
                with c2:
                    card("Regla mínima viable", enunciado="Adherencia: el músculo que manda.")
                    st.write("Si hoy estás sin gasolina: 1 bloque. Si estás bien: 2. Si estás brillante: repite mañana.")
                    card_end()
            else:
                st.write("Sin datos en el rango filtrado.")

        st.write("")
        c1, c2, c3 = st.columns([0.45, 0.35, 0.2])
        with c1:
            _, export_file = get_user_storage_paths()
            export_path = export_file if export_file is not None else (DATA_DIR / "history_export.csv")

            export_cols = ["timestamp", "bloque", "fecha", "concepto", "respuesta", "meta"]
            dff_export = dff.copy()[export_cols]
            dff_export.to_csv(export_path, index=False, encoding="utf-8")
            st.download_button(
                "Descargar CSV (filtrado)",
                data=export_path.read_bytes(),
                file_name="azimut_historial_filtrado.csv",
            )
        with c2:
            with st.expander("Ver tabla completa (debug)"):
                show = dff.drop(columns=["fecha_sort"], errors="ignore")
                st.dataframe(show, use_container_width=True)
        with c3:
            if st.button("Limpiar historial"):
                st.session_state.historial = []
                save_history([])
                st.rerun()
