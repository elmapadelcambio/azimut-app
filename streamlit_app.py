import json
import re
from datetime import datetime, date
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
HISTORY_FILE = DATA_DIR / "history.json"

# =========================================================
# SESIÓN: modo oscuro + historial
# =========================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_history(hist):
    HISTORY_FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")

if "historial" not in st.session_state:
    st.session_state.historial = load_history()

# =========================================================
# TEXTO (corpus)
# =========================================================
def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

AZIMUT_TEXT = load_text(AZIMUT_FILE)
NEWS_TEXT = load_text(NEWSLETTERS_FILE)

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

# =========================================================
# EXTRACCIONES
# =========================================================
def extract_emotions_from_azimut(text: str) -> list[str]:
    if not text:
        return []
    emotions = []
    primary_candidates = [
        "Amor", "Miedo", "Tristeza", "Ira", "Alegría", "Vergüenza",
        "Asco", "Sorpresa", "Calma", "Ilusión", "Culpa",
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

EMOTIONS = extract_emotions_from_azimut(AZIMUT_TEXT)

def circadian_checklist_from_corpus(_azimut: str, _news: str) -> list[str]:
    return [
        "Me acuesto y me levanto a horas consistentes",
        "Dormitorio fresco, oscuro y silencioso",
        "Evito pantallas/luz intensa antes de dormir",
        "Rutina de aterrizaje nocturno",
        "Luz natural al inicio del día",
        "Movimiento temprano",
        "Café cuando ya he arrancado",
        "Ceno con margen antes de dormir",
        "Luz brillante solo de día",
        "Si hago siesta, que sea corta",
        "Contacto con el exterior",
        "Coherencia entre luz, comida y actividad",
    ][:12]

CHECKLIST_BLOCK2 = circadian_checklist_from_corpus(AZIMUT_TEXT, NEWS_TEXT)

def biases_from_corpus(_news: str, _azimut: str) -> list[str]:
    return unique_preserve([
        "Sesgo de confirmación", "Sesgo de negatividad", "Sesgo de supervivencia",
        "Falacia de los costes hundidos", "Heurística de autoridad",
        "Heurística de disponibilidad", "Heurística de representatividad",
        "Efecto halo", "Efecto anclaje", "Efecto bandwagon",
        "Disonancia cognitiva", "Efecto Dunning-Kruger", "Efecto Gell-Mann",
        "Atención selectiva", "Sesgo retrospectivo", "Ilusión de control",
    ])

BIASES = biases_from_corpus(NEWS_TEXT, AZIMUT_TEXT)

def limiting_beliefs_examples(_news: str, _azimut: str) -> list[str]:
    return unique_preserve([
        "“No puedo.”", "“Debo tener control sobre todo.”", "“Tengo que ser bueno.”",
        "“No debo fallar.”", "“No debo decepcionar.”",
        "“He fallado, por tanto, no valgo.”", "“Es lo que hay.”",
    ])

BELIEF_EXAMPLES = limiting_beliefs_examples(NEWS_TEXT, AZIMUT_TEXT)

def azimut_benefits(_news: str, _azimut: str) -> list[str]:
    return unique_preserve([
        "Entender tus emociones", "Regular tu respuesta al estrés",
        "Cultivar atención y calma", "Tomar decisiones con claridad",
        "Reconocer patrones", "Mejorar tolerancia a incertidumbre",
        "Aumentar capacidad de parar", "Reencuadrar narrativas",
        "Construir consistencia", "Identificar sesgos",
    ])

BENEFITS_BLOCK9 = azimut_benefits(NEWS_TEXT, AZIMUT_TEXT)

# =========================================================
# THEME / BRAND CSS
# =========================================================
def apply_theme(dark: bool):
    if dark:
        bg = "#0b1220"
        text = "#e9eef7"
        muted = "#b8c2d6"
        card = "#101a2b"
        border = "rgba(255,255,255,0.10)"
        main_title = "#e9eef7"
        section_title = "#e9eef7"
        instruction = "#e9eef7"
    else:
        bg = BRAND_WHITE
        text = "#0b0f1a"
        muted = "#4b5563"
        card = "#ffffff"
        border = "rgba(10,20,40,0.10)"
        main_title = "#0b0f1a"
        section_title = "#0b0f1a"
        instruction = "#0b0f1a"

    st.markdown(
        f"""
        <style>
          /* Base */
          .stApp {{
            background: {bg};
            color: {text};
          }}
          .stMarkdown, p, li, span {{ color: {text}; }}

          /* Sidebar azul fijo */
          section[data-testid="stSidebar"] {{
            background: {BRAND_BLUE};
          }}

          /* Título Azimut Personalizado */
          .az-sidebar-title {{
            color: #ffffff;
            font-size: 2.2rem;
            font-weight: 900;
            border-bottom: 4px solid {BRAND_YELLOW};
            padding-bottom: 4px;
            margin-bottom: 30px;
            display: inline-block;
            line-height: 1.1;
          }}

          /* Radio dot (marca) */
          section[data-testid="stSidebar"] input[type="radio"] {{
            accent-color: {BRAND_YELLOW} !important;
          }}

          /* Separación visual entre items del menú */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
            padding: 12px 10px !important;
            margin: 9px 0px !important;
            border-radius: 14px !important;
          }}

          /* Texto del menú */
          /* Base (segunda línea) blanca */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label span {{
            color: #ffffff !important;
            font-weight: 600 !important;
            line-height: 1.35 !important;
            white-space: pre-line !important;
          }}
          /* Primera línea (BLOQUE X) amarilla */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label span::first-line {{
            color: {BRAND_YELLOW} !important;
            font-weight: 900 !important;
            font-size: 1.05em !important;
            letter-spacing: 0.5px !important;
          }}

          /* Cards */
          .az-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
          }}
          .az-muted {{ color: {muted} !important; }}

          /* Botones (Letra blanca) */
          div.stButton > button {{
            background-color: {BRAND_BLUE} !important;
            color: #ffffff !important;
            border: 0px !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            padding: 0.65rem 1.05rem !important;
          }}

          /* Pestañas (Tabs) - Línea azul */
          div[data-testid="stTabs"] button[aria-selected="true"] {{
             color: {BRAND_BLUE} !important;
             border-bottom-color: {BRAND_BLUE} !important;
          }}
          div[data-testid="stTabs"] button:hover {{
             color: {BRAND_BLUE} !important;
          }}

          /* Títulos de bloque y sección */
          .az-block-title {{
            font-size: 2.1rem;
            font-weight: 900;
            color: {main_title};
            margin: 0.2rem 0 0.2rem 0;
          }}
          .az-block-underline {{
            height: 4px;
            width: 120px;
            background: {BRAND_BLUE};
            border-radius: 999px;
            margin: 0.2rem 0 1.2rem 0;
          }}

          .az-section-title {{
            font-size: 1.4rem;
            font-weight: 900;
            color: {section_title};
            margin: 0.8rem 0 0.15rem 0;
            display: inline-block;
            padding-bottom: 6px;
            border-bottom: 4px solid {BRAND_YELLOW};
          }}

          .az-instruction {{
            font-weight: 800;
            color: {instruction};
            margin-top: 0.25rem;
          }}

          /* Panel Stats */
          .az-panel {{
            background: {card};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 18px;
          }}
          .az-statbar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
          }}
          .az-stat {{
            flex: 1 1 220px;
            border: 1px solid {border};
            background: {card};
            border-radius: 14px;
            padding: 14px;
          }}
          /* Caja azul para el contador principal */
          .az-stat-primary {{
            flex: 1 1 220px;
            background: {BRAND_BLUE};
            border-radius: 14px;
            padding: 14px;
            color: #ffffff;
          }}
          .az-stat-primary .k {{
             font-size: 0.78rem; font-weight: 900; color: rgba(255,255,255,0.8); text-transform: uppercase;
          }}
          .az-stat-primary .v {{
             font-size: 1.8rem; font-weight: 950; margin-top: 0.2rem; color: #ffffff;
          }}

          .az-stat .k {{
            font-size: 0.78rem;
            font-weight: 900;
            color: {muted};
            letter-spacing: 0.2px;
            text-transform: uppercase;
          }}
          .az-stat .v {{
            font-size: 1.5rem;
            font-weight: 950;
            margin-top: 0.2rem;
            color: {BRAND_BLUE};
          }}

          /* Sidebar bottom moon (Discreta) */
          .az-sidebar-bottom {{
            position: fixed;
            bottom: 10px;
            left: 10px;
            z-index: 9999;
          }}
          .az-sidebar-bottom button {{
            width: 38px !important;
            height: 38px !important;
            border-radius: 8px !important;
            border: none !important;
            background: transparent !important; /* Se funde con la barra */
            color: rgba(255,255,255,0.6) !important;
            font-size: 16px !important;
            box-shadow: none !important;
            padding: 0px !important;
          }}
          .az-sidebar-bottom button:hover {{
            background: rgba(255,255,255,0.1) !important;
            color: #ffffff !important;
          }}

          /* Evitar "cajas" vacías estilo input sin label */
          .stTextInput label:empty, .stTextArea label:empty {{
            display: none !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_theme(st.session_state.dark_mode)

# =========================================================
# Sidebar - Título personalizado y Botón Luna
# =========================================================
# Título
st.sidebar.markdown('<div class="az-sidebar-title">Azimut</div>', unsafe_allow_html=True)

# Botón Luna (Abajo izquierda)
st.sidebar.markdown('<div class="az-sidebar-bottom">', unsafe_allow_html=True)
if st.sidebar.button("🌙", key="moon_toggle_sidebar", help="Modo oscuro"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# DF + analítica
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

def dominant_emotion_and_context(df: pd.DataFrame):
    d4 = df[df["bloque"] == 4].copy()
    emotion = None
    context = None
    if len(d4):
        emo = d4["respuesta"].fillna("").astype(str).str.strip()
        emo = emo[emo != ""]
        if len(emo):
            emotion = emo.value_counts().index[0]
        
        def meta_where(x):
            if isinstance(x, dict):
                return str(x.get("donde", "")).strip()
            return ""
        
        where = d4["meta"].apply(meta_where)
        where = where[where != ""]
        if len(where):
            context = where.value_counts().index[0]
    return emotion, context

def recommendations(dominant_emotion: str | None):
    if not dominant_emotion:
        return [
            "Registra 2–3 días en el Bloque 4 para que aparezca señal.",
            "Si hoy estás dispersa: Bloque 2 (ritmo) suele ser la palanca de bajo coste.",
        ]
    e = dominant_emotion.lower()
    if any(k in e for k in ["ans", "mied", "pavor", "inquiet", "nerv", "estrés"]):
        return [
            "Señal de activación alta: vuelve al Bloque 2 (anclas circadianas) hoy.",
            "Haz Bloque 3: localiza el marcador corporal para bajar el ‘ruido’.",
        ]
    if any(k in e for k in ["trist", "melanc", "vacío"]):
        return [
            "Si baja la energía: Bloque 5 (recurso) en formato mínimo viable.",
            "Bloque 1: elimina una fricción concreta hoy.",
        ]
    if any(k in e for k in ["ira", "rab", "indign", "enfado"]):
        return [
            "Si hay fricción social: Bloque 7 (abogado del diablo).",
            "Bloque 3: identifica dónde se carga el cuerpo antes de responder.",
        ]
    return [
        "Hoy: Bloque 4 + Bloque 5 (claridad + recurso).",
        "Si detectas automatismos: Bloque 6 como lupa.",
    ]

# =========================================================
# GUARDADO
# =========================================================
def guardar_respuesta(bloque: int, fecha_str: str, concepto: str, respuesta: str, meta: dict | None = None):
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
# UI helpers
# =========================================================
def block_title(title: str):
    st.markdown(f'<div class="az-block-title">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="az-block-underline"></div>', unsafe_allow_html=True)

def section_title(title: str):
    st.markdown(f'<div class="az-section-title">{title}</div>', unsafe_allow_html=True)

def instruction(text: str):
    st.markdown(f'<div class="az-instruction">{text}</div>', unsafe_allow_html=True)

def card(title: str, subtitle: str | None = None):
    st.markdown('<div class="az-card">', unsafe_allow_html=True)
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<div class='az-muted'>{subtitle}</div>", unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def goto(item: str):
    st.session_state["nav_menu"] = item
    st.rerun()

def fecha_bloque(bloque: int):
    st.caption("Fecha del registro (manual, para tu seguimiento):")
    key = f"fecha_bloque_{bloque}"
    default = st.session_state.get(key, date.today())
    d = st.date_input("Fecha", value=default, key=key)
    return d.strftime("%d/%m/%Y")

# =========================================================
# NAVEGACIÓN
# =========================================================
MENU_ITEMS = [
    "INICIO",
    "BLOQUE 1\nVía Negativa",
    "BLOQUE 2\nRitmos Circadianos",
    "BLOQUE 3\nMarcadores Somáticos",
    "BLOQUE 4\nRegistro de Precisión",
    "BLOQUE 5\nGestión de Recursos",
    "BLOQUE 6\nDetector de Sesgos",
    "BLOQUE 7\nEl Abogado del Diablo",
    "BLOQUE 8\nAntifragilidad",
    "BLOQUE 9\nEl Nuevo Rumbo",
    "📊 MIS RESPUESTAS",
]
menu = st.sidebar.radio("Ir a:", MENU_ITEMS, key="nav_menu", label_visibility="collapsed")

# =========================================================
# PANTALLAS
# =========================================================
df_all = history_df()

# ---------- INICIO ----------
if menu == "INICIO":
    block_title("Azimut")
    card("Cómo usar esta app", None)
    st.write(
        "La idea es sencilla: **cada día** completas el bloque que te toque. "
        "Con los días notarás algo concreto: **identificarás antes lo que te pasa**, "
        "y tus explicaciones tendrán más precisión.\n\n"
        "Tus respuestas se guardan en **“📊 MIS RESPUESTAS”**.\n\n"
        "Deja **“Bloque 9”** para el cierre del programa."
    )
    card_end()
    
    st.write("")
    card("Accesos rápidos", None)
    b1, b2, b3 = st.columns(3)
    if b1.button("Bloque 1"): goto("BLOQUE 1\nVía Negativa")
    if b2.button("Bloque 2"): goto("BLOQUE 2\nRitmos Circadianos")
    if b3.button("Bloque 3"): goto("BLOQUE 3\nMarcadores Somáticos")
    
    b4, b5, b6 = st.columns(3)
    if b4.button("Bloque 4"): goto("BLOQUE 4\nRegistro de Precisión")
    if b5.button("Bloque 5"): goto("BLOQUE 5\nGestión de Recursos")
    if b6.button("Bloque 6"): goto("BLOQUE 6\nDetector de Sesgos")
    
    b7, b8, b9 = st.columns(3)
    if b7.button("Bloque 7"): goto("BLOQUE 7\nEl Abogado del Diablo")
    if b8.button("Bloque 8"): goto("BLOQUE 8\nAntifragilidad")
    if b9.button("Bloque 9"): goto("BLOQUE 9\nEl Nuevo Rumbo")
    card_end()

# ---------- BLOQUE 1 ----------
elif menu == "BLOQUE 1\nVía Negativa":
    block_title("Bloque 1: Vía Negativa")
    instruction("Identifica lo que resta. Hoy no añadimos herramientas: quitamos lastre.")
    f = fecha_bloque(1)
    section_title("Registro del día")
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?", label_visibility="visible")
    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)

# ---------- BLOQUE 2 ----------
elif menu == "BLOQUE 2\nRitmos Circadianos":
    block_title("Bloque 2: Ritmos circadianos")
    instruction("Marca los puntos que has cumplido hoy.")
    f = fecha_bloque(2)
    section_title("Checklist")
    seleccionados = []
    for i, item in enumerate(CHECKLIST_BLOCK2):
        if st.checkbox(item, key=f"b2_{i}"):
            seleccionados.append(item)
    if st.button("Guardar registro"):
        guardar_respuesta(2, f, "Ritmos circadianos — Hitos", ", ".join(seleccionados))

# ---------- BLOQUE 3 ----------
elif menu == "BLOQUE 3\nMarcadores Somáticos":
    block_title("Bloque 3: Marcadores somáticos")
    instruction("El cuerpo habla en dialectos. Vamos a transcribirlo.")
    f = fecha_bloque(3)
    section_title("Mapa corporal")
    zona = st.selectbox("¿Dónde lo sientes?", ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros", "Cabeza", "Espalda", "Manos", "Piernas"])
    tipo = st.text_input("Describe la sensación (calor, nudo, presión...):")
    if st.button("Guardar registro"):
        guardar_respuesta(3, f, f"Marcador somático — Localización: {zona}", tipo)

# ---------- BLOQUE 4 ----------
elif menu == "BLOQUE 4\nRegistro de Precisión":
    block_title("Bloque 4: Registro de precisión")
    instruction("El objetivo no es ‘sentir menos’, sino **nombrar mejor**.")
    f = fecha_bloque(4)
    section_title("Registro diario")
    emo = st.selectbox("Emoción detectada:", EMOTIONS if EMOTIONS else ["Ansiedad", "Paz"])
    por_que = st.text_area("¿Por qué crees que era esa emoción?")
    donde = st.text_input("¿Dónde estabas?")
    que_paso = st.text_area("¿Qué pasó para sentir eso?")
    if st.button("Guardar registro"):
        meta = {"por_que": por_que, "donde": donde, "que_paso": que_paso}
        guardar_respuesta(4, f, "Precisión emocional — Etiquetado", emo, meta=meta)

# ---------- BLOQUE 5 ----------
elif menu == "BLOQUE 5\nGestión de Recursos":
    block_title("Bloque 5: Gestión de recursos")
    instruction("Un recurso es aquello que te deja más capaz después de usarlo.")
    f = fecha_bloque(5)
    section_title("Registro")
    recurso = st.text_input("¿Qué recurso has fortalecido hoy?")
    p = st.text_area("¿Por qué era importante?", height=80)
    c = st.text_area("¿Cómo lo hiciste?", height=90)
    s = st.text_area("¿Cómo te sientes después?", height=80)
    if st.button("Guardar registro"):
        meta = {"por_que": p, "como": c, "despues": s}
        guardar_respuesta(5, f, "Gestión de recursos — Recurso", recurso, meta=meta)

# ---------- BLOQUE 6 ----------
elif menu == "BLOQUE 6\nDetector de Sesgos":
    block_title("Bloque 6: Detector de sesgos")
    instruction("El piloto automático defendiendo su ruta.")
    f = fecha_bloque(6)
    section_title("Registro")
    sesgo = st.selectbox("Sesgo identificado:", BIASES)
    obs = st.text_area("Contexto:", height=120)
    if st.button("Guardar registro"):
        guardar_respuesta(6, f, f"Sesgos — {sesgo}", obs)

# ---------- BLOQUE 7 ----------
elif menu == "BLOQUE 7\nEl Abogado del Diablo":
    block_title("Bloque 7: El abogado del diablo")
    instruction("Pinchar el globo del relato cuando se vuelve dogma.")
    f = fecha_bloque(7)
    section_title("Registro")
    creencia = st.text_input("Creencia limitante detectada:")
    contra = st.text_area("Evidencia real que la contradice:", height=140)
    if st.button("Guardar registro"):
        guardar_respuesta(7, f, f"Abogado del diablo — Creencia: {creencia}", contra)

# ---------- BLOQUE 8 ----------
elif menu == "BLOQUE 8\nAntifragilidad":
    block_title("Bloque 8: Antifragilidad")
    instruction("Usar el caos como fertilizante.")
    f = fecha_bloque(8)
    section_title("Registro")
    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    ventaja = st.text_area("¿Qué beneficio has extraído?", height=120)
    if st.button("Guardar registro"):
        guardar_respuesta(8, f, f"Antifragilidad — Evento: {caos}", ventaja)

# ---------- BLOQUE 9 ----------
elif menu == "BLOQUE 9\nEl Nuevo Rumbo":
    block_title("Bloque 9: El nuevo rumbo")
    instruction("Cierre del programa.")
    section_title("Reflexión final")
    reflexion = st.text_area("Escribe tu reflexión:", height=190)
    if st.button("Guardar reflexión final"):
        guardar_respuesta(9, "", "Integración — Reflexión final", reflexion)
        st.balloons()

# ---------- MIS RESPUESTAS ----------
elif menu == "📊 MIS RESPUESTAS":
    block_title("Mis respuestas")

    df = df_all.copy()
    if df.empty:
        st.write("Aún no tienes registros guardados.")
    else:
        df["fecha_sort"] = df["fecha"].apply(lambda x: to_sortable_date(x) if isinstance(x, str) else None)
        df["ts_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["ts_date"] = df["ts_dt"].dt.date

        min_d = df["ts_date"].dropna().min()
        max_d = df["ts_date"].dropna().max()
        if pd.isna(min_d) or pd.isna(max_d):
            min_d = date.today(); max_d = date.today()

        # Filtros
        section_title("Filtros")
        f1, f2, f3 = st.columns([0.5, 0.5, 1.0])
        start = f1.date_input("Desde", value=min_d)
        end = f2.date_input("Hasta", value=max_d)
        bloques_sel = f3.multiselect("Bloques", sorted(df["bloque"].dropna().unique().tolist()), default=sorted(df["bloque"].dropna().unique().tolist()))

        dff = df[df["bloque"].isin(bloques_sel)].copy()
        dff = dff[(dff["ts_date"].notna()) & (dff["ts_date"] >= start) & (dff["ts_date"] <= end)]

        # Dashboard Stats (Fondo AZUL solicitado)
        total_periodo = int(len(dff))
        dom_emo, dom_ctx = dominant_emotion_and_context(dff)
        emo_pred = dom_emo if dom_emo else "—"

        st.markdown('<div class="az-panel">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="az-statbar">
              <div class="az-stat-primary">
                <div class="k">Registros del periodo</div>
                <div class="v">{total_periodo}</div>
              </div>
              <div class="az-stat">
                <div class="k">Emoción predominante</div>
                <div class="v">{emo_pred}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Historial", "Gráficos", "Insights"])

        # -------- HISTORIAL
        with tab1:
            section_title("Historial detallado")
            dff2 = dff.sort_values(by=["bloque", "fecha_sort", "timestamp"], ascending=[True, True, True])

            def render_meta(meta):
                if not isinstance(meta, dict) or not meta: return
                mapping = [("por_que","Por qué"), ("donde","Dónde"), ("que_paso","Qué pasó"), ("como","Cómo"), ("despues","Efecto")]
                for k, label in mapping:
                    v = str(meta.get(k, "")).strip()
                    if v: st.markdown(f"**{label}:** {v}")
                # Extras
                for k, v in meta.items():
                    if k not in [x[0] for x in mapping]:
                        st.markdown(f"**{k}:** {v}")

            for bloque in sorted(dff2["bloque"].unique()):
                st.markdown(f"### Bloque {bloque}")
                bdf = dff2[dff2["bloque"] == bloque].copy()

                if bloque == 9:
                    for _, row in bdf.iterrows():
                        st.markdown(f"**{row.get('concepto','')}**")
                        resp = str(row.get("respuesta", "")).strip()
                        if resp: st.write(resp)
                        render_meta(row.get("meta", {}))
                        st.divider()
                else:
                    bdf["group_date"] = bdf["fecha"].where(bdf["fecha"].astype(str).str.strip() != "", None)
                    bdf["group_date"] = bdf["group_date"].fillna(bdf["ts_date"].astype(str))
                    for gd in bdf["group_date"].unique():
                        st.markdown(f"#### {gd}")
                        gdf = bdf[bdf["group_date"] == gd]
                        for _, row in gdf.iterrows():
                            st.markdown(f"**{row.get('concepto','')}**")
                            resp = str(row.get("respuesta", "")).strip()
                            if resp: st.write(resp)
                            render_meta(row.get("meta", {}))
                            st.divider()

        # -------- GRÁFICOS
        with tab2:
            section_title("Visualización de datos")
            daily = dff.dropna(subset=["ts_date"]).groupby("ts_date").size().reset_index(name="registros")
            daily = daily.sort_values("ts_date")
            
            section_title("Actividad diaria")
            if PLOTLY_AVAILABLE:
                fig_line = px.line(daily, x="ts_date", y="registros", markers=True)
                fig_line.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                if len(daily): st.line_chart(daily.set_index("ts_date"))
            
            section_title("Frecuencia de emociones (Bloque 4)")
            d4 = dff[dff["bloque"] == 4].copy()
            d4["emo"] = d4["respuesta"].fillna("").astype(str).str.strip()
            d4 = d4[d4["emo"] != ""]
            if len(d4):
                emo_counts = d4["emo"].value_counts().reset_index()
                emo_counts.columns = ["Emoción", "Frecuencia"]
                if PLOTLY_AVAILABLE:
                    fig_bar = px.bar(emo_counts, x="Frecuencia", y="Emoción", orientation="h")
                    fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.bar_chart(emo_counts.set_index("Emoción"))
            else:
                st.info("Faltan registros en el Bloque 4.")

        # -------- INSIGHTS
        with tab3:
            section_title("Sistema de inteligencia (Insights)")
            recs = recommendations(dom_emo)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown("### Patrones")
                st.write("")
                st.markdown(f"**Emoción dominante:** {dom_emo if dom_emo else '—'}")
                st.markdown(f"**Contexto recurrente:** {dom_ctx if dom_ctx else '—'}")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown("### Sugerencias")
                st.write("")
                for r in recs[:4]: st.write(f"- {r}")
                st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        c1, c2, c3 = st.columns([0.45, 0.35, 0.2])
        with c1:
            export_path = DATA_DIR / "history_export.csv"
            dff.to_csv(export_path, index=False, encoding="utf-8")
            st.download_button("Descargar CSV", data=export_path.read_bytes(), file_name="azimut_historial.csv")
        with c2:
            with st.expander("Ver tabla completa"):
                st.dataframe(dff.drop(columns=["fecha_sort"], errors="ignore"), use_container_width=True)
        with c3:
            if st.button("Limpiar historial"):
                st.session_state.historial = []
                save_history([])
                st.rerun()
