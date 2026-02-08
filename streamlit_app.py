import json
import re
from datetime import datetime, date
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# 1. CONFIGURACIÓN, BRANDING Y ESTILOS FORZADOS (BLANCO/NEGRO)
# =========================================================
st.set_page_config(page_title="Azimut - Programa de Claridad", page_icon="🧭", layout="wide")

BRAND_BLUE = "#00a7ff"
BRAND_YELLOW = "#f9e205"

st.markdown(f"""
    <style>
    /* Forzar fondo blanco y texto negro en toda la app */
    .stApp {{
        background-color: #FFFFFF;
        color: #000000;
    }}
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: #000000 !important;
    }}
    /* Estilo de tarjetas de métricas e insights */
    .insight-card {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        border-left: 6px solid {BRAND_BLUE};
        margin-bottom: 15px;
        color: #000000;
    }}
    .recommendation-card {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        border-left: 6px solid {BRAND_YELLOW};
        margin-bottom: 15px;
    }}
    /* Botones personalizados */
    div.stButton > button {{
        background-color: {BRAND_BLUE};
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
    }}
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #f8f9fa;
        border-right: 1px solid #eeeeee;
    }}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. PERSISTENCIA Y CARGA
# =========================================================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

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
    st.toast(f"✅ Registro guardado con éxito")

# =========================================================
# 3. NAVEGACIÓN LATERAL
# =========================================================
with st.sidebar:
    st.title("🧭 Azimut")
    st.subheader("Cuaderno de Navegación")
    menu = st.radio(
        "Ir a:",
        ["Inicio", "Bloque 1: Vía Negativa", "Bloque 2: Ritmos Circadianos", 
         "Bloque 4: Precisión Emocional", "📊 MIS RESPUESTAS"]
    )
    st.divider()
    st.caption("Programa de Claridad Mental y Precisión Emocional")

# =========================================================
# 4. PANTALLAS PRINCIPALES
# =========================================================

if menu == "Inicio":
    st.title("Bienvenido a Azimut")
    st.write("Esta app es una herramienta de precisión. Aquí no vienes a 'pensar más', sino a **pensar mejor**.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <h3>Objetivo de hoy</h3>
            <p>Identifica un automatismo, nómbralo y quítale poder. La claridad nace de la eliminación, no de la acumulación.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.info("💡 **Dato:** Los usuarios que registran su precisión emocional 3 veces por semana reducen su reactividad al estrés en un 40%.")

elif menu == "Bloque 4: Precisión Emocional":
    st.header("🏷️ Bloque 4: Precisión Emocional")
    fecha = st.date_input("Fecha", value=date.today()).strftime("%d/%m/%Y")
    
    emociones_lista = ["Ansiedad", "Paz", "Frustración", "Gratitud", "Miedo", "Ira", "Alegría", "Cansancio"]
    emo = st.selectbox("Selecciona la emoción detectada:", emociones_lista)
    contexto = st.text_input("¿Dónde estabas? (Contexto físico/situacional)")
    detalles = st.text_area("¿Qué hechos ocurrieron? (Evita juicios)")
    
    if st.button("Guardar Registro"):
        meta = {"contexto": contexto, "detalles": detalles}
        guardar_respuesta(4, fecha, "Etiquetado de Precisión", emo, meta)

# =========================================================
# 5. PANEL DE RESPUESTAS E INSIGHTS MEJORADO
# =========================================================
elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Análisis y Resultados")
    
    if not st.session_state.historial:
        st.warning("No hay registros disponibles. Comienza completando el Bloque 4.")
    else:
        df = pd.DataFrame(st.session_state.historial)
        df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y')

        # Filtro de fecha
        st.subheader("Filtros")
        rango = st.date_input("Selecciona el periodo de análisis:", 
                            value=[df['fecha_dt'].min(), df['fecha_dt'].max()])
        
        if len(rango) == 2:
            mask = (df['fecha_dt'] >= pd.to_datetime(rango[0])) & (df['fecha_dt'] <= pd.to_datetime(rango[1]))
            df_filtered = df.loc[mask]
        else:
            df_filtered = df

        # --- SECCIÓN DE INSIGHTS ---
        st.divider()
        st.subheader("💡 Hallazgos Inteligentes")
        
        c1, c2, c3 = st.columns(3)
        # Lógica para detectar patrones
        df_emo = df_filtered[df_filtered['bloque'] == 4]
        if not df_emo.empty:
            emo_top = df_emo['respuesta'].mode()[0]
            contexto_top = df_emo['meta'].apply(lambda x: x.get('contexto', 'N/A')).mode()[0]
            
            c1.metric("Registros", len(df_filtered))
            c2.metric("Emoción Dominante", emo_top)
            c3.metric("Contexto Recurrente", contexto_top)

            # Recomendación Dinámica
            st.markdown("### 🌱 Recomendación para tu semana")
            if emo_top in ["Ansiedad", "Miedo", "Frustración"]:
                st.markdown(f"""<div class="recommendation-card">
                    <strong>Patrón detectado:</strong> Hemos notado una tendencia hacia la <b>{emo_top}</b>, frecuentemente en <b>{contexto_top}</b>.<br><br>
                    <strong>Acción recomendada:</strong> Mañana, antes de entrar en ese contexto, dedica 2 minutos al <b>Bloque 2</b> (respiración y anclaje).
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="recommendation-card">
                    <strong>¡Buen trabajo!</strong> Tu estado dominante es <b>{emo_top}</b>. Aprovecha esta claridad para trabajar hoy en el <b>Bloque 1 (Vía Negativa)</b>.
                </div>""", unsafe_allow_html=True)

        # --- VISUALIZACIÓN ---
        st.divider()
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Gráfico de actividad
            actividad = df_filtered.groupby('fecha').size().reset_index(name='cuenta')
            fig_line = px.line(actividad, x='fecha', y='cuenta', title="Tu Constancia (Registros por día)",
                              color_discrete_sequence=[BRAND_BLUE])
            fig_line.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="black")
            st.plotly_chart(fig_line, use_container_width=True)

        with col_g2:
            # Gráfico de distribución emocional
            if not df_emo.empty:
                dist = df_emo['respuesta'].value_counts().reset_index()
                fig_bar = px.bar(dist, x='count', y='respuesta', orientation='h', title="Distribución de Emociones",
                                color_discrete_sequence=[BRAND_YELLOW])
                fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="black")
                st.plotly_chart(fig_bar, use_container_width=True)

        # --- HISTORIAL Y EXPORTACIÓN ---
        st.divider()
        with st.expander("Ver tabla completa de registros"):
            st.dataframe(df_filtered[['fecha', 'concepto', 'respuesta']], use_container_width=True)
        
        c_ex1, c_ex2 = st.columns(2)
        with c_ex1:
            if st.button("🗑️ Reiniciar Historial"):
                st.session_state.historial = []
                save_history([])
                st.rerun()
        with c_ex2:
            st.download_button("📥 Descargar Reporte CSV", 
                             data=df_filtered.to_csv(index=False).encode('utf-8'),
                             file_name=f"azimut_reporte_{date.today()}.csv")
