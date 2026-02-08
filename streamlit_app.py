import json
import re
from datetime import datetime, date
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURACIÓN Y BRANDING
# =========================================================
st.set_page_config(page_title="Azimut - Programa de Claridad", page_icon="🧭", layout="wide")

BRAND_BLUE = "#00a7ff"
BRAND_YELLOW = "#f9e205"
BRAND_WHITE = "#ffffff"

# Estilos CSS para mejorar la UI de Streamlit
st.markdown(f"""
    <style>
    .main {{ background-color: #fcfcfc; }}
    .stMetric {{ 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid {BRAND_BLUE}; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }}
    .insight-card {{ 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #eee; 
        border-left: 5px solid {BRAND_YELLOW}; 
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    .block-header {{
        color: {BRAND_BLUE};
        font-weight: bold;
        border-bottom: 2px solid {BRAND_YELLOW};
        padding-bottom: 5px;
        margin-bottom: 20px;
    }}
    div.stButton > button {{
        background-color: {BRAND_BLUE};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }}
    div.stButton > button:hover {{
        background-color: #0086cc;
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# Archivos y Persistencia
AZIMUT_FILE = Path("azimutrenovadocompleto.txt")
NEWSLETTERS_FILE = Path("AA-TODAS las newsletters publicadas .txt")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

# =========================================================
# UTILIDADES Y CARGA DE DATOS
# =========================================================
def load_text(path: Path) -> str:
    if not path.exists(): return ""
    try: return path.read_text(encoding="utf-8", errors="ignore")
    except: return ""

AZIMUT_TEXT = load_text(AZIMUT_FILE)
NEWS_TEXT = load_text(NEWSLETTERS_FILE)

def load_history():
    if HISTORY_FILE.exists():
        try: return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except: return []
    return []

def save_history(hist):
    HISTORY_FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")

if "historial" not in st.session_state:
    st.session_state.historial = load_history()

def guardar_respuesta(bloque, fecha_str, concepto, respuesta, meta=None):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bloque": int(bloque),
        "fecha": fecha_str,
        "concepto": concepto,
        "respuesta": respuesta,
        "meta": meta or {},
    }
    st.session_state.historial.append(entry)
    save_history(st.session_state.historial)
    st.toast(f"✅ Guardado en Bloque {bloque}")

# Extracciones dinámicas (Simificadas para el ejemplo, usa tus funciones originales)
EMOTIONS = ["Amor", "Miedo", "Tristeza", "Ira", "Alegría", "Vergüenza", "Asco", "Sorpresa", "Calma", "Ilusión", "Culpa"]
CHECKLIST_BLOCK2 = [
    "Me acuesto y levanto a horas consistentes", "Dormitorio fresco/oscuro", 
    "Sin pantallas antes de dormir", "Luz natural al despertar", "Movimiento temprano"
]
BIASES = ["Sesgo de confirmación", "Efecto Dunning-Kruger", "Sesgo de negatividad", "Disonancia cognitiva"]

# =========================================================
# NAVEGACIÓN
# =========================================================
with st.sidebar:
    st.title("🧭 Azimut")
    st.markdown("---")
    menu = st.radio(
        "Navegación:",
        ["Inicio", "Bloque 1: Vía Negativa", "Bloque 2: Ritmos Circadianos", 
         "Bloque 3: Marcadores Somáticos", "Bloque 4: Precisión Emocional", 
         "Bloque 5: Gestión de Recursos", "Bloque 6: Detector de Sesgos", 
         "Bloque 7: El Abogado del Diablo", "Bloque 8: Antifragilidad", 
         "Bloque 9: El Nuevo Rumbo", "📊 MIS RESPUESTAS"]
    )
    st.markdown("---")
    if st.session_state.historial:
        st.caption(f"Registros totales: {len(st.session_state.historial)}")

# Utilidad para fecha
def fecha_bloque(bloque: int):
    d = st.date_input("Fecha del registro", value=date.today(), key=f"f_{bloque}")
    return d.strftime("%d/%m/%Y")

# =========================================================
# PANTALLAS
# =========================================================

if menu == "Inicio":
    st.title("Bienvenido a Azimut")
    st.subheader("Tu cuaderno de navegación para pensar mejor.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
        Esta aplicación está diseñada para ayudarte a identificar patrones, nombrar emociones con precisión 
        y detectar los sesgos que nublan tu juicio diario. 
        
        **Cómo usar esta app:**
        1. Completa el bloque que te corresponda hoy.
        2. No busques la perfección, busca la **precisión**.
        3. Revisa la sección de **Mis Respuestas** para ver los hallazgos que la app detecta por ti.
        """)
    with col2:
        st.info("💡 **Consejo:** Empieza por el Bloque 1 si es tu primera vez.")

