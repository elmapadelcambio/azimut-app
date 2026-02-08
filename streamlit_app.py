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
# HISTORIAL
# =========================================================
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
# EXTRACCIONES (básicas, robustas)
# =========================================================
def extract_emotions_from_azimut(text: str) -> list[str]:
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


EMOTIONS = extract_emotions_from_azimut(AZIMUT_TEXT)


def circadian_checklist_from_corpus(_azimut: str, _news: str) -> list[str]:
    return [
        "Me acuesto y me levanto a horas consistentes (también fines de semana)",
        "Dormitorio fresco, oscuro y silencioso",
        "Evito pantallas/luz intensa antes de dormir",
        "Rutina de aterrizaje nocturno (bajar estímulos 30–60 min)",
        "Luz natural al inicio del día (salir fuera aunque esté nublado)",
        "Movimiento temprano (caminar/estirar/actividad suave)",
        "Café cuando ya he arrancado (no como primer disparo del día)",
        "Ceno con margen antes de dormir",
        "Luz brillante solo de día; por la noche, luz baja",
        "Si hago siesta, que sea corta y no tarde",
        "Contacto con el exterior (aire/naturaleza) como ancla diaria",
        "Coherencia entre luz, comida y actividad (sin vivir en husos horarios)",
    ][:12]


CHECKLIST_BLOCK2 = circadian_checklist_from_corpus(AZIMUT_TEXT, NEWS_TEXT)


