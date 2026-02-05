import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Azimut - Entrenamiento", page_icon="🧭", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007BFF; color: white; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL ---
st.sidebar.title("🧭 Navegación Azimut")
menu = st.sidebar.radio("Ir a la fase:", [
    "Inicio", 
    "Semana 1: Vía Negativa", 
    "Semana 3: Marcadores Somáticos",
    "Semana 4: Fórmula de Resiliencia"
])

# --- PÁGINA DE INICIO ---
if menu == "Inicio":
    st.title("Bienvenido a tu Brújula")
    st.write("Esta app es el soporte práctico de tu programa **Azimut**. Aquí registrarás tus avances y entrenarás tu neurobiología.")
    st.image("https://images.unsplash.com/photo-1506784919141-93504993957f?auto=format&fit=crop&w=800&q=80", caption="El camino se hace restando.")

# --- SEMANA 1: VÍA NEGATIVA ---
elif menu == "Semana 1: Vía Negativa":
    st.header("📉 Semana 1: Vía Negativa")
    st.subheader("Quitar primero lo que sobra")
    
    st.info("Popularizado por Nassim Taleb: eliminar lo que hace daño produce más beneficio que añadir soluciones nuevas.")
    
    malestar = st.text_area("¿Qué situación te drena energía hoy?")
    if malestar:
        peor = st.text_area("Si quisieras que esto empeorara drásticamente, ¿qué harías?")
        if peor:
            st.warning("⚠️ **Tu estrategia para hoy:** Simplemente deja de hacer lo que escribiste arriba.")
            if st.button("Guardar compromiso de resta"):
                st.success("Compromiso registrado. Menos es más.")

# --- SEMANA 3: MARCADORES SOMÁTICOS ---
elif menu == "Semana 3: Marcadores Somáticos":
    st.header("🧘 Marcadores Somáticos")
    st.write("Identifica dónde se 'ancla' la emoción en tu cuerpo para reducir la activación de la amígdala.")
    
    emocion = st.selectbox("¿Qué sientes ahora?", ["Ansiedad/Miedo", "Ira/Frustración", "Tristeza/Duelo", "Calma/Gratitud"])
    
    st.write("### Mapa Corporal")
    col1, col2 = st.columns(2)
    
    with col1:
        zonas = st.multiselect("¿En qué zona notas la sensación?", 
                             ["Cuello/Garganta", "Pecho", "Abdomen", "Mandíbula", "Hombros"])
    with col2:
        tipo = st.radio("Tipo de sensación:", ["Calor", "Presión/Peso", "Nudo", "Vacío", "Hormigueo"])
    
    intensidad = st.select_slider("Intensidad (1 al 10)", options=list(range(1, 11)))
    
    if st.button("Registrar Sensación"):
        st.write(f"✅ Has nombrado tu emoción como **{emocion}** con una intensidad de **{intensidad}**. Esto ya está bajando tu reactividad emocional.")

# --- SEMANA 4: RESILIENCIA ---
elif menu == "Semana 4: Fórmula de Resiliencia":
    st.header("🧬 Fórmula de la Resiliencia")
    st.latex(r''' Resiliencia = \frac{Reto}{Recursos} ''')
    
    st.write("Para aumentar tu resiliencia, puedes o bajar el reto o **subir tus recursos**.")
    recurso = st.text_input("¿Qué recurso (sueño, respiración, apoyo) vas a fortalecer hoy?")
    
    if recurso:
        st.success(f"Recurso '{recurso}' activado. Has equilibrado la balanza.")
