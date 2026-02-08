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
# ESTILOS (Branding)
# =========================================================
st.markdown(
    f"""
    <style>
      .stApp {{ background: {BRAND_WHITE}; }}

      /* Sidebar */
      section[data-testid="stSidebar"] {{
        background: {BRAND_BLUE};
      }}
      section[data-testid="stSidebar"] * {{
        color: {BRAND_WHITE} !important;
      }}

      /* Menú (radio): texto en amarillo + negrita */
      section[data-testid="stSidebar"] div[role="radiogroup"] * {{
        color: {BRAND_YELLOW} !important;
        font-weight: 800 !important;
      }}

      /* Radio seleccionado: marca amarilla (si el navegador respeta accent-color) */
      section[data-testid="stSidebar"] input[type="radio"] {{
        accent-color: {BRAND_YELLOW} !important;
      }}

      /* Títulos */
      h1, h2, h3, h4 {{ color: {BRAND_BLUE} !important; }}

      /* Botones */
      div.stButton > button {{
        background-color: {BRAND_BLUE} !important;
        color: {BRAND_YELLOW} !important;
        border: 0px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        padding: 0.55rem 1rem !important;
      }}
      div.stButton > button:hover {{
        filter: brightness(0.95);
      }}

      /* Inputs */
      .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        border-radius: 10px !important;
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
    st.title("Azimut")
    st.write(
        "Esta app es un cuaderno de navegación: no para *pensar más*, sino para **pensar mejor**.\n\n"
        "La idea es sencilla y obstinada: **cada día** completas el bloque (o bloques) que te toquen, "
        "sin necesidad de hacerlo perfecto. Al principio costará —como afinar el oído en una sala con eco—, "
        "pero con los días notarás algo muy concreto: **identificarás antes lo que te pasa**, "
        "y tus explicaciones tendrán más precisión y menos niebla.\n\n"
        "Esa mejora no es un sentimiento: es **evidencia**. Se ve en el detalle, en la claridad, "
        "en la rapidez con la que nombras una emoción, detectas un sesgo o encuentras el punto exacto del cuerpo "
        "donde se tensó el sistema.\n\n"
        "Tus respuestas se guardan en **“📊 MIS RESPUESTAS”**. Ahí podrás revisar el historial por bloques y por fecha, "
        "ver **qué patrones se repiten**, y también el avance en otros puntos (más matices, más contexto, mejores reencuadres).\n\n"
        "Deja **“Bloque 9: El Nuevo Rumbo”** para el final: es el cierre del programa, cuando hayas completado el recorrido."
    )

# --- BLOQUE 1 ---
elif menu == "Bloque 1: Vía Negativa":
    st.header("📉 Bloque 1: Vía Negativa")
    st.write("Identifica lo que resta. Hoy no añadimos herramientas: quitamos lastre.")

    f = fecha_bloque(1)
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?")
    if st.button("Guardar compromiso"):
        guardar_respuesta(1, f, "Vía negativa — Resta del día", dato)

# --- BLOQUE 2 ---
elif menu == "Bloque 2: Ritmos Circadianos":
    st.header("☀️ Bloque 2: Sincronización biológica")
    st.write("Marca los puntos que has cumplido hoy (10–12 anclas diarias).")

    f = fecha_bloque(2)
    seleccionados = []
    for item in CHECKLIST_BLOCK2:
        if st.checkbox(item):
            seleccionados.append(item)

    if st.button("Guardar registro"):
        guardar_respuesta(2, f, "Ritmos circadianos — Hitos", ", ".join(seleccionados))

# --- BLOQUE 3 ---
elif menu == "Bloque 3: Marcadores Somáticos":
    st.header("🧘 Bloque 3: Marcadores somáticos")
    st.write("El cuerpo habla en dialectos: tensión, nudo, calor, vacío. Vamos a transcribirlo.")

    f = fecha_bloque(3)
    zona = st.selectbox(
        "¿Dónde lo sientes?",
        ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros", "Cabeza", "Cuello", "Espalda", "Manos", "Brazos", "Piernas", "Pies"],
    )
    tipo = st.text_input("Describe la sensación (calor, nudo, presión, hormigueo, pesadez...):")
    if st.button("Guardar registro"):
        guardar_respuesta(3, f, f"Marcador somático — Localización: {zona}", tipo)

# --- BLOQUE 4 ---
elif menu == "Bloque 4: Registro de Precisión":
    st.header("🏷️ Bloque 4: Precisión emocional (registro diario)")
    st.write("Aquí el objetivo no es ‘sentir menos’, sino **nombrar mejor**.")

    f = fecha_bloque(4)

    emo = st.selectbox("Emoción detectada:", EMOTIONS if EMOTIONS else ["Ansiedad", "Frustración", "Paz", "Gratitud"])
    por_que = st.text_area("¿Por qué crees que era esa emoción?", height=90)
    donde = st.text_input("¿Dónde estabas? (contexto físico)")
    que_paso = st.text_area("¿Qué pasó para sentir eso? (hechos, no juicio)", height=110)

    if st.button("Guardar registro"):
        meta = {"por_que": por_que, "donde": donde, "que_paso": que_paso}
        guardar_respuesta(4, f, "Precisión emocional — Etiquetado", emo, meta=meta)

# --- BLOQUE 5 ---
elif menu == "Bloque 5: Gestión de Recursos":
    st.header("🧬 Bloque 5: Gestión de recursos")
    st.write("Un recurso es aquello que te deja más capaz después de usarlo, no más roto.")

    f = fecha_bloque(5)

    st.caption("Ejemplos (por si hoy tu mente viene con la persiana a medio bajar):")
    st.write(
        "- Sueño / descanso real\n- Calma / respiración\n- Apoyo social\n- Orden del entorno\n- Movimiento\n"
        "- Nutrición simple\n- Tiempo sin pantallas\n- Límites / decir NO\n- Planificación mínima viable\n"
        "- Exposición a luz y aire"
    )

    recurso = st.text_input("¿Qué recurso has fortalecido hoy?")
    p = st.text_area("¿Por qué ese recurso era importante hoy?", height=80)
    c = st.text_area("¿Cómo lo hiciste? (acciones concretas)", height=90)
    s = st.text_area("¿Cómo te sientes después de haberlo hecho?", height=80)

    if st.button("Guardar registro"):
        meta = {"por_que": p, "como": c, "despues": s}
        guardar_respuesta(5, f, "Gestión de recursos — Recurso fortalecido", recurso, meta=meta)

# --- BLOQUE 6 ---
elif menu == "Bloque 6: Detector de Sesgos":
    st.header("⚖️ Bloque 6: Detector de sesgos")
    st.write("Sesgo = el piloto automático defendiendo su ruta como si fuera ley natural.")

    f = fecha_bloque(6)

    sesgo = st.selectbox("Sesgo identificado hoy:", BIASES if BIASES else ["Sesgo de confirmación", "Anclaje", "Efecto halo"])
    obs = st.text_area("Contexto de la situación (qué pasó, qué pensaste, qué hiciste):", height=120)

    if st.button("Guardar registro"):
        guardar_respuesta(6, f, f"Sesgos — {sesgo}", obs)

# --- BLOQUE 7 ---
elif menu == "Bloque 7: El Abogado del Diablo":
    st.header("😈 Bloque 7: El abogado del diablo")
    st.write("No se trata de autoatacarte. Se trata de pinchar el globo del relato cuando se vuelve dogma.")

    f = fecha_bloque(7)

    st.caption("Ejemplos de creencias limitantes (del corpus):")
    for b in BELIEF_EXAMPLES:
        st.write(f"- {b}")

    creencia = st.text_input("Creencia limitante detectada (tu versión exacta):")
    st.caption("Pistas si te cuesta:")
    st.write(
        "- Escribe la frase tal como aparece, sin maquillarla.\n"
        "- Pregunta: ¿esto es un **dato** o una **sentencia**?\n"
        "- Si tu mejor amiga dijera esto, ¿qué le responderías?\n"
        "- ¿Qué evidencia reciente contradice la creencia, aunque sea pequeña?"
    )
    contra = st.text_area("Evidencia real que la contradice (hechos, ejemplos, datos):", height=140)

    if st.button("Guardar registro"):
        guardar_respuesta(7, f, f"Abogado del diablo — Creencia: {creencia}", contra)

# --- BLOQUE 8 ---
elif menu == "Bloque 8: Antifragilidad":
    st.header("💎 Bloque 8: Antifragilidad")
    st.write("No romantizamos el caos. Lo usamos como fertilizante cuando ya ha ocurrido.")

    f = fecha_bloque(8)

    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    st.caption("Pistas si te cuesta extraer aprendizaje/beneficio:")
    st.write(
        "- ¿Qué habilidad entrenaste sin querer (paciencia, límites, adaptación)?\n"
        "- ¿Qué información nueva apareció gracias a esto?\n"
        "- Si esto se repitiera, ¿qué harías distinto la próxima vez?\n"
        "- ¿Qué parte de tu control era ilusión?"
    )
    ventaja = st.text_area("¿Qué beneficio o aprendizaje has extraído?", height=120)

    if st.button("Guardar registro"):
        guardar_respuesta(8, f, f"Antifragilidad — Evento: {caos}", ventaja)

# --- BLOQUE 9 ---
elif menu == "Bloque 9: El Nuevo Rumbo":
    st.header("🧭 Bloque 9: Integración (una sola vez)")
    st.write("Lista de beneficios posibles tras el programa (compendio):")
    st.write("\n".join([f"- {x}" for x in BENEFITS_BLOCK9]))

    reflexion = st.text_area(
        "Tu reflexión final (qué aprendiste, cómo avanzaste por bloques, qué te costó, qué gestionas mejor ahora):",
        height=180,
    )
    if st.button("Guardar reflexión final"):
        guardar_respuesta(9, "", "Integración — Reflexión final", reflexion)
        st.balloons()

# --- MIS RESPUESTAS ---
elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Mis respuestas (por bloque → por fecha)")
    hist = st.session_state.historial

    if not hist:
        st.write("Aún no tienes registros guardados.")
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

        for bloque in sorted(df["bloque"].unique()):
            st.subheader(f"Bloque {bloque}")
            bdf = df[df["bloque"] == bloque].copy()

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
                for fecha in bdf["fecha"].unique():
                    st.markdown(f"### {fecha}")
                    fdf = bdf[bdf["fecha"] == fecha]
                    for _, row in fdf.iterrows():
                        st.markdown(f"**{row.get('concepto','')}**")
                        st.write(row.get("respuesta", ""))
                        meta = row.get("meta", {})
                        if isinstance(meta, dict) and meta:
                            st.caption("Detalles:")
                            st.json(meta)
                        st.divider()

        with st.expander("Ver tabla completa"):
            show = df.drop(columns=["fecha_sort"], errors="ignore")
            st.dataframe(show, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Limpiar todo el historial"):
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
