import json
import re
from datetime import datetime, date
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

# Archivos (en tu repo)
AZIMUT_FILE = Path("azimutrenovadocompleto.txt")
NEWSLETTERS_FILE = Path("AA-TODAS las newsletters publicadas .txt")

# Persistencia local
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
# EXTRACCIONES (básicas, robustas)
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
        if re.search(rf"\b{re.escape(e)}\b", text, flags=re.IGNORECASE):
            emotions.append(e)

    # Heurística: listas cortas separadas por comas
    for line in text.splitlines():
        line = line.strip()
        if "," in line and len(line) < 150:
            if re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line):
                parts = [normalize_space(p) for p in line.split(",")]
                for p in parts:
                    if 2 <= len(p) <= 26 and re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$", p):
                        low = p.lower()
                        if low not in {"emoción primaria", "matices", "emociones", "bloque", "semana"}:
                            emotions.append(p[0].upper() + p[1:] if p else p)

    return unique_preserve(emotions)

EMOTIONS = extract_emotions_from_azimut(AZIMUT_TEXT)

def circadian_checklist_from_corpus(azimut: str, news: str) -> list[str]:
    # Versión “limpia”: coherente con tu mensaje, sin ruido
    base = [
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
    ]
    return base[:12]

CHECKLIST_BLOCK2 = circadian_checklist_from_corpus(AZIMUT_TEXT, NEWS_TEXT)

def biases_from_corpus(news: str, azimut: str) -> list[str]:
    # Base amplia y útil (y compatible con lo que aparece en tus textos)
    biases = [
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
    return unique_preserve(biases)

BIASES = biases_from_corpus(NEWS_TEXT, AZIMUT_TEXT)

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
        "Construir consistencia (con estructura)",
        "Identificar sesgos y no enamorarte de tu primer relato",
    ]
    return unique_preserve(benefits)

BENEFITS_BLOCK9 = azimut_benefits(NEWS_TEXT, AZIMUT_TEXT)

