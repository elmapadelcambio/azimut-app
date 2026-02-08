import json
import re
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
HISTORY_FILE = DATA_DIR / "history.json"
PROFILE_FILE = DATA_DIR / "profile.json"

# =========================================================
# PERFIL / ONBOARDING
# =========================================================
DEFAULT_PROFILE = {
    "onboarded": False,
    "nombre": "",
    "fecha_inicio": date.today().strftime("%Y-%m-%d"),
    "objetivo_dias_semana": 5,  # 1–7
    "objetivo_bloques_dia": 1,  # 1–3
    "modo": "Suave",  # Suave / Estándar / Intensivo
}


def load_profile():
    if PROFILE_FILE.exists():
        try:
            p = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
            if not isinstance(p, dict):
                return DEFAULT_PROFILE.copy()
            out = DEFAULT_PROFILE.copy()
            out.update(p)
            return out
        except Exception:
            return DEFAULT_PROFILE.copy()
    return DEFAULT_PROFILE.copy()


def save_profile(p: dict):
    PROFILE_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


if "perfil" not in st.session_state:
    st.session_state.perfil = load_profile()

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

          /* Multiselect tags: fondo azul */
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


def safe_parse_ymd(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return date.today()


def compute_adherence_metrics(df: pd.DataFrame, profile: dict):
    # df debe tener ts_dt y ts_date calculados
    start = safe_parse_ymd(str(profile.get("fecha_inicio", date.today().strftime("%Y-%m-%d"))))
    today = date.today()
    if start > today:
        start = today

    days_total = (today - start).days + 1
    if days_total < 1:
        days_total = 1

    if df.empty or "ts_date" not in df.columns:
        active_days = 0
        active_rate = 0.0
        avg_per_active = 0.0
        avg_per_total = 0.0
        streak = 0
        best_streak = 0
        return {
            "start": start,
            "today": today,
            "days_total": days_total,
            "active_days": active_days,
            "active_rate": active_rate,
            "avg_per_active": avg_per_active,
            "avg_per_total": avg_per_total,
            "streak": streak,
            "best_streak": best_streak,
        }

    # Filtra desde fecha inicio
    df2 = df[df["ts_date"].notna()].copy()
    df2 = df2[df2["ts_date"] >= start]

    active_dates = sorted(set(df2["ts_date"].tolist()))
    active_days = len(active_dates)
    active_rate = active_days / days_total if days_total else 0.0

    total_regs = len(df2)
    avg_per_active = (total_regs / active_days) if active_days else 0.0
    avg_per_total = total_regs / days_total if days_total else 0.0

    # Streak actual: días consecutivos hasta hoy
    active_set = set(active_dates)
    streak = 0
    d = today
    while d >= start and d in active_set:
        streak += 1
        d = d - timedelta(days=1)

    # Best streak (máxima racha histórica)
    best_streak = 0
    cur = 0
    d = start
    while d <= today:
        if d in active_set:
            cur += 1
            best_streak = max(best_streak, cur)
        else:
            cur = 0
        d = d + timedelta(days=1)

    return {
        "start": start,
        "today": today,
        "days_total": days_total,
        "active_days": active_days,
        "active_rate": active_rate,
        "avg_per_active": avg_per_active,
        "avg_per_total": avg_per_total,
        "streak": streak,
        "best_streak": best_streak,
    }


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
# UI helpers: cards + fecha
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
# ONBOARDING (producto)
# =========================================================
def onboarding_panel():
    p = st.session_state.perfil

    card(
        "Onboarding",
        "Configura tu brújula: esto define tu objetivo y activa el tablero de progreso.",
        enunciado="Tres minutos ahora = semanas de adherencia después.",
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        nombre = st.text_input("Nombre (opcional)", value=str(p.get("nombre", "")))
        fecha_inicio = st.date_input(
            "Fecha de inicio del programa",
            value=safe_parse_ymd(str(p.get("fecha_inicio", date.today().strftime("%Y-%m-%d")))),
        )
        modo = st.selectbox("Modo", ["Suave", "Estándar", "Intensivo"], index=["Suave", "Estándar", "Intensivo"].index(p.get("modo", "Suave")))
    with col2:
        objetivo_dias = st.slider("Objetivo: días/semana", min_value=1, max_value=7, value=int(p.get("objetivo_dias_semana", 5)))
        objetivo_bloques = st.slider("Objetivo: bloques/día", min_value=1, max_value=3, value=int(p.get("objetivo_bloques_dia", 1)))
        st.markdown("**Regla práctica**")
        st.write("- Suave: 1 bloque/día, 3–4 días/semana\n- Estándar: 1–2 bloques/día, 5 días/semana\n- Intensivo: 2–3 bloques/día, 6–7 días/semana")

    card_end()

    if st.button("Guardar onboarding"):
        p["nombre"] = nombre.strip()
        p["fecha_inicio"] = fecha_inicio.strftime("%Y-%m-%d")
        p["objetivo_dias_semana"] = int(objetivo_dias)
        p["objetivo_bloques_dia"] = int(objetivo_bloques)
        p["modo"] = modo
        p["onboarded"] = True
        st.session_state.perfil = p
        save_profile(p)
        st.toast("✅ Onboarding guardado")
        st.rerun()


def progress_dashboard(df_all: pd.DataFrame):
    p = st.session_state.perfil
    card("Progreso", "Tablero operativo: constancia > intensidad.", enunciado="Métricas frías para un sistema emocional más templado.")
    # Preparación df
    df = df_all.copy()
    if df.empty:
        st.write("Aún no hay registros. Empieza con Bloque 1 y deja que el sistema aprenda tu patrón.")
        card_end()
        return

    df["ts_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["ts_date"] = df["ts_dt"].dt.date
    metrics = compute_adherence_metrics(df, p)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Racha actual", f"{metrics['streak']} día(s)")
    with c2:
        st.metric("Mejor racha", f"{metrics['best_streak']} día(s)")
    with c3:
        st.metric("Días activos", f"{metrics['active_days']} / {metrics['days_total']}")
    with c4:
        st.metric("Constancia", f"{metrics['active_rate']*100:.0f}%")

    st.markdown("<div class='az-gap'></div>", unsafe_allow_html=True)

    # Objetivo semanal aproximado: constancia vs objetivo_dias_semana
    objetivo_dias = int(p.get("objetivo_dias_semana", 5))
    # Ventana últimos 7 días
    last7_start = date.today() - timedelta(days=6)
    df7 = df[df["ts_date"].notna() & (df["ts_date"] >= last7_start)].copy()
    active7 = len(set(df7["ts_date"].tolist()))
    st.write(f"**Últimos 7 días:** {active7} día(s) con registro (objetivo: {objetivo_dias}/7).")
    st.progress(min(1.0, active7 / 7.0))

    # Progreso por bloque (conteo simple)
    st.markdown("#### Progreso por bloque")
    counts = df.groupby("bloque").size().reindex(range(1, 10), fill_value=0).reset_index()
    counts.columns = ["Bloque", "Registros"]
    if PLOTLY_AVAILABLE:
        fig = px.bar(counts, x="Bloque", y="Registros", title="Registros por bloque")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(counts.set_index("Bloque"))

    card_end()


# =========================================================
# PANTALLAS
# =========================================================
df_all = history_df()

# ---------- INICIO ----------
if menu == "INICIO":
    card("Azimut", "Cuaderno de navegación: no para pensar más, sino para pensar mejor.")
    p = st.session_state.perfil
    nombre = p.get("nombre", "").strip()
    saludo = f"Hola, {nombre}." if nombre else "Hola."
    st.write(
        f"{saludo} Aquí no buscamos épica: buscamos **fidelidad al proceso**.\n\n"
        "Azimut funciona como un **entrenamiento de precisión**: cada bloque es una coordenada. "
        "Lo rellenás breve, lo guardas, y con el tiempo aparece lo valioso: **patrones**.\n\n"
        "Tus respuestas se guardan en **“📊 MIS RESPUESTAS”**. Ahí puedes filtrar por fechas, "
        "ver tu historial por bloques, y observar constancia y distribución.\n\n"
        "Regla de oro: empieza pequeño. La adherencia es un animal tímido."
    )
    card_end()

    st.markdown("---")

    # Onboarding si no está hecho
    if not st.session_state.perfil.get("onboarded", False):
        onboarding_panel()
    else:
        progress_dashboard(df_all)

        with st.expander("Ajustes de onboarding"):
            onboarding_panel()

# ---------- BLOQUE 1 ----------
elif menu == "Bloque 1: Vía Negativa":
    st.header("Bloque 1: Vía negativa")
    st.write("Antes de añadir soluciones, quita lo que empeora la situación.")
    f = fecha_bloque(1)

    card("Registro del día", subtitle="Menos, pero con impacto.", enunciado="Una frase clara. Sin negociación.")
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?", label_visibility="visible")
    card_end()

    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)

# ---------- BLOQUE 2 ----------
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

# ---------- BLOQUE 3 ----------
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

# ---------- BLOQUE 4 ----------
elif menu == "Bloque 4: Raíz y Rama":
    st.header("Bloque 4: Raíz y rama")
    st.write("Toda emoción compleja suele tener una base más simple.")
    f = fecha_bloque(4)

    card("Registro", subtitle="Raíz (primaria) → Rama (secundaria).", enunciado="Separa la reacción automática de la historia mental.")
    situacion = st.text_input("Situación")
    primaria = st.text_input("Emoción primaria (raíz)")
    secundaria = st.text_input("Emoción secundaria (rama)")
    pensamiento = st.text_area("Pensamiento asociado (la frase interna)", height=90)
    reflexion = st.text_area("Reflexión breve (qué cambió al verlo así)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"primaria": primaria, "secundaria": secundaria, "pensamiento": pensamiento}
        guardar_respuesta(4, f, f"Raíz y rama — {situacion}", reflexion, meta=meta)

# ---------- BLOQUE 5 ----------
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

# ---------- BLOQUE 6 ----------
elif menu == "Bloque 6: Detector de Sesgos":
    st.header("Bloque 6: Detector de sesgos")
    st.write("El piloto automático es eficiente… y a veces tramposo.")
    f = fecha_bloque(6)

    card("Registro", subtitle="Sesgo → pensamiento → alternativa.", enunciado="Detecta el sesgo antes de actuar.")
    sesgo = st.selectbox("Sesgo detectado hoy:", BIASES if BIASES else ["Sesgo de confirmación", "Heurística de disponibilidad"])
    situacion = st.text_input("Situación")
    pensamiento = st.text_area("Pensamiento automático", height=90)
    alternativa = st.text_area("Alternativa más realista (o más falsable)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"situacion": situacion, "pensamiento": pensamiento, "alternativa": alternativa}
        guardar_respuesta(6, f, f"Sesgo — {sesgo}", alternativa, meta=meta)

# ---------- BLOQUE 7 ----------
elif menu == "Bloque 7: El Abogado del Diablo":
    st.header("Bloque 7: El abogado del diablo")
    st.write("No es autoataque: es higiene mental.")
    f = fecha_bloque(7)

    card("Registro", subtitle="Frase literal → evidencia → nueva formulación.", enunciado="Cuando el relato se vuelve dogma, se pincha el globo.")
    creencia = st.text_input("Creencia limitante (literal)")
    evidencia = st.text_area("Evidencia que la contradice (hechos, no deseo)", height=110)
    nueva = st.text_area("Nueva formulación (más realista / más útil)", height=90)
    card_end()

    if st.button("Guardar registro"):
        meta = {"evidencia": evidencia}
        guardar_respuesta(7, f, f"Abogado del diablo — {creencia}", nueva, meta=meta)

# ---------- BLOQUE 8 ----------
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

# ---------- BLOQUE 9 ----------
elif menu == "Bloque 9: El Nuevo Rumbo":
    st.header("Bloque 9: El nuevo rumbo")
    st.write("Cierre del recorrido. Integración: pocas ideas, mucha verdad.")
    f = fecha_bloque(9)

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

# ---------- MIS RESPUESTAS ----------
elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Mis respuestas")

    df = df_all.copy()
    if df.empty:
        st.write("Aún no tienes registros guardados.")
    else:
        df["fecha_sort"] = df["fecha"].apply(lambda x: to_sortable_date(x) if isinstance(x, str) else None)
        df["ts_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["ts_date"] = df["ts_dt"].dt.date

        # Panel de métricas arriba (producto)
        st.markdown("### Progreso y adherencia")
        metrics = compute_adherence_metrics(df, st.session_state.perfil)
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Racha actual", f"{metrics['streak']}")
        with c2:
            st.metric("Mejor racha", f"{metrics['best_streak']}")
        with c3:
            st.metric("Días activos", f"{metrics['active_days']}")
        with c4:
            st.metric("Días desde inicio", f"{metrics['days_total']}")
        with c5:
            st.metric("Constancia", f"{metrics['active_rate']*100:.0f}%")

        st.markdown("---")

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

            # Distribución por bloque
            by_block = dff.groupby("bloque").size().reindex(range(1, 10), fill_value=0).reset_index(name="registros")
            if PLOTLY_AVAILABLE:
                fig_bar = px.bar(by_block, x="bloque", y="registros", title="Distribución por bloque")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.bar_chart(by_block.set_index("bloque"))

        with tab3:
            st.markdown("### Insights")
            # Insight simple: bloque más usado y día más activo
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
                    p = st.session_state.perfil
                    obj_d = int(p.get("objetivo_dias_semana", 5))
                    obj_b = int(p.get("objetivo_bloques_dia", 1))
                    card("Objetivo", enunciado="Diseño de adherencia (no de perfección).")
                    st.write(f"**Objetivo días/semana:** {obj_d}")
                    st.write(f"**Objetivo bloques/día:** {obj_b}")
                    st.write("Si hoy estás sin gasolina, haz 1 bloque. Si estás bien, haz 2. Si estás brillante, no te vengas arriba: repite mañana.")
                    card_end()
            else:
                st.write("Sin datos en el rango filtrado.")

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
