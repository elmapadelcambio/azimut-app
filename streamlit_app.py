import streamlit as st

st.set_page_config(page_title="Azimut: Entrenamiento Completo", page_icon="🧭", layout="wide")

# --- NAVEGACIÓN ---
st.sidebar.title("🧭 Programa Azimut")
st.sidebar.markdown("---")
fase = st.sidebar.selectbox("Selecciona la Fase de tu Entrenamiento:", [
    "1. Limpieza y Ritmos (Sem. 1-2)",
    "2. Neurobiología y Cuerpo (Sem. 3-5)",
    "3. Sesgos y Narrativas (Sem. 6-7)",
    "4. Antifragilidad y Rumbo (Sem. 8-9)"
])

# --- FASE 1: LIMPIEZA ---
if fase == "1. Limpieza y Ritmos (Sem. 1-2)":
    st.title("🛡️ Fase 1: Despejar el Camino")
    tab1, tab2 = st.tabs(["Vía Negativa", "Higiene de Luz"])
    
    with tab1:
        st.subheader("La Vía Negativa")
        st.write("¿Qué conducta vas a **eliminar** hoy para ganar claridad?")
        resta = st.text_input("Hoy voy a dejar de...", placeholder="Ej: Mirar el móvil al despertar")
        if resta: st.success(f"Objetivo: Menos es más. Has eliminado: {resta}")

    with tab2:
        st.subheader("Ritmos Circadianos")
        st.write("¿Has recibido luz solar directa hoy?")
        luz = st.checkbox("Sí, he salido al exterior al menos 10 min.")
        if luz: st.balloons()

# --- FASE 2: NEUROBIOLOGÍA ---
elif fase == "2. Neurobiología y Cuerpo (Sem. 3-5)":
    st.title("🧠 Fase 2: El Cuerpo como Brújula")
    
    st.subheader("Precisión Emocional")
    emocion = st.select_slider("¿Cuál es la intensidad de tu emoción?", options=["Baja", "Media", "Alta", "Desbordante"])
    
    st.write("### Escáner de Marcadores Somáticos")
    st.write("¿Dónde sientes la emoción?")
    
    col1, col2 = st.columns(2)
    with col1:
        zona = st.multiselect("Zonas:", ["Garganta", "Pecho", "Estómago", "Mandíbula"])
    with col2:
        sensacion = st.radio("Sensación:", ["Presión", "Calor", "Vacío", "Tensión"])
    
    if st.button("Registrar en mi Mapa"):
        st.info(f"Registrado: Sentimiento en {zona} como {sensacion}. La amígdala se está regulando...")

# --- FASE 3: SESGOS ---
elif fase == "3. Sesgos y Narrativas (Sem. 6-7)":
    st.title("⚖️ Fase 3: El Abogado del Diablo")
    st.write("Identifica el sesgo que está dominando tu pensamiento.")
    sesgo = st.selectbox("¿Qué trampa mental detectas?", ["Sesgo de Confirmación", "Negatividad", "Anclaje"])
    pensamiento = st.text_area("¿Cuál es el pensamiento limitante?")
    if pensamiento:
        st.warning(f"**Reto del Abogado del Diablo:** Escribe una prueba real de que '{pensamiento}' NO es 100% cierto.")
        prueba = st.text_input("Evidencia en contra:")

# --- FASE 4: ANTIFRAGILIDAD ---
elif fase == "4. Antifragilidad y Rumbo (Sem.