# =========================================================
# BRAND / THEME (claro + oscuro)
# =========================================================
def apply_theme(dark: bool):
    if dark:
        bg = "#0b1220"
        panel = "#121a2a"
        text = "#e9eef7"
        muted = "#b8c2d6"
        card = "#101a2b"
        border = "rgba(255,255,255,0.08)"
    else:
        bg = BRAND_WHITE
        panel = "#ffffff"
        text = "#0b0f1a"
        muted = "#4b5563"
        card = "#ffffff"
        border = "rgba(10,20,40,0.10)"

    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {bg};
            color: {text};
          }}

          /* Sidebar: azul fijo */
          section[data-testid="stSidebar"] {{
            background: {BRAND_BLUE};
          }}

          /* Sidebar: textos amarillos (items) */
          section[data-testid="stSidebar"] * {{
            color: {BRAND_YELLOW} !important;
            font-weight: 800 !important;
          }}

          /* Separación entre items del menú */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
            padding: 10px 10px !important;
            margin: 6px 0px !important;
            border-radius: 12px !important;
          }}

          /* Radio seleccionado: intento de marca amarilla */
          section[data-testid="stSidebar"] input[type="radio"] {{
            accent-color: {BRAND_YELLOW} !important;
          }}

          /* Títulos */
          h1, h2, h3, h4 {{
            color: {BRAND_BLUE} !important;
          }}

          /* Texto general */
          .stMarkdown, .stText, p, li, span {{
            color: {text};
          }}

          /* Cards (estilo “app premium”) */
          .az-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
          }}
          .az-muted {{
            color: {muted} !important;
          }}

          /* Botones */
          div.stButton > button {{
            background-color: {BRAND_BLUE} !important;
            color: {BRAND_YELLOW} !important;
            border: 0px !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            padding: 0.65rem 1.05rem !important;
          }}
          div.stButton > button:hover {{
            filter: brightness(0.95);
          }}

          /* Inputs */
          .stTextInput input, .stTextArea textarea, .stSelectbox div {{
            border-radius: 14px !important;
          }}

          /* Botón luna: flotante bottom-left */
          .az-moon {{
            position: fixed;
            left: 18px;
            bottom: 18px;
            z-index: 9999;
          }}
          .az-moon button {{
            width: 44px !important;
            height: 44px !important;
            border-radius: 999px !important;
            padding: 0px !important;
            font-size: 18px !important;
            background: {BRAND_BLUE} !important;
            color: {BRAND_YELLOW} !important;
            box-shadow: 0 10px 22px rgba(0,0,0,0.20) !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_theme(st.session_state.dark_mode)

# =========================================================
# ACCIÓN: luna (modo oscuro)
# =========================================================
# Truco: colocamos un botón normal pero lo “atamos” a un wrapper con posición fija
moon_wrap = st.container()
moon_wrap.markdown('<div class="az-moon">', unsafe_allow_html=True)
moon_label = "🌙" if not st.session_state.dark_mode else "🌙"
if moon_wrap.button(moon_label, key="moon_toggle", help="Modo oscuro"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()
moon_wrap.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# DATOS → DF + utilidades analíticas
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

def compute_metrics(df: pd.DataFrame):
    total = len(df)
    # días con registros (usa fecha manual si está, si no, intenta por timestamp)
    days = set()
    for _, r in df.iterrows():
        if isinstance(r.get("fecha"), str) and r["fecha"].strip():
            days.add(r["fecha"].strip())
        else:
            ts = r.get("timestamp")
            if isinstance(ts, str) and ts:
                days.add(ts[:10])
    active_days = len(days)
    # últimos 7 días: aproximación basada en timestamp real
    last7 = 0
    if total:
        try:
            df_ts = df[df["timestamp"].notna()].copy()
            df_ts["ts_dt"] = pd.to_datetime(df_ts["timestamp"], errors="coerce")
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
            last7 = int((df_ts["ts_dt"] >= cutoff).sum())
        except Exception:
            last7 = 0
    return total, active_days, last7

def dominant_emotion_and_context(df: pd.DataFrame):
    # Emoción dominante: bloque 4 (concepto contiene "Precisión emocional")
    d4 = df[df["bloque"] == 4].copy()
    emotion = None
    context = None

    if len(d4):
        # emoción es "respuesta"
        emo_counts = d4["respuesta"].fillna("").astype(str).str.strip()
        emo_counts = emo_counts[emo_counts != ""]
        if len(emo_counts):
            emotion = emo_counts.value_counts().index[0]

        # contexto recurrente: meta.donde
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
            "Registra 2–3 días en el Bloque 4 para que pueda aparecer una señal clara.",
            "Si hoy estás dispersa: Bloque 2 (ritmo) suele ser la palanca de bajo coste.",
        ]

    e = dominant_emotion.lower()
    # Mapa simple (evita prometer “IA clínica”; son sugerencias funcionales)
    if any(k in e for k in ["ans", "mied", "pavor", "inquiet", "nerv", "estrés", "estres"]):
        return [
            "Señal de activación alta: vuelve al Bloque 2 (anclas circadianas) hoy.",
            "Haz Bloque 3: localiza el marcador corporal para bajar el ‘ruido’ antes de interpretar.",
        ]
    if any(k in e for k in ["trist", "melanc", "vacío", "vacio"]):
        return [
            "Si hay descenso de energía: Bloque 5 (recurso) en formato mínimo viable.",
            "Haz Bloque 1 (vía negativa): elimina una fricción concreta hoy.",
        ]
    if any(k in e for k in ["ira", "rab", "indign", "enfado"]):
        return [
            "Si hay fricción social: Bloque 7 (abogado del diablo) para desmontar el relato dominante.",
            "Bloque 3: identifica dónde se ‘carga’ el cuerpo antes de responder.",
        ]
    return [
        "Mantén Bloque 4 + Bloque 5 hoy: claridad + recurso.",
        "Si detectas automatismos: Bloque 6 (sesgos) como lupa.",
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
# UI: NAVEGACIÓN
# =========================================================
st.sidebar.title("🧭 Programa Azimut")

MENU_ITEMS = [
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
]

menu = st.sidebar.radio("Ir a:", MENU_ITEMS, key="nav_menu")

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
# HELPERS UI: cards + botones tipo “stitch”
# =========================================================
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

# =========================================================
# PANTALLAS
# =========================================================
df_all = history_df()

# ---------- INICIO / DASHBOARD HOME ----------
if menu == "Inicio":
    total, active_days, last7 = compute_metrics(df_all)
    dom_emo, dom_ctx = dominant_emotion_and_context(df_all)
    recs = recommendations(dom_emo)

    # Hero card
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

    st.write("")

    # Métricas (tiempo real)
    c1, c2, c3 = st.columns(3)
    with c1:
        card("Registros", "Total acumulado")
        st.metric(label="", value=int(total))
        card_end()
    with c2:
        card("Días activos", "Días con al menos un registro")
        st.metric(label="", value=int(active_days))
        card_end()
    with c3:
        card("Últimos 7 días", "Entradas registradas (aprox.)")
        st.metric(label="", value=int(last7))
        card_end()

    st.write("")

    # Insights + recomendaciones dinámicas
    left, right = st.columns([1.1, 0.9])
    with left:
        card("Insights", "Se alimenta de tus registros (sobre todo del Bloque 4).")
        if dom_emo:
            st.write(f"**Emoción dominante:** {dom_emo}")
        else:
            st.write("**Emoción dominante:** (aún no hay suficiente señal)")
        if dom_ctx:
            st.write(f"**Contexto recurrente:** {dom_ctx}")
        else:
            st.write("**Contexto recurrente:** (pendiente)")
        card_end()

    with right:
        card("Sugerencia práctica", "Recomendación dinámica basada en la señal actual.")
        for r in recs[:3]:
            st.write(f"- {r}")
        card_end()

    st.write("")

    # Botones tipo “tiles” para saltar a bloques (como en tu mock)
    card("Accesos rápidos", "Entradas directas (para no depender de la barra lateral).")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Bloque 1"):
            goto("Bloque 1: Vía Negativa")
    with b2:
        if st.button("Bloque 2"):
            goto("Bloque 2: Ritmos Circadianos")
    with b3:
        if st.button("Bloque 3"):
            goto("Bloque 3: Marcadores Somáticos")

    b4, b5, b6 = st.columns(3)
    with b4:
        if st.button("Bloque 4"):
            goto("Bloque 4: Registro de Precisión")
    with b5:
        if st.button("Bloque 5"):
            goto("Bloque 5: Gestión de Recursos")
    with b6:
        if st.button("Bloque 6"):
            goto("Bloque 6: Detector de Sesgos")

    b7, b8, b9 = st.columns(3)
    with b7:
        if st.button("Bloque 7"):
            goto("Bloque 7: El Abogado del Diablo")
    with b8:
        if st.button("Bloque 8"):
            goto("Bloque 8: Antifragilidad")
    with b9:
        if st.button("Bloque 9 (final)"):
            goto("Bloque 9: El Nuevo Rumbo")
    card_end()

# ---------- BLOQUE 1 ----------
elif menu == "Bloque 1: Vía Negativa":
    st.header("📉 Bloque 1: Vía Negativa")
    st.write("Identifica lo que resta. Hoy no añadimos herramientas: quitamos lastre.")
    f = fecha_bloque(1)

    card("Registro del día", "Una frase. Sin épica. Sin negociación.")
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?")
    card_end()

    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)

# ---------- BLOQUE 2 ----------
elif menu == "Bloque 2: Ritmos Circadianos":
    st.header("☀️ Bloque 2: Sincronización biológica")
    st.write("Marca los puntos que has cumplido hoy (10–12 anclas diarias).")
    f = fecha_bloque(2)

    card("Checklist", "Marca lo cumplido. Lo importante es la repetición, no la perfección.")
    seleccionados = []
    for i, item in enumerate(CHECKLIST_BLOCK2):
        if st.checkbox(item, key=f"b2_{i}"):
            seleccionados.append(item)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(2, f, "Ritmos circadianos — Hitos", ", ".join(seleccionados))

# ---------- BLOQUE 3 ----------
elif menu == "Bloque 3: Marcadores Somáticos":
    st.header("🧘 Bloque 3: Marcadores somáticos")
    st.write("El cuerpo habla en dialectos: tensión, nudo, calor, vacío. Vamos a transcribirlo.")
    f = fecha_bloque(3)

    card("Mapa corporal", "Localiza + nombra la sensación con precisión artesanal.")
    zona = st.selectbox(
        "¿Dónde lo sientes?",
        ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros", "Cabeza", "Cuello", "Espalda", "Manos", "Brazos", "Piernas", "Pies"],
    )
    tipo = st.text_input("Describe la sensación (calor, nudo, presión, hormigueo, pesadez...):")
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(3, f, f"Marcador somático — Localización: {zona}", tipo)

# ---------- BLOQUE 4 ----------
elif menu == "Bloque 4: Registro de Precisión":
    st.header("🏷️ Bloque 4: Precisión emocional (registro diario)")
    st.write("Aquí el objetivo no es ‘sentir menos’, sino **nombrar mejor**.")
    f = fecha_bloque(4)

    card("Formulario", "Cuanto más concreto el contexto, más útil el registro.")
    emo = st.selectbox("Emoción detectada:", EMOTIONS if EMOTIONS else ["Ansiedad", "Frustración", "Paz", "Gratitud"])
    por_que = st.text_area("¿Por qué crees que era esa emoción?", height=90)
    donde = st.text_input("¿Dónde estabas? (contexto físico)")
    que_paso = st.text_area("¿Qué pasó para sentir eso? (hechos, no juicio)", height=110)
    card_end()

    if st.button("Guardar registro"):
        meta = {"por_que": por_que, "donde": donde, "que_paso": que_paso}
        guardar_respuesta(4, f, "Precisión emocional — Etiquetado", emo, meta=meta)

# ---------- BLOQUE 5 ----------
elif menu == "Bloque 5: Gestión de Recursos":
    st.header("🧬 Bloque 5: Gestión de recursos")
    st.write("Un recurso es aquello que te deja más capaz después de usarlo, no más roto.")
    f = fecha_bloque(5)

    card("Ejemplos", "Si hoy tu mente viene con la persiana a medio bajar, usa un ejemplo y aterriza.")
    st.write(
        "- Sueño / descanso real\n- Calma / respiración\n- Apoyo social\n- Orden del entorno\n- Movimiento\n"
        "- Nutrición simple\n- Tiempo sin pantallas\n- Límites / decir NO\n- Planificación mínima viable\n"
        "- Exposición a luz y aire\n- Pausas sin estímulo\n- Pedir ayuda explícita"
    )
    card_end()

    card("Registro", "Tres preguntas: motivo → método → efecto.")
    recurso = st.text_input("¿Qué recurso has fortalecido hoy?")
    p = st.text_area("¿Por qué ese recurso era importante hoy?", height=80)
    c = st.text_area("¿Cómo lo hiciste? (acciones concretas)", height=90)
    s = st.text_area("¿Cómo te sientes después de haberlo hecho?", height=80)
    card_end()

    if st.button("Guardar registro"):
        meta = {"por_que": p, "como": c, "despues": s}
        guardar_respuesta(5, f, "Gestión de recursos — Recurso fortalecido", recurso, meta=meta)

# ---------- BLOQUE 6 ----------
elif menu == "Bloque 6: Detector de Sesgos":
    st.header("⚖️ Bloque 6: Detector de sesgos")
    st.write("Sesgo = el piloto automático defendiendo su ruta como si fuera ley natural.")
    f = fecha_bloque(6)

    card("Registro", "El sesgo no se ‘quita’: se detecta antes de que firme el contrato.")
    sesgo = st.selectbox("Sesgo identificado hoy:", BIASES if BIASES else ["Sesgo de confirmación", "Anclaje", "Efecto halo"])
    obs = st.text_area("Contexto (qué pasó, qué pensaste, qué hiciste):", height=120)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(6, f, f"Sesgos — {sesgo}", obs)

# ---------- BLOQUE 7 ----------
elif menu == "Bloque 7: El Abogado del Diablo":
    st.header("😈 Bloque 7: El abogado del diablo")
    st.write("No es autoataque: es pinchar el globo del relato cuando se vuelve dogma.")
    f = fecha_bloque(7)

    card("Ejemplos de creencias limitantes", "Si una te ‘pica’, probablemente es material útil.")
    for b in BELIEF_EXAMPLES:
        st.write(f"- {b}")
    card_end()

    card("Registro", "Primero frase literal → luego hechos que la contradicen.")
    creencia = st.text_input("Creencia limitante detectada (tu versión exacta):")
    st.caption("Pistas si te cuesta:")
    st.write(
        "- Escribe la frase tal como aparece, sin maquillarla.\n"
        "- Pregunta: ¿esto es un **dato** o una **sentencia**?\n"
        "- Si tu mejor amiga dijera esto, ¿qué le responderías?\n"
        "- ¿Qué evidencia reciente contradice la creencia, aunque sea pequeña?"
    )
    contra = st.text_area("Evidencia real que la contradice (hechos, ejemplos, datos):", height=140)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(7, f, f"Abogado del diablo — Creencia: {creencia}", contra)

# ---------- BLOQUE 8 ----------
elif menu == "Bloque 8: Antifragilidad":
    st.header("💎 Bloque 8: Antifragilidad")
    st.write("No romantizamos el caos. Lo usamos como fertilizante cuando ya ha ocurrido.")
    f = fecha_bloque(8)

    card("Registro", "Evento → aprendizaje. Con pistas si hoy cuesta.")
    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    st.caption("Pistas si te cuesta extraer aprendizaje/beneficio:")
    st.write(
        "- ¿Qué habilidad entrenaste sin querer (paciencia, límites, adaptación)?\n"
        "- ¿Qué información nueva apareció gracias a esto?\n"
        "- Si esto se repitiera, ¿qué harías distinto la próxima vez?\n"
        "- ¿Qué parte de tu control era ilusión?"
    )
    ventaja = st.text_area("¿Qué beneficio o aprendizaje has extraído?", height=120)
    card_end()

    if st.button("Guardar registro"):
        guardar_respuesta(8, f, f"Antifragilidad — Evento: {caos}", ventaja)

# ---------- BLOQUE 9 ----------
elif menu == "Bloque 9: El Nuevo Rumbo":
    st.header("🧭 Bloque 9: Integración (una sola vez)")
    st.write("Este bloque es cierre: úsalo cuando hayas completado el recorrido.")
    card("Beneficios posibles", "Lista compendio (no es checklist moral, es un mapa de posibilidades).")
    st.write("\n".join([f"- {x}" for x in BENEFITS_BLOCK9]))
    card_end()

    card("Reflexión final", "Qué aprendiste, cómo avanzaste por bloques, qué te costó y qué gestionas mejor ahora.")
    reflexion = st.text_area(
        "Escribe tu reflexión:",
        height=190,
    )
    card_end()

    if st.button("Guardar reflexión final"):
        guardar_respuesta(9, "", "Integración — Reflexión final", reflexion)
        st.balloons()

# ---------- MIS RESPUESTAS + ANALÍTICA ----------
elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Mis respuestas")

    if df_all.empty:
        st.write("Aún no tienes registros guardados.")
    else:
        # Preparación (orden + filtro fecha)
        df = df_all.copy()

        df["fecha_sort"] = df["fecha"].apply(lambda x: to_sortable_date(x) if isinstance(x, str) else None)
        # Si no hay fecha manual, intenta desde timestamp
        def ts_date(ts):
            try:
                return pd.to_datetime(ts).date()
            except Exception:
                return None

        df["ts_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["ts_date"] = df["ts_dt"].dt.date

        # ---------- Filtros inteligentes ----------
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

        # ---------- TAB 1: HISTORIAL por bloque → fecha ----------
        with tab1:
            st.markdown("### Historial por bloque → por fecha")
            dff2 = dff.sort_values(by=["bloque", "fecha_sort", "timestamp"], ascending=[True, True, True])

            for bloque in sorted(dff2["bloque"].unique()):
                st.subheader(f"Bloque {bloque}")
                bdf = dff2[dff2["bloque"] == bloque].copy()

                if bloque == 9:
                    for _, row in bdf.iterrows():
                        st.markdown(f"**{row.get('concepto','')}**")
                        st.write(row.get("respuesta", ""))
                        meta = row.get("meta", {})
                        if isinstance(meta, dict) and meta:
                            st.caption("Detalles:")
                            st.json(meta)
                        st.divider()
                else:
                    # Agrupa por fecha manual (si está) y si no, por ts_date
                    # preferimos fecha manual visible:
                    bdf["group_date"] = bdf["fecha"].where(bdf["fecha"].astype(str).str.strip() != "", None)
                    bdf["group_date"] = bdf["group_date"].fillna(bdf["ts_date"].astype(str))

                    for gd in bdf["group_date"].unique():
                        st.markdown(f"### {gd}")
                        gdf = bdf[bdf["group_date"] == gd]
                        for _, row in gdf.iterrows():
                            st.markdown(f"**{row.get('concepto','')}**")
                            st.write(row.get("respuesta", ""))
                            meta = row.get("meta", {})
                            if isinstance(meta, dict) and meta:
                                st.caption("Detalles:")
                                st.json(meta)
                            st.divider()

        # ---------- TAB 2: VISUALIZACIÓN AVANZADA ----------
        with tab2:
            st.markdown("### Gráficos de tendencia (Plotly)")

            # Tendencia: nº de registros por día
            daily = dff.dropna(subset=["ts_date"]).groupby("ts_date").size().reset_index(name="registros")
            daily = daily.sort_values("ts_date")

            fig_line = px.line(daily, x="ts_date", y="registros", markers=True, title="Constancia de registro (registros/día)")
            st.plotly_chart(fig_line, use_container_width=True)

            # Distribución emocional (Bloque 4)
            d4 = dff[dff["bloque"] == 4].copy()
            d4["emo"] = d4["respuesta"].fillna("").astype(str).str.strip()
            d4 = d4[d4["emo"] != ""]
            if len(d4):
                emo_counts = d4["emo"].value_counts().reset_index()
                emo_counts.columns = ["Emoción", "Frecuencia"]
                fig_bar = px.bar(emo_counts, x="Emoción", y="Frecuencia", title="Distribución emocional (Bloque 4)")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Aún no hay registros suficientes en el Bloque 4 para la distribución emocional.")

        # ---------- TAB 3: INSIGHTS + RECOMENDACIONES ----------
        with tab3:
            st.markdown("### Sistema de análisis e inteligencia (Insights)")
            dom_emo, dom_ctx = dominant_emotion_and_context(dff)
            recs = recommendations(dom_emo)

            c1, c2 = st.columns(2)
            with c1:
                card("Detección de patrones", "Emoción dominante + contexto recurrente (si hay señal).")
                st.write(f"**Emoción dominante:** {dom_emo if dom_emo else '—'}")
                st.write(f"**Contexto recurrente:** {dom_ctx if dom_ctx else '—'}")
                card_end()

            with c2:
                card("Recomendaciones dinámicas", "Sugerencias prácticas basadas en la señal actual.")
                for r in recs[:4]:
                    st.write(f"- {r}")
                card_end()

        # ---------- EXPORT + limpieza ----------
        st.write("")
        c1, c2, c3 = st.columns([0.45, 0.35, 0.2])

        with c1:
            export_path = DATA_DIR / "history_export.csv"
            # export “profesional”: filtrado según los filtros actuales
            export_cols = ["timestamp", "bloque", "fecha", "concepto", "respuesta", "meta"]
            dff_export = dff.copy()
            dff_export = dff_export[export_cols]
            dff_export.to_csv(export_path, index=False, encoding="utf-8")
            st.download_button(
                "Descargar CSV (filtrado)",
                data=export_path.read_bytes(),
                file_name="azimut_historial_filtrado.csv",
            )

        with c2:
            with st.expander("Ver tabla completa (debug)"):
                show = dff.copy()
                show = show.drop(columns=["fecha_sort"], errors="ignore")
                st.dataframe(show, use_container_width=True)

        with c3:
            if st.button("Limpiar historial"):
                st.session_state.historial = []
                save_history([])
                st.rerun()
