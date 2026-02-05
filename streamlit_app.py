import streamlit as st

# Configuración profesional
st.set_page_config(page_title="Azimut: Programa Completo", page_icon="🧭")

# --- SIDEBAR: LAS 9 SEMANAS ---
st.sidebar.title("Navegación Azimut")
semana = st.sidebar.select_slider(
    "Selecciona la semana de entrenamiento:",
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9]
)

st.sidebar.info(f"Estás en la Semana {semana}")

# --- CONTENIDO DINÁMICO SEGÚN EL DOCUMENTO ---

if semana == 1:
    st.header("Semana 1: Vía Negativa")
    st.write("Antes de sumar, toca restar. Identifica qué te sobra.")
    resta = st.text_input("¿Qué hábito o conducta vas a ELIMINAR hoy?")
    if resta:
        st.success(f"Compromiso: Menos es más. Hoy dejas atrás: {resta}")

elif semana == 2:
    st.header("Semana 2: Ritmos y Entorno")
    st.write("Ajusta tu biología a la luz solar.")
    luz = st.radio("¿Has recibido luz solar directa en los primeros 20 min del día?", ["No", "Sí"])
    if luz == "Sí": st.balloons()

elif semana in [3, 4, 5]:
    st.header(f"Semana {semana}: El Cuerpo y la Emoción")
    st.subheader("Mapa de Marcadores Somáticos")
    st.write("Localiza la sensación física para calmar la amígdala.")
    
    
    
    col1, col2 = st.columns(2)
    with col1:
        zona = st.selectbox("¿Dónde lo sientes?", ["Pecho", "Garganta", "Estómago", "Hombros", "Mandíbula"])
    with col2:
        tipo = st.selectbox("Tipo de sensación:", ["Presión", "Calor", "Vibración", "Nudo"])
        
    if st.button("Registrar Marcador"):
        st.info(f"Registrado: {tipo} en {zona}. Observa la sensación sin juzgarla.")

elif semana in [6, 7]:
    st.header("Semanas 6-7: Sesgos y Narrativas")
    st.write("Cuestiona tu propia historia (El Abogado del Diablo).")
    pensamiento = st.text_area("¿Qué pensamiento te está limitando hoy?")
    if pensamiento:
        st.warning(f"Reto: Escribe una prueba objetiva de que '{pensamiento}' NO es verdad.")
        contraprueba = st.text_input("Evidencia contraria:")

elif semana in [8, 9]:
    st.header("Semanas 8-9: Antifragilidad")
    st.write("Usa el caos para fortalecerte.")
    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    if caos:
        st.success(f"Enfoque Azimut: ¿Cómo puedes usar este '{caos}' a tu favor?")

# --- PIE DE PÁGINA ---
st.sidebar.markdown("---")
st.sidebar.write("© 2024 Azimut - Entrenamiento Neurobiológico")
