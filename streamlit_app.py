import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Azimut - Tu Brújula Interior", page_icon="🧭", layout="wide")

# --- INICIALIZACIÓN DE MEMORIA (Para guardar respuestas) ---
if 'historial' not in st.session_state:
    st.session_state.historial = []

def guardar_respuesta(semana, etiqueta, valor):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.historial.append({"Fecha": fecha, "Semana": semana, "Concepto": etiqueta, "Respuesta": valor})
    st.toast(f"✅ Guardado en la Semana {semana}")

# --- NAVEGACIÓN ---
st.sidebar.title("🧭 Programa Azimut")
menu = st.sidebar.radio("Ir a:", [
    "Inicio", 
    "Semana 1: Vía Negativa", 
    "Semana 2: Ritmos Circadianos", 
    "Semana 3: Marcadores Somáticos", 
    "Semana 4: Registro de Precisión", 
    "Semana 5: Gestión de Recursos",
    "Semana 6: Detector de Sesgos",
    "Semana 7: El Abogado del Diablo",
    "Semana 8: Antifragilidad",
    "Semana 9: El Nuevo Rumbo",
    "📊 MIS RESPUESTAS"
])

# --- SEMANA 1 ---
if menu == "Semana 1: Vía Negativa":
    st.header("📉 Semana 1: Vía Negativa")
    st.write("Identifica conductas tóxicas o innecesarias para eliminarlas.")
    dato = st.text_input("¿Qué vas a dejar de hacer hoy?")
    if st.button("Guardar Compromiso"):
        guardar_respuesta(1, "Resta del día", dato)

# --- SEMANA 2 (10 Puntos de Higiene) ---
elif menu == "Semana 2: Ritmos Circadianos":
    st.header("☀️ Semana 2: Sincronización Biológica")
    st.write("Marca los elementos de higiene biológica que has cumplido hoy:")
    check_list = [
        "Ver la luz del sol al despertar (10-20 min)", "Evitar luz azul 2h antes de dormir",
        "Cenar al menos 3h antes de acostarse", "Exposición al frío/ducha fresca",
        "Movimiento físico matutino", "Café solo después de 90 min despierto",
        "Temperatura del dormitorio fresca", "Oscuridad total para dormir",
        "Eliminar notificaciones del móvil por la noche", "Contacto con la naturaleza/tierra (Grounding)"
    ]
    seleccionados = []
    for item in check_list:
        if st.checkbox(item): seleccionados.append(item)
    
    if st.button("Registrar Día"):
        guardar_respuesta(2, "Hitos cumplidos", ", ".join(seleccionados))

# --- SEMANA 3 ---
elif menu == "Semana 3: Marcadores Somáticos":
    st.header("🧘 Semana 3: Marcadores Somáticos")
    
    zona = st.selectbox("¿Dónde lo sientes?", ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros"])
    tipo = st.text_input("Describe la sensación (calor, nudo, presión...):")
    if st.button("Registrar Mapa"):
        guardar_respuesta(3, f"Localización: {zona}", tipo)

# --- SEMANAS 4 A 7 (REGISTROS MULTI-USO) ---
elif menu == "Semana 4: Registro de Precisión":
    st.header("🏷️ Semana 4: Precisión Emocional (Registro Diario)")
    emo = st.selectbox("Emoción detectada:", ["Inquietud", "Pavor", "Frustración", "Indignación", "Melancolía", "Paz", "Gratitud"])
    if st.button("Añadir Registro"):
        guardar_respuesta(4, "Etiquetado emocional", emo)

elif menu == "Semana 5: Gestión de Recursos":
    st.header("🧬 Semana 5: Fórmula de Resiliencia")
    recurso = st.text_input("¿Qué recurso (sueño, calma, apoyo) has fortalecido hoy?")
    if st.button("Añadir Recurso"):
        guardar_respuesta(5, "Recurso fortalecido", recurso)

elif menu == "Semana 6: Detector de Sesgos":
    st.header("⚖️ Semana 6: Identificar Trampas")
    sesgo = st.selectbox("Sesgo identificado hoy:", ["Confirmación", "Negatividad", "Anclaje", "Efecto Halo"])
    obs = st.text_area("Contexto de la situación:")
    if st.button("Registrar Sesgo"):
        guardar_respuesta(6, f"Sesgo: {sesgo}", obs)

elif menu == "Semana 7: El Abogado del Diablo":
    st.header("😈 Semana 7: Desmontando Narrativas")
    creencia = st.text_input("Creencia limitante detectada:")
    contra = st.text_area("Evidencia real que la contradice:")
    if st.button("Registrar Desafío"):
        guardar_respuesta(7, f"Creencia: {creencia}", contra)

# --- SEMANA 8 ---
elif menu == "Semana 8: Antifragilidad":
    st.header("💎 Semana 8: Cosechar del Caos")
    caos = st.text_input("¿Qué imprevisto ha ocurrido?")
    ventaja = st.text_input("¿Qué beneficio o aprendizaje has extraído?")
    if st.button("Registrar Evolución"):
        guardar_respuesta(8, f"Evento: {caos}", ventaja)

# --- SEMANA 9 ---
elif menu == "Semana 9: El Nuevo Rumbo":
    st.header("🧭 Semana 9: Integración")
    st.write("### Logros alcanzados en este programa:")
    logros = [
        "Mayor consciencia de mi cuerpo", "Capacidad de frenar impulsos",
        "Mejor calidad de descanso", "Claridad para decir NO (Vía Negativa)",
        "Detección de trampas mentales", "Menos reactividad emocional"
    ]
    for l in logros: st.write(f"✅ {l}")
    
    reflexion = st.text_area("Tu reflexión final:")
    if st.button("Cerrar Mapa"):
        guardar_respuesta(9, "Reflexión Final", reflexion)
        st.balloons()

# --- APARTADO: MIS RESPUESTAS ---
elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Tu Historial de Progreso")
    if not st.session_state.historial:
        st.write("Aún no tienes registros guardados.")
    else:
        st.table(st.session_state.historial)
        if st.button("Limpiar todo el historial"):
            st.session_state.historial = []
            st.rerun()
