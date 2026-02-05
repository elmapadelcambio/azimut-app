import streamlit as st

st.set_page_config(page_title="Azimut App", page_icon="🧭")

# --- NAVEGACIÓN ---
page = st.sidebar.radio("Ir a:", ["Inicio", "Semana 1: Vía Negativa", "Semana 3: Marcadores Somáticos"])

if page == "Inicio":
    st.title("🧭 Bienvenid@ a Azimut")
    st.markdown("""
    Esta herramienta complementa tu programa de entrenamiento neurobiológico.
    
    **Pasos recomendados:**
    1. Identifica qué te sobra (**Vía Negativa**).
    2. Localiza la emoción en tu cuerpo (**Marcadores Somáticos**).
    """)

elif page == "Semana 1: Vía Negativa":
    st.title("🗑️ Vía Negativa")
    st.write("Identifica una conducta que hoy vas a **eliminar** para ganar claridad.")
    item = st.text_input("¿Qué vas a dejar de hacer hoy?")
    if item:
        st.success(f"Compromiso adquirido: Hoy NO voy a {item}")

elif page == "Semana 3: Marcadores Somáticos":
    st.title("🧘 Escáner Corporal")
    st.write("¿En qué parte de tu cuerpo sientes la emoción actual?")
    
    # Simulación de mapa corporal
    parte = st.multiselect(
        "Selecciona las zonas donde notas tensión, calor o presión:",
        ["Garganta (nudo)", "Pecho (opresión)", "Estómago (mariposas/vacío)", "Hombros (carga)", "Mandíbula (tensión)"]
    )
    
    intensidad = st.slider("Intensidad de la sensación física:", 1, 10, 5)
    
    if parte:
        st.info(f"Nivel de activación: {intensidad}/10. Respira llevando el aire hacia: {', '.join(parte)}.")
