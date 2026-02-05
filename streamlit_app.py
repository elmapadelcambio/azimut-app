import streamlit as st

st.set_page_config(page_title="Azimut - Entrenamiento 9 Semanas", page_icon="🧭", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stSelectbox label, .stSlider label { font-weight: bold; color: #1E3A8A; }
    .css-1n76uvr { background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
st.sidebar.title("🧭 Navegación Azimut")
semana = st.sidebar.selectbox("Selecciona la semana actual:", [
    "Semana 1: Vía Negativa",
    "Semana 2: Ritmos Circadianos",
    "Semana 3: Marcadores Somáticos",
    "Semana 4: Precisión Emocional",
    "Semana 5: Fórmula de Resiliencia",
    "Semana 6: Sesgos Cognitivos",
    "Semana 7: El Abogado del Diablo",
    "Semana 8: Antifragilidad",
    "Semana 9: El Nuevo Rumbo"
])

# --- LÓGICA DE CONTENIDO POR SEMANA ---

if semana == "Semana 1: Vía Negativa":
    st.header("📉 Semana 1: Limpiar el Armario")
    st.write("Identifica y resta para ganar.")
    opcion = st.text_input("¿Qué hábito específico vas a ELIMINAR hoy para reducir ruido mental?")
    if opcion: st.success(f"Compromiso: No haré '{opcion}'. Menos es más.")

elif semana == "Semana 2: Ritmos Circadianos":
    st.header("☀️ Semana 2: Sincronización Biológica")
    st.write("Cuestionario de higiene de luz:")
    luz = st.checkbox("¿He recibido luz solar directa antes de las 10:00 AM?")
    pantallas = st.checkbox("¿He usado filtro de luz azul o evitado pantallas tras el ocaso?")
    if luz and pantallas: st.balloons()

elif semana == "Semana 3: Marcadores Somáticos":
    st.header("🧘 Semana 3: Localización Corporal")
    st.write("No pienses la emoción, siéntela.")
    
    zona = st.multiselect("¿Dónde notas la activación física?", ["Garganta", "Pecho", "Abdomen", "Hombros", "Mandíbula"])
    tipo = st.radio("Cualidad de la sensación:", ["Calor", "Frío", "Presión", "Hormigueo", "Vacío"])
    if st.button("Registrar en mi mapa"): st.info("Sensación registrada. Observar el cuerpo calma la amígdala.")

elif semana == "Semana 4: Precisión Emocional":
    st.header("🏷️ Semana 4: Etiquetado de Precisión")
    st.write("Nombra la emoción con exactitud para reducir su carga.")
    base = st.selectbox("Emoción base:", ["Ira", "Miedo", "Tristeza", "Alegría"])
    matiz = {
        "Ira": ["Frustración", "Indignación", "Fastidio"],
        "Miedo": ["Inquietud", "Desasosiego", "Aprensión"],
        "Tristeza": ["Melancolía", "Desgana", "Pena"],
        "Alegría": ["Gratitud", "Paz", "Euforia"]
    }
    exacta = st.select_slider("Elige el matiz exacto:", options=matiz[base])
    st.write(f"Has identificado: **{exacta}**.")

elif semana == "Semana 5: Fórmula de Resiliencia":
    st.header("🧬 Semana 5: Equilibrar la Balanza")
    st.latex(r''' Resiliencia = \frac{Reto}{Recursos} ''')
    reto = st.slider("Nivel de reto/estrés hoy:", 1, 10, 5)
    recurso = st.text_input("¿Qué recurso vas a subir hoy (Sueño, Deporte, Respiración)?")
    if recurso: st.success(f"Resiliencia aumentada mediante: {recurso}")

elif semana == "Semana 6: Sesgos Cognitivos":
    st.header("⚖️ Semana 6: Trampas Mentales")
    sesgo = st.selectbox("¿Qué sesgo detectas en tu juicio hoy?", ["Confirmación (solo veo lo que me da la razón)", "Negatividad (solo veo lo malo)", "Anclaje (me quedo con la primera idea)"])
    ejemplo = st.text_area("Describe un pensamiento de hoy que podría estar sesgado:")
    if ejemplo: st.warning("Has detectado el filtro. Ahora puedes ver la realidad.")

elif semana == "Semana 7: El Abogado del Diablo":
    st.header("😈 Semana 7: Desmontando Narrativas")
    creencia = st.text_input("Escribe una creencia absoluta que tengas hoy (Ej: 'No valgo para esto')")
    if creencia:
        st.write(f"**Reto del Abogado del Diablo:** Escribe 3 evidencias REALES que contradigan que '{creencia}' sea verdad.")
        st.text_area("Evidencias en contra:")

elif semana == "Semana 8: Antifragilidad":
    st.header("💎 Semana 8: El Beneficio del Caos")
    st.write("Lo resiliente aguanta; lo antifrágil mejora con el golpe.")
    caos = st.text_input("¿Qué imprevisto o error ha ocurrido esta semana?")
    beneficio = st.text_input("¿Qué aprendizaje o ventaja puedes extraer de ese error?")
    if beneficio: st.success("Has convertido el estrés en combustible.")

elif semana == "Semana 9: El Nuevo Rumbo":
    st.header("🧭 Semana 9: Integración y Azimut")
    st.write("Tu nueva brújula está calibrada.")
    reflexion = st.text_area("¿Cuál es la principal diferencia entre quien empezó la Semana 1 y quien eres hoy?")
    if st.button("Finalizar Programa"):
        st.balloons()
        st.header("¡Buen viaje, Azimut!")
