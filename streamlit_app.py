import json
import re
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

# Si en tu repo están en otra carpeta, cambia aquí:
AZIMUT_FILE = Path("azimutrenovadocompleto.txt")
NEWSLETTERS_FILE = Path("AA-TODAS las newsletters publicadas .txt")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

# =========================================================
# ESTILOS (Stitch-like UI en contenido + sidebar AZUL)
# - Escritorio ancho: NO limitamos el ancho del contenido.
# - Sidebar azul: se mantiene.
# =========================================================
st.markdown(
    f"""
    <style>
      :root {{
        --bg: #0b1220;
        --panel: #0f1a2b;
        --card: #0c1a2a;
        --text: #e7eefc;
        --muted: #92a4c6;
        --accent: {BRAND_BLUE};
        --accent2: {BRAND_YELLOW};
        --border: rgba(255,255,255,0.08);
        --shadow: 0 14px 36px rgba(0,0,0,0.35);
        --radius: 18px;
      }}

      /* App background (contenido estilo Stitch) */
      .stApp {{
        background: var(--bg);
        color: var(--text);
      }}

      /* Headings */
      h1, h2, h3, h4, h5 {{
        color: var(--text) !important;
        letter-spacing: .15px;
      }}

      /* Ajuste de padding global */
      .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
      }}

      /* =========================
         SIDEBAR (se mantiene AZUL)
         ========================= */
      section[data-testid="stSidebar"] {{
        background: {BRAND_BLUE};
      }}
      section[data-testid="stSidebar"] * {{
        color: {BRAND_WHITE} !important;
      }}

      /* Menú radio: texto en amarillo + negrita */
      section[data-testid="stSidebar"] div[role="radiogroup"] * {{
        color: {BRAND_YELLOW} !important;
        font-weight: 850 !important;
      }}

      /* Radio seleccionado: marca amarilla (fallback por CSS del wrapper) */
      div[role="radiogroup"] label span:first-child {{
        border-color: rgba(249,226,5,0.65) !important;
      }}
      div[role="radiogroup"] label[data-checked="true"] span:first-child {{
        background: {BRAND_YELLOW} !important;
      }}

      /* =========================
         COMPONENTES VISUALES
         ========================= */
      .az-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        padding: 16px 16px;
        margin: 12px 0;
      }}
      .az-card-tight {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        padding: 14px 14px;
        margin: 10px 0;
      }}
      .az-title {{
        font-size: 28px;
        font-weight: 950;
        margin: 0 0 6px 0;
        color: var(--text);
      }}
      .az-sub {{
        color: var(--muted) !important;
        font-size: 14px;
        line-height: 1.5;
        margin: 0 0 10px 0;
      }}
      .az-muted {{
        color: var(--muted) !important;
        font-size: 14px;
        line-height: 1.5;
      }}
      .az-badge {{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(0,167,255,0.12);
        border: 1px solid rgba(0,167,255,0.35);
        color: var(--accent);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .2px;
      }}
      .az-badge-yellow {{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(249,226,5,0.12);
        border: 1px solid rgba(249,226,5,0.35);
        color: var(--accent2);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .2px;
      }}
      .az-divider {{
        height: 1px;
        background: rgba(255,255,255,0.08);
        margin: 12px 0;
      }}

      /* =========================
         INPUTS (dark glass)
         ========================= */
      .stTextInput input, .stTextArea textarea {{
        background: rgba(255,255,255,0.03) !important;
        color: var(--text) !important;
        border-radius: 14px !important;
        border: 1px solid var(--border) !important;
      }}
      .stSelectbox div[data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.03) !important;
        color: var(--text) !important;
        border-radius: 14px !important;
        border: 1px solid var(--border) !important;
      }}
      .stDateInput div[data-baseweb="input"] > div {{
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        border: 1px solid var(--border) !important;
      }}

      /* =========================
         BOTONES (primary)
         Mantengo identidad: azul + amarillo
         ========================= */
      div.stButton > button {{
        background: linear-gradient(180deg, rgba(0,167,255,1), rgba(0,140,220,1)) !important;
        color: {BRAND_YELLOW} !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 950 !important;
        padding: 0.75rem 1.2rem !important;
        box-shadow: 0 10px 24px rgba(0,167,255,0.22);
      }}
      div.stButton > button:hover {{
        filter: brightness(1.03);
      }}

      /* Dataframe */
      [data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        background: rgba(255,255,255,0.02);
      }}

      /* Expander */
      details {{
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 8px 10px;
        background: rgba(255,255,255,0.02);
      }}

      /* Toast/Info boxes: reduce “webby feel” */
      div[data-testid="stAlert"] {{
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        background: rgba(255,255,255,0.03) !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# UTILIDADES
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

# -------------------------
# Persistencia (sin registro)
# -------------------------
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
# “COMPONENTES” HTML (cards/badges)
# =========================================================
def az_header(title: str, subtitle: str | None = None):
    st.markdown(f'<div class="az-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="az-sub">{subtitle}</div>', unsafe_allow_html=True)

def az_card_open(badge: str | None = None, badge_yellow: bool = False, title: str | None = None, subtitle: str | None = None, tight: bool = False):
    klass = "az-card-tight" if tight else "az-card"
    st.markdown(f'<div class="{klass}">', unsafe_allow_html=True)
    if badge:
        bklass = "az-badge-yellow" if badge_yellow else "az-badge"
        st.markdown(f'<span class="{bklass}">{badge}</span>', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div style="font-size:18px;font-weight:950;margin-top:10px">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="az-muted" style="margin-top:8px">{subtitle}</div>', unsafe_allow_html=True)

def az_card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def az_divider():
    st.markdown('<div class="az-divider"></div>', unsafe_allow_html=True)

# =========================================================
# EXTRACCIONES DESDE TUS TEXTOS
# =========================================================
def extract_emotions_from_azimut(text: str) -> list[str]:
    if not text:
        return []
    emotions = []

    primary_candidates = [
        "Amor", "Miedo", "Tristeza", "Ira", "Alegría", "Vergüenza",
        "Asco", "Sorpresa", "Calma", "Ilusión", "Culpa"
    ]
    for e in primary_candidates:
        if re.search(rf"\b{re.escape(e)}\b", text):
            emotions.append(e)

    for line in text.splitlines():
        line = line.strip()
        if "," in line and len(line) < 140:
            if re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line) and not re.search(r"[-]{5,}", line):
                parts = [normalize_space(p) for p in line.split(",")]
                for p in parts:
                    if 2 <= len(p) <= 22 and re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$", p):
                        if p.lower() not in {"emoción primaria", "matices"}:
                            emotions.append(p)

    cleaned = []
    for e in emotions:
        e = e.strip()
        if not e:
            continue
        e = e[0].upper() + e[1:] if e else e
        cleaned.append(e)

    return unique_preserve(cleaned)

EMOTIONS = extract_emotions_from_azimut(AZIMUT_TEXT)

def circadian_checklist_from_corpus(azimut: str, news: str) -> list[str]:
    base = [
        "Me acuesto y me levanto a horas consistentes (también fines de semana)",
        "Dormitorio fresco, oscuro y silencioso",
        "Evito pantallas/luz intensa antes de dormir (modo nocturno + distancia)",
        "Rutina de aterrizaje nocturno (bajar estímulos 30–60 min)",
        "Luz natural al inicio del día (salir fuera aunque esté nublado)",
        "Muevo el cuerpo temprano (caminar/estirar/actividad suave)",
        "Café después de haber “arrancado” (no como primer disparo del día)",
        "Ceno con margen antes de dormir (evito acostarme con digestión en marcha)",
        "Exposición a luz brillante solo en horario diurno (tarde/noche: luz baja)",
        "Si hago siesta, que sea corta y no tarde",
        "Contacto con el exterior (naturaleza / aire / paseo) como ancla diaria",
        "Mantengo coherencia entre luz, comida y actividad (no cada día un huso horario)",
    ]
    return base[:12]

CHECKLIST_BLOCK2 = circadian_checklist_from_corpus(AZIMUT_TEXT, NEWS_TEXT)

def biases_from_corpus(news: str, azimut: str) -> list[str]:
    biases = [
        "Sesgo de confirmación",
        "Heurística de autoridad",
        "Sesgo de credibilidad",
        "Efecto Gell-Mann (amnesia)",
        "Efecto Dunning-Kruger",
        "Falacia de los costes hundidos",
        "Sesgo de negatividad",
        "Sesgo de supervivencia",
        "Efecto bandwagon / pensamiento grupal / efecto manada",
        "Disonancia cognitiva",
        "Atención selectiva",
    ]
    return unique_preserve(biases)

BIASES = biases_from_corpus(NEWSLETTERS_FILE.read_text(encoding="utf-8", errors="ignore") if NEWSLETTERS_FILE.exists() else "", AZIMUT_TEXT)

def limiting_beliefs_examples(news: str, azimut: str) -> list[str]:
    beliefs = [
        "“No puedo.”",
        "“Debo tener control sobre todo para sentirme segura.”",
        "“Tengo que ser bueno.”",
        "“No debo fallar.”",
        "“No debo decepcionar.”",
        "“He fallado, por tanto, no valgo.”",
        "“Es lo que hay; no hay opciones.”",
    ]
    return unique_preserve(beliefs)

BELIEF_EXAMPLES = limiting_beliefs_examples(NEWS_TEXT, AZIMUT_TEXT)

def azimut_benefits(news: str, azimut: str) -> list[str]:
    benefits = [
        "Entender tus emociones (sin juzgarte)",
        "Regular tu respuesta al estrés",
        "Cultivar atención, presencia y calma",
        "Tomar decisiones con más claridad",
        "Reconocer patrones y automatismos",
        "Mejorar tu tolerancia a la incertidumbre",
        "Aumentar tu capacidad de parar antes de reaccionar",
        "Reencuadrar narrativas que te secuestran",
        "Construir consistencia (sin épica, con estructura)",
        "Identificar sesgos y no enamorarte de tu primer relato",
    ]
    return unique_preserve(benefits)

BENEFITS_BLOCK9 = azimut_benefits(NEWS_TEXT, AZIMUT_TEXT)

# =========================================================
# UI: NAVEGACIÓN
# =========================================================
st.sidebar.title("🧭 Programa Azimut")
menu = st.sidebar.radio(
    "Ir a:",
    [
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
        "📊 MIS RESPUESTAS",
    ],
)

# =========================================================
# FECHA POR BLOQUE (1–8)
# =========================================================
def fecha_bloque(bloque: int):
    st.caption("Fecha del registro (manual, para tu seguimiento):")
    key = f"fecha_bloque_{bloque}"
    default = st.session_state.get(key, date.today())
    d = st.date_input("Fecha", value=default, key=key)
    return d.strftime("%d/%m/%Y")

# =========================================================
# PANTALLAS
# =========================================================
if menu == "Inicio":
    az_header(
        "Azimut",
        "Cuaderno de navegación: no para *pensar más*, sino para **pensar mejor**."
    )

    az_card_open(badge="INSIGHT", title="Cómo usar esta app",
                 subtitle=(
                     "Cada día completas el bloque (o bloques) que te toquen, sin necesidad de hacerlo perfecto. "
                     "Al principio costará —como afinar el oído en una sala con eco—, pero con los días notarás algo muy concreto: "
                     "**identificarás antes lo que te pasa**, y tus explicaciones tendrán más precisión y menos niebla."
                 ))
    az_card_close()

    az_card_open(badge="PROGRESO", title="Evidencia, no opinión",
                 subtitle=(
                     "Esa mejora no es un sentimiento: es **evidencia**. Se ve en el detalle, en la claridad, en la rapidez con la que "
                     "nombras una emoción, detectas un sesgo o encuentras el punto exacto del cuerpo donde se tensó el sistema."
                 ))
    az_card_close()

    az_card_open(badge="HISTORIAL", badge_yellow=True, title="Dónde se guardan tus respuestas",
                 subtitle=(
                     "Tus respuestas se guardan en **“📊 MIS RESPUESTAS”**. Ahí podrás revisar el historial por bloques y por fecha, "
                     "ver **qué patrones se repiten**, y también el avance en otros puntos (más matices, más contexto, mejores reencuadres)."
                 ))
    az_card_close()

    az_card_open(badge="FINAL", title="Regla de oro",
                 subtitle=(
                     "Deja **“Bloque 9: El Nuevo Rumbo”** para el final: es el cierre del programa, cuando hayas completado el recorrido."
                 ), tight=True)
    az_card_close()


elif menu == "Bloque 1: Vía Negativa":
    az_header("Bloque 1 · Vía Negativa", "Identifica lo que resta. Hoy no añadimos herramientas: quitamos lastre.")

    f = fecha_bloque(1)
    az_card_open(badge="BLOQUE 1", title="Resta del día",
                 subtitle="Una sola cosa. Con precisión. Lo que quitas hoy te devuelve energía mañana.")
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?")
    az_card_close()

    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)


elif menu == "Bloque 2: Ritmos Circadianos":
    az_header("Bloque 2 · Ritmos Circadianos", "Sincronización biológica: pequeñas anclas, grandes efectos.")

    f = fecha_bloque(2)

    az_card_open(badge="CHECKLIST", title="Anclas del día",
                 subtitle="Marca lo que has cumplido hoy. No es perfección: es patrón.")
    seleccionados = []
    for item in CHECKLIST_BLOCK2:
        if st.checkbox(item):
            seleccionados.append(item)
    az_card_close()

    if st.button("Guardar registro"):
        guardar_respuesta(2, f, "Ritmos circadianos — Hitos", ", ".join(seleccionados))


elif menu == "Bloque 3: Marcadores Somáticos":
    az_header("Bloque 3 · Marcadores Somáticos", "El cuerpo habla en dialectos: tensión, nudo, calor, vacío. Vamos a transcribirlo.")

    f = fecha_bloque(3)

    az_card_open(badge="CUERPO", title="Localiza y describe",
                 subtitle="No busques poesía: busca coordenadas.")
    zona = st.selectbox(
        "¿Dónde lo sientes?",
        ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros", "Cabeza", "Cuello", "Espalda", "Manos", "Brazos", "Piernas", "Pies"],
    )
    tipo = st.text_input("Describe la sensación (calor, nudo, presión, hormigueo, pesadez...):")
    az_card_close()

    if st.button("Guardar registro"):
        guardar_respuesta(3, f, f"Marcador somático — Localización: {zona}", tipo)


elif menu == "Bloque 4: Registro de Precisión":
    az_header("Bloque 4 · Registro de Precisión", "Aquí el objetivo no es ‘sentir menos’, sino **nombrar mejor**.")

    f = fecha_bloque(4)

    az_card_open(badge="PRECISIÓN", title="Registro diario",
                 subtitle="Hechos + contexto + etiqueta. Menos niebla, más mapa.")
    emo = st.selectbox("Emoción detectada:", EMOTIONS if EMOTIONS else ["Ansiedad", "Frustración", "Paz", "Gratitud"])
    por_que = st.text_area("¿Por qué crees que era esa emoción?", height=90)
    donde = st.text_area("¿Dónde estabas? (contexto físico)", height=70)
    que_paso = st.text_area("¿Qué pasó para sentir eso? (hechos, no juicio)", height=110)
    az_card_close()

    if st.button("Guardar registro"):
        meta = {"por_que": por_que, "donde": donde, "que_paso": que_paso}
        guardar_respuesta(4, f, "Precisión emocional — Etiquetado", emo, meta=meta)


elif menu == "Bloque 5: Gestión de Recursos":
    az_header("Bloque 5 · Gestión de Recursos", "Un recurso es aquello que te deja más capaz después de usarlo, no más roto.")

    f = fecha_bloque(5)

    az_card_open(badge="RECURSOS", title="Ejemplos rápidos",
                 subtitle="Por si hoy tu mente viene con la persiana a medio bajar.")
    st.markdown(
        '<div class="az-muted">'
        "• Sueño / descanso real<br>"
        "• Calma / respiración<br>"
        "• Apoyo social<br>"
        "• Orden del entorno<br>"
        "• Movimiento<br>"
        "• Nutrición simple<br>"
        "• Tiempo sin pantallas<br>"
        "• Límites / decir NO<br>"
        "• Planificación mínima viable<br>"
        "• Exposición a luz y aire"
        "</div>",
        unsafe_allow_html=True
    )
    az_card_close()

    az_card_open(badge="DIARIO", title="Registro",
                 subtitle="Define un recurso, y aterriza cómo lo fortaleciste.")
    recurso = st.text_input("¿Qué recurso has fortalecido hoy?")
    p = st.text_area("¿Por qué ese recurso era importante hoy?", height=80)
    c = st.text_area("¿Cómo lo hiciste? (acciones concretas)", height=90)
    s = st.text_area("¿Cómo te sientes después de haberlo hecho?", height=80)
    az_card_close()

    if st.button("Guardar registro"):
        meta = {"por_que": p, "como": c, "despues": s}
        guardar_respuesta(5, f, "Gestión de recursos — Recurso fortalecido", recurso, meta=meta)


elif menu == "Bloque 6: Detector de Sesgos":
    az_header("Bloque 6 · Detector de Sesgos", "Sesgo = piloto automático defendiendo su ruta como si fuera ley natural.")

    f = fecha_bloque(6)

    az_card_open(badge="SESGOS", title="Identifica el sesgo",
                 subtitle="Etiqueta la distorsión y describe el contexto. Lo que no nombras, te gobierna.")
    sesgo = st.selectbox("Sesgo identificado hoy:", BIASES if BIASES else ["Sesgo de confirmación", "Anclaje", "Efecto halo"])
    obs = st.text_area("Contexto (qué pasó, qué pensaste, qué hiciste):", height=120)
    az_card_close()

    if st.button("Guardar registro"):
        guardar_respuesta(6, f, f"Sesgos — {sesgo}", obs)


elif menu == "Bloque 7: El Abogado del Diablo":
    az_header("Bloque 7 · El Abogado del Diablo", "No es autoataque. Es pinchar el globo del relato cuando se vuelve dogma.")

    f = fecha_bloque(7)

    az_card_open(badge="EJEMPLOS", title="Creencias típicas (del corpus)", subtitle="Úsalas como espejo, no como guion.", tight=True)
    st.markdown("<div class='az-muted'>" + "<br>".join([f"• {b}" for b in BELIEF_EXAMPLES]) + "</div>", unsafe_allow_html=True)
    az_card_close()

    az_card_open(badge="REENCADRE", title="Tu caso de hoy",
                 subtitle="Escribe la creencia tal cual aparece. Luego busca evidencia que la contradiga.")
    creencia = st.text_input("Creencia limitante (tu versión exacta):")

    st.markdown(
        "<div class='az-muted'>"
        "Pistas:<br>"
        "• Escribe la frase sin maquillarla.<br>"
        "• ¿Es un <b>dato</b> o una <b>sentencia</b>?<br>"
        "• Si tu mejor amiga dijera esto, ¿qué le responderías?<br>"
        "• ¿Qué evidencia reciente la contradice, aunque sea pequeña?"
        "</div>",
        unsafe_allow_html=True
    )

    contra = st.text_area("Evidencia real que la contradice (hechos, ejemplos, datos):", height=140)
    az_card_close()

    if st.button("Guardar registro"):
        guardar_respuesta(7, f, f"Abogado del diablo — Creencia: {creencia}", contra)


elif menu == "Bloque 8: Antifragilidad":
    az_header("Bloque 8 · Antifragilidad", "No romantizamos el caos. Lo usamos como fertilizante cuando ya ha ocurrido.")

    f = fecha_bloque(8)

    az_card_open(badge="EVENTO", title="Qué pasó",
                 subtitle="Describe el imprevisto con precisión mínima viable.")
    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    az_card_close()

    az_card_open(badge="EXTRACCIÓN", title="Qué te dejó",
                 subtitle="No busques épica: busca aprendizaje utilizable.")
    st.markdown(
        "<div class='az-muted'>"
        "Pistas:<br>"
        "• ¿Qué habilidad entrenaste sin querer (paciencia, límites, adaptación)?<br>"
        "• ¿Qué información nueva apareció gracias a esto?<br>"
        "• Si esto se repitiera, ¿qué harías distinto la próxima vez?<br>"
        "• ¿Qué parte de tu control era ilusión?"
        "</div>",
        unsafe_allow_html=True
    )
    ventaja = st.text_area("¿Qué beneficio o aprendizaje has extraído?", height=120)
    az_card_close()

    if st.button("Guardar registro"):
        guardar_respuesta(8, f, f"Antifragilidad — Evento: {caos}", ventaja)


elif menu == "Bloque 9: El Nuevo Rumbo":
    az_header("Bloque 9 · El Nuevo Rumbo", "Integración (una sola vez). Cierre del programa.")

    az_card_open(badge="BENEFICIOS", title="Lo que suele cambiar (compendio)", subtitle="Úsalo como checklist de evolución, no como promesa.", tight=True)
    st.markdown("<div class='az-muted'>" + "<br>".join([f"• {x}" for x in BENEFITS_BLOCK9]) + "</div>", unsafe_allow_html=True)
    az_card_close()

    az_card_open(badge="CIERRE", badge_yellow=True, title="Reflexión final",
                 subtitle="Qué aprendiste, qué avanzaste por bloques, qué te costó, qué gestionas mejor ahora.")
    reflexion = st.text_area("", height=180, label_visibility="collapsed")
    az_card_close()

    if st.button("Guardar reflexión final"):
        guardar_respuesta(9, "", "Integración — Reflexión final", reflexion)
        st.balloons()


elif menu == "📊 MIS RESPUESTAS":
    az_header("📊 Mis respuestas", "Historial por bloque → por fecha. Aquí se ve el patrón… o la niebla.")

    hist = st.session_state.historial
    if not hist:
        az_card_open(badge="VACÍO", title="Aún no hay registros",
                     subtitle="Empieza por un bloque hoy. Un dato honesto vale más que una intención bonita.", tight=True)
        az_card_close()
    else:
        df = pd.DataFrame(hist)

        # Orden por bloque, fecha y timestamp
        if "fecha" in df.columns:
            def to_sortable(d):
                try:
                    return datetime.strptime(d, "%d/%m/%Y").strftime("%Y-%m-%d")
                except Exception:
                    return "9999-99-99"
            df["fecha_sort"] = df["fecha"].apply(to_sortable)
        else:
            df["fecha_sort"] = "9999-99-99"

        df = df.sort_values(by=["bloque", "fecha_sort", "timestamp"], ascending=[True, True, True])

        # Vista “premium”: dos columnas en escritorio (sin forzar ancho)
        left, right = st.columns([1.15, 0.85], gap="large")

        with left:
            for bloque in sorted(df["bloque"].unique()):
                st.markdown(f"### Bloque {bloque}")

                bdf = df[df["bloque"] == bloque].copy()

                if bloque == 9:
                    for _, row in bdf.iterrows():
                        az_card_open(badge=f"BLOQUE {bloque}", title=str(row.get("concepto","")), tight=True)
                        st.write(row.get("respuesta", ""))
                        meta = row.get("meta", {})
                        if isinstance(meta, dict) and meta:
                            st.caption("Detalles:")
                            st.json(meta)
                        az_card_close()
                else:
                    for fecha in bdf["fecha"].unique():
                        st.markdown(f"#### {fecha}")
                        fdf = bdf[bdf["fecha"] == fecha]
                        for _, row in fdf.iterrows():
                            az_card_open(badge=f"BLOQUE {bloque}", title=str(row.get("concepto","")), tight=True)
                            st.write(row.get("respuesta", ""))
                            meta = row.get("meta", {})
                            if isinstance(meta, dict) and meta:
                                st.caption("Detalles:")
                                st.json(meta)
                            az_card_close()

        with right:
            az_card_open(badge="HERRAMIENTAS", badge_yellow=True, title="Acciones", subtitle="Exporta o limpia el historial.", tight=True)
            az_card_close()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Limpiar historial"):
                    st.session_state.historial = []
                    save_history([])
                    st.rerun()

            with col2:
                export_path = DATA_DIR / "history_export.csv"
                df_export = df.drop(columns=["fecha_sort"], errors="ignore")
                df_export.to_csv(export_path, index=False, encoding="utf-8")
                st.download_button(
                    "Descargar CSV",
                    data=export_path.read_bytes(),
                    file_name="azimut_historial.csv",
                )

            with st.expander("Ver tabla completa"):
                show = df.drop(columns=["fecha_sort"], errors="ignore")
                st.dataframe(show, use_container_width=True)