elif menu == "Bloque 4: Precisión Emocional":
    st.markdown("<h2 class='block-header'>🏷️ Bloque 4: Precisión Emocional</h2>", unsafe_allow_html=True)
    f = fecha_bloque(4)
    
    emo = st.selectbox("¿Qué emoción detectas?", EMOTIONS)
    por_que = st.text_area("¿Por qué crees que era esa emoción?")
    donde = st.text_input("¿Dónde estabas? (Contexto)")
    que_paso = st.text_area("¿Qué pasó exactamente? (Hechos)")
    
    if st.button("Guardar Registro Emocional"):
        meta = {"por_que": por_que, "donde": donde, "que_paso": que_paso}
        guardar_respuesta(4, f, "Etiquetado Emocional", emo, meta)

# (Aquí irían los demás bloques 1, 2, 3, 5, 6, 7, 8 siguiendo tu lógica original...)

elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Análisis de Progreso")
    
    hist = st.session_state.historial
    if not hist:
        st.warning("Aún no hay datos para analizar. ¡Empieza a registrar hoy!")
    else:
        df = pd.DataFrame(hist)
        df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y')

        # Filtro de Fecha
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            rango = st.date_input("Rango de análisis", 
                                value=[df['fecha_dt'].min(), df['fecha_dt'].max()])
        
        if len(rango) == 2:
            df_filtered = df[(df['fecha_dt'] >= pd.to_datetime(rango[0])) & (df['fecha_dt'] <= pd.to_datetime(rango[1]))]
        else:
            df_filtered = df

        # --- SECCIÓN DE HALLAZGOS (INSIGHTS) ---
        st.subheader("💡 Hallazgos Clave")
        c1, c2, c3 = st.columns(3)
        
        # Lógica de Insights
        df_emo = df_filtered[df_filtered['bloque'] == 4]
        emocion_frecuente = df_emo['respuesta'].mode().iloc[0] if not df_emo.empty else "N/A"
        contexto_frecuente = df_emo['meta'].apply(lambda x: x.get('donde', 'N/A')).mode().iloc[0] if not df_emo.empty else "N/A"

        c1.metric("Total Registros", len(df_filtered))
        c2.metric("Emoción Principal", emocion_frecuente)
        c3.metric("Contexto Clave", contexto_frecuente)

        # Recomendaciones Dinámicas
        st.markdown("### 🌱 Recomendaciones Azimut")
        if emocion_frecuente in ["Miedo", "Ira", "Ansiedad"]:
            st.markdown(f"""<div class='insight-card'>
                <strong>Atención detectada:</strong> Tu emoción más frecuente es <b>{emocion_frecuente}</b>. 
                Sugerimos priorizar el <b>Bloque 2</b> para estabilizar ritmos circadianos y reducir la reactividad del sistema nervioso.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='insight-card'>
                <strong>Buen camino:</strong> Mantienes una variedad saludable de etiquetas. 
                Sigue profundizando en el <b>Bloque 6</b> para detectar sesgos ocultos en tus momentos de calma.
            </div>""", unsafe_allow_html=True)

        # --- GRÁFICOS ---
        tab1, tab2 = st.tabs(["📈 Actividad", "📊 Distribución Emocional"])
        
        with tab1:
            actividad = df_filtered.groupby('fecha').size().reset_index(name='cuenta')
            fig_line = px.line(actividad, x='fecha', y='cuenta', title="Frecuencia de Registros",
                              line_shape="spline", color_discrete_sequence=[BRAND_BLUE])
            st.plotly_chart(fig_line, use_container_width=True)
            
        with tab2:
            if not df_emo.empty:
                emo_counts = df_emo['respuesta'].value_counts().reset_index()
                fig_bar = px.bar(emo_counts, x='count', y='respuesta', orientation='h',
                                title="Emociones Identificadas", color_discrete_sequence=[BRAND_YELLOW])
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No hay datos emocionales en este rango.")

        # --- TABLA Y EXPORTACIÓN ---
        st.divider()
        with st.expander("Ver todos los registros detallados"):
            st.table(df_filtered[['fecha', 'bloque', 'concepto', 'respuesta']])
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            if st.button("🗑️ Borrar Historial"):
                st.session_state.historial = []
                save_history([])
                st.rerun()
        with col_ex2:
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte CSV", data=csv, file_name="azimut_reporte.csv")