def biases_from_corpus(_news: str, _azimut: str) -> list[str]:
    return unique_preserve(
        [
            "Sesgo de confirmación",
            "Sesgo de negatividad",
            "Sesgo de supervivencia",
            "Falacia de los costes hundidos",
            "Heurística de autoridad",
            "Heurística de disponibilidad",
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


BIASES = biases_from_corpus(NEWS_TEXT, AZIMUT_TEXT)


def limiting_beliefs_examples(_news: str, _azimut: str) -> list[str]:
    return unique_preserve(
        [
            "“No puedo.”",
            "“Debo tener control sobre todo para sentirme segura.”",
            "“Tengo que ser bueno.”",
            "“No debo fallar.”",
            "“No debo decepcionar.”",
            "“He fallado, por tanto, no valgo.”",
            "“Es lo que hay; no hay opciones.”",
        ]
    )


BELIEF_EXAMPLES = limiting_beliefs_examples(NEWS_TEXT, AZIMUT_TEXT)


def azimut_benefits(_news: str, _azimut: str) -> list[str]:
    return unique_preserve(
        [
            "Entender tus emociones (sin juzgarte)",
            "Regular tu respuesta al estrés",
            "Cultivar atención, presencia y calma",
            "Tomar decisiones con más claridad",
            "Reconocer patrones y automatismos",
            "Mejorar tu tolerancia a la incertidumbre",
            "Aumentar tu capacidad de parar antes de reaccionar",
            "Reencuadrar narrativas que te secuestran",
            "Construir consistencia (con estructura)",
            "Identificar sesgos y no enamorarte de tu primer relato",
        ]
    )


BENEFITS_BLOCK9 = azimut_benefits(NEWS_TEXT, AZIMUT_TEXT)

# =========================================================
# BRAND / THEME (solo modo claro)
# =========================================================
def apply_theme():
    bg = BRAND_WHITE
    text = "#0b0f1a"
    muted = "#4b5563"
    card = "#ffffff"
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

          /* Radio labels: más aire entre items */
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

          /* Título de bloque (negro) + subrayado inferior azul */
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

          /* Subtítulos internos (negro) + subrayado amarillo */
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

          /* MÁS AIRE en el patrón: subtítulo -> frase en negrita -> pregunta */
          h3 + div p {{
            margin-top: 14px !important;
          }}
          .stMarkdown p {{
            margin-bottom: 12px !important;
            line-height: 1.45 !important;
          }}

          .az-card {{
            background: {card};
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

          /* Botones principales: fondo azul, texto blanco */
          div.stButton > button {{
            background-color: {BRAND_BLUE} !important;
            color: #ffffff !important;
            border: 0px !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            padding: 0.70rem 1.05rem !important;
          }}

          /* Tabs: subrayado activo en azul marca */
          .stTabs [data-baseweb="tab-highlight"] {{
            background-color: {BRAND_BLUE} !important;
          }}
          .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: {text} !important;
          }}

          /* Multiselect tags (Bloques): fondo azul */
          .stMultiSelect span[data-baseweb="tag"] {{
            background-color: {BRAND_BLUE} !important;
            color: #ffffff !important;
            border: 0px !important;
          }}

          hr {{
            border-color: {border} !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme()

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
    if any(k in e for k in ["ans", "mied", "pavor", "inquiet", "nerv", "estrés", "estres"]):
        return [
            "Señal de activación alta: hoy prioriza Bloque 2 (anclas circadianas).",
            "Luego Bloque 3: localiza el marcador corporal antes de interpretar.",
        ]
    if any(k in e for k in ["trist", "melanc", "vacío", "vacio"]):
        return [
            "Si baja la energía: Bloque 5 (recurso) en formato mínimo viable.",
            "Bloque 1: elimina una fricción concreta hoy.",
        ]
    if any(k in e for k in ["ira", "rab", "indign", "enfado"]):
        return [
            "Si hay fricción social: Bloque 7 (abogado del diablo) para desmontar el relato dominante.",
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
# UI: navegación
# =========================================================
st.sidebar.markdown('<div class="az-sidebar-title">Azimut</div>', unsafe_allow_html=True)

MENU_ITEMS = [
    "INICIO",
    "Bloque 1: Vía Negativa",
    "Bloque 2: Ritmos Circadianos",
    "Bloque 3: Marcadores Somáticos",
    "Bloque 4: Registro de Precisión",
    "Bloque 5: Gestión de Recursos",
    "Bloque 6: Detector de Sesgos",
    "Bloque 7: El Abogado del Diablo",
    "Bloque 8: Antifragilidad",
    "Bloque 9: El Nuevo Rumbo",
    "📊 MIS RESPUESTAS",
]
menu = st.sidebar.radio("Ir a:", MENU_ITEMS, key="nav_menu")

# =========================================================
# UI helpers: cards + goto
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
    card("Azimut", "Cuaderno de navegación: no para pensar más, sino para pensar mejor.")
    st.write(
        "La idea es sencilla y obstinada: **cada día** completas el bloque (o bloques) que te toquen, "
        "sin necesidad de hacerlo perfecto. Al principio costará —como afinar el oído en una sala con eco—, "
        "pero con los días notarás algo muy concreto: **identificarás antes lo que te pasa**, "
        "y tus explicaciones tendrán más precisión y menos niebla.\n\n"
        "Esa mejora no es un sentimiento: es **evidencia**. Se ve en el detalle, en la claridad, "
        "en la rapidez con la que nombras una emoción, detectas un sesgo o localizas el punto exacto "
        "del cuerpo donde se tensó el sistema.\n\n"
        "Tus respuestas se guardan en **“📊 MIS RESPUESTAS”**. Ahí podrás ver el historial por bloques y por fecha, "
        "identificar **qué patrones se repiten** y observar el avance en otros puntos.\n\n"
        "Deja **“Bloque 9: El Nuevo Rumbo”** para el final: es el cierre del programa, cuando hayas completado el recorrido."
    )
    card_end()

elif menu == "Bloque 1: Vía Negativa":
    st.header("Bloque 1: Vía Negativa")
    st.write("Identifica lo que resta. Hoy no añadimos herramientas: quitamos lastre.")
    f = fecha_bloque(1)

    card("Registro del día", enunciado="Una frase. Sin épica. Sin negociación.")
    st.write("¿Qué vas a dejar de hacer hoy?")
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    dato = st.text_input("", label_visibility="collapsed")
    card_end()

    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)

elif menu == "Bloque 2: Ritmos Circadianos":
    st.header("Bloque 2: Ritmos Circadianos")
    st.write("Marca los puntos que has cumplido hoy (10–12 anclas diarias).")
    f = fecha_bloque(2)

    card("Checklist", enunciado="Marca lo cumplido. La repetición vence a la motivación.")
    seleccionados = []
    for i, item in enumerate(CHECKLIST_BLOCK2):
        if st.checkbox(item, key=f"b2_{i}"):
            seleccionados.append(item)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(2, f, "Ritmos circadianos — Hitos", ", ".join(seleccionados))

elif menu == "Bloque 3: Marcadores Somáticos":
    st.header("Bloque 3: Marcadores somáticos")
    st.write("El cuerpo habla en dialectos: tensión, nudo, calor, vacío. Vamos a transcribirlo.")
    f = fecha_bloque(3)

    card("Mapa corporal", enunciado="Localiza + nombra la sensación con precisión artesanal.")
    zona = st.selectbox(
        "¿Dónde lo sientes?",
        ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros", "Cabeza", "Cuello", "Espalda", "Manos", "Brazos", "Piernas", "Pies"],
    )
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    tipo = st.text_input("Describe la sensación (calor, nudo, presión, hormigueo, pesadez...):")
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(3, f, f"Marcador somático — Localización: {zona}", tipo)

elif menu == "Bloque 4: Registro de Precisión":
    st.header("Bloque 4: Registro de Precisión")
    st.write("Aquí el objetivo no es ‘sentir menos’, sino **nombrar mejor**.")
    f = fecha_bloque(4)

    card("Formulario", enunciado="Cuanto más concreto el contexto, más útil el registro.")
    emo = st.selectbox("Emoción detectada:", EMOTIONS if EMOTIONS else ["Ansiedad", "Frustración", "Paz", "Gratitud"])
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    por_que = st.text_area("¿Por qué crees que era esa emoción?", height=90)
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    donde = st.text_input("¿Dónde estabas? (contexto físico)")
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    que_paso = st.text_area("¿Qué pasó para sentir eso? (hechos, no juicio)", height=110)
    card_end()

    if st.button("Guardar registro"):
        meta = {"por_que": por_que, "donde": donde, "que_paso": que_paso}
        guardar_respuesta(4, f, "Precisión emocional — Etiquetado", emo, meta=meta)

elif menu == "Bloque 5: Gestión de Recursos":
    st.header("Bloque 5: Gestión de recursos")
    st.write("Un recurso es aquello que te deja más capaz después de usarlo, no más roto.")
    f = fecha_bloque(5)

    card("Ejemplos", enunciado="Si hoy tu mente viene con la persiana a medio bajar, usa un ejemplo y aterriza.")
    st.write(
        "- Sueño / descanso real\n- Calma / respiración\n- Apoyo social\n- Orden del entorno\n- Movimiento\n"
        "- Nutrición simple\n- Tiempo sin pantallas\n- Límites / decir NO\n- Planificación mínima viable\n"
        "- Exposición a luz y aire\n- Pausas sin estímulo\n- Pedir ayuda explícita"
    )
    card_end()

    card("Registro", enunciado="Motivo → método → efecto.")
    recurso = st.text_input("¿Qué recurso has fortalecido hoy?")
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    p = st.text_area("¿Por qué ese recurso era importante hoy?", height=80)
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    c = st.text_area("¿Cómo lo hiciste? (acciones concretas)", height=90)
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    s = st.text_area("¿Cómo te sientes después de haberlo hecho?", height=80)
    card_end()

    if st.button("Guardar registro"):
        meta = {"por_que": p, "como": c, "despues": s}
        guardar_respuesta(5, f, "Gestión de recursos — Recurso fortalecido", recurso, meta=meta)

elif menu == "Bloque 6: Detector de Sesgos":
    st.header("Bloque 6: Detector de sesgos")
    st.write("Sesgo = el piloto automático defendiendo su ruta como si fuera ley natural.")
    f = fecha_bloque(6)

    card("Registro", enunciado="Detecta el sesgo antes de que firme el contrato.")
    sesgo = st.selectbox("Sesgo identificado hoy:", BIASES)
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    obs = st.text_area("Contexto (qué pasó, qué pensaste, qué hiciste):", height=120)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(6, f, f"Sesgos — {sesgo}", obs)

elif menu == "Bloque 7: El Abogado del Diablo":
    st.header("Bloque 7: El abogado del diablo")
    st.write("No es autoataque: es pinchar el globo del relato cuando se vuelve dogma.")
    f = fecha_bloque(7)

    card("Ejemplos de creencias limitantes", enunciado="Si una te pica, probablemente es material útil.")
    for b in BELIEF_EXAMPLES:
        st.write(f"- {b}")
    card_end()

    card("Registro", enunciado="Frase literal → hechos que la contradicen.")
    creencia = st.text_input("Creencia limitante detectada (tu versión exacta):")
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    st.caption("Pistas si te cuesta:")
    st.write(
        "- Escribe la frase tal como aparece, sin maquillarla.\n"
        "- ¿Es un **dato** o una **sentencia**?\n"
        "- Si tu mejor amiga dijera esto, ¿qué le responderías?\n"
        "- ¿Qué evidencia reciente la contradice, aunque sea pequeña?"
    )
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    contra = st.text_area("Evidencia real que la contradice (hechos):", height=140)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(7, f, f"Abogado del diablo — Creencia: {creencia}", contra)

elif menu == "Bloque 8: Antifragilidad":
    st.header("Bloque 8: Antifragilidad")
    st.write("No romantizamos el caos. Lo usamos como fertilizante cuando ya ha ocurrido.")
    f = fecha_bloque(8)

    card("Registro", enunciado="Evento → aprendizaje (con pistas si hoy cuesta).")
    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    st.caption("Pistas:")
    st.write(
        "- ¿Qué habilidad entrenaste sin querer?\n"
        "- ¿Qué información nueva apareció?\n"
        "- Si se repitiera, ¿qué harías distinto?\n"
        "- ¿Qué parte de tu control era ilusión?"
    )
    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
    ventaja = st.text_area("¿Qué beneficio o aprendizaje has extraído?", height=120)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(8, f, f"Antifragilidad — Evento: {caos}", ventaja)

elif menu == "Bloque 9: El Nuevo Rumbo":
    st.header("Bloque 9: El Nuevo Rumbo")
    st.write("Este bloque es cierre: úsalo cuando hayas completado el recorrido.")

    card("Beneficios de haber completado Azimut", enunciado="Lista compendio (mapa de posibilidades).")
    st.write("\n".join([f"- {x}" for x in BENEFITS_BLOCK9]))
    card_end()

    card("Reflexión final", enunciado="Qué aprendiste, cómo avanzaste por bloques, qué te costó y qué gestionas mejor ahora.")
    reflexion = st.text_area("Escribe tu reflexión:", height=190)
    card_end()

    if st.button("Guardar reflexión final"):
        guardar_respuesta(9, "", "Integración — Reflexión final", reflexion)
        st.balloons()

elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Mis respuestas")

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

                if bloque == 9:
                    for _, row in bdf.iterrows():
                        card(row.get("concepto", "") or "Registro", subtitle=None)
                        st.write(row.get("respuesta", ""))
                        meta = row.get("meta", {})
                        if isinstance(meta, dict) and meta:
                            st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
                            st.caption("Detalles")
                            for k, v in meta.items():
                                if str(v).strip():
                                    st.write(f"**{k.replace('_',' ').capitalize()}:** {v}")
                        card_end()
                        st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
                else:
                    bdf["group_date"] = bdf["fecha"].where(bdf["fecha"].astype(str).str.strip() != "", None)
                    bdf["group_date"] = bdf["group_date"].fillna(bdf["ts_date"].astype(str))

                    for gd in bdf["group_date"].unique():
                        st.markdown(f"#### {gd}")
                        gdf = bdf[bdf["group_date"] == gd]
                        for _, row in gdf.iterrows():
                            card(row.get("concepto", "") or "Registro", subtitle=None)
                            st.write(row.get("respuesta", ""))
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
                fig_line = px.line(
                    daily, x="ts_date", y="registros", markers=True, title="Constancia de registro (registros/día)"
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Plotly no está instalado. Usando gráficos nativos. (Si quieres Plotly, añade `plotly` a requirements.txt).")
                if len(daily):
                    chart_df = daily.set_index("ts_date")
                    st.line_chart(chart_df)

            d4 = dff[dff["bloque"] == 4].copy()
            d4["emo"] = d4["respuesta"].fillna("").astype(str).str.strip()
            d4 = d4[d4["emo"] != ""]
            if len(d4):
                emo_counts = d4["emo"].value_counts().reset_index()
                emo_counts.columns = ["Emoción", "Frecuencia"]

                if PLOTLY_AVAILABLE:
                    fig_bar = px.bar(emo_counts, x="Emoción", y="Frecuencia", title="Distribución emocional (Bloque 4)")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.bar_chart(emo_counts.set_index("Emoción"))
            else:
                st.info("Aún no hay registros suficientes en el Bloque 4 para la distribución emocional.")

        with tab3:
            st.markdown("### Sistema de análisis e inteligencia (Insights)")
            dom_emo, dom_ctx = dominant_emotion_and_context(dff)
            recs = recommendations(dom_emo)

            c1, c2 = st.columns(2)
            with c1:
                card("Detección de patrones", enunciado="Lo que se repite, manda.")
                st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
                st.write(f"**Emoción dominante:** {dom_emo if dom_emo else '—'}")
                st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
                st.write(f"**Contexto recurrente:** {dom_ctx if dom_ctx else '—'}")
                card_end()
            with c2:
                card("Recomendaciones dinámicas", enunciado="Acción pequeña, palanca grande.")
                st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)
                for r in recs[:4]:
                    st.write(f"- {r}")
                card_end()

        st.write("")
        c1, c2, c3 = st.columns([0.45, 0.35, 0.2])
        with c1:
            export_path = DATA_DIR / "history_export.csv"
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
