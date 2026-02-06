import streamlit as st
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA Y COLORES DE MARCA ---
st.set_page_config(page_title="Azimut - El Mapa del Cambio", page_icon="🧭", layout="wide")

# Definición de colores
AZUL_MARCA = "#00a7ff"
AMARILLO_MARCA = "#f9e205"

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(f"""
    <style>
    /* Títulos en Azul Marca */
    h1, h2, h3, h4 {{
        color: {AZUL_MARCA} !important;
    }}
    
    /* Barra Lateral (Fondo y Texto) */
    section[data-testid="stSidebar"] {{
        background-color: {AZUL_MARCA};
    }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {{
        color: white !important;
    }}
    
    /* Botones: Azul con texto Amarillo */
    div.stButton > button {{
        background-color: {AZUL_MARCA} !important;
        color: {AMARILLO_MARCA} !important;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        font-size: 16px;
    }}
    div.stButton > button:hover {{
        background-color: #008ecc !important; /* Un azul un poco más oscuro al pasar el ratón */
        color: {AMARILLO_MARCA} !important;
    }}
    
    /* Ajustes generales */
    .stTextArea textarea {{ border-radius: 10px; }}
    .stTextInput input {{ border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO (MEMORIA) ---
if 'historial' not in st.session_state:
    st.session_state.historial = []

def guardar_respuesta(fecha, semana, etiqueta, valor):
    # Guardamos la fecha como string para que sea fácil de leer
    fecha_str = fecha.strftime("%d/%m/%Y")
    st.session_state.historial.append({
        "Fecha": fecha_str,
        "Semana": semana,
        "Concepto": etiqueta,
        "Respuesta": valor
    })
    st.toast(f"✅ Guardado en {semana} ({fecha_str})")

# --- NAVEGACIÓN ---
st.sidebar.title("🧭 MAPA AZIMUT")
menu = st.sidebar.radio("Navegación:", [
    "Inicio", 
    "Semana 1: Vía Negativa", 
    "Semana 2: Ritmos y Entorno", 
    "Semana 3: Marcadores Somáticos", 
    "Semana 4: Precisión Emocional", 
    "Semana 5: Gestión de Recursos",
    "Semana 6: Detector de Sesgos",
    "Semana 7: El Abogado del Diablo",
    "Semana 8: Antifragilidad",
    "Semana 9: El Nuevo Rumbo",
    "📊 MIS RESPUESTAS"
])

# --- PÁGINA DE INICIO ---
if menu == "Inicio":
    st.title("Bienvenido a tu Mapa del Cambio")
    st.write("""
    Esta herramienta es el complemento práctico de tu programa **Azimut**.
    
    Úsala cada semana para registrar tus avances, detectar patrones y consolidar tu aprendizaje.
    Tus respuestas se guardan en el apartado **'Mis Respuestas'** para que puedas ver tu evolución.
    """)

# --- SEMANA 1 ---
elif menu == "Semana 1: Vía Negativa":
    st.header("📉 Semana 1: Vía Negativa")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.write("Antes de sumar, toca restar. Identifica qué te sobra para ganar claridad.")
    dato = st.text_input("¿Qué conducta, hábito o decisión vas a ELIMINAR hoy?")
    
    if st.button("Guardar Compromiso"):
        guardar_respuesta(hoy, "Semana 1", "Resta del día", dato)

# --- SEMANA 2 (Extraído de Newsletters) ---
elif menu == "Semana 2: Ritmos y Entorno":
    st.header("☀️ Semana 2: Regulación Biológica")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.write("Marca los puntos de higiene biológica que has cumplido hoy:")
    
    # Puntos extraídos de tus textos (Newsletters sobre sueño, luz, hábitos)
    puntos_regulacion = [
        "Exposición a luz solar directa al despertar",
        "Oscuridad total en el dormitorio al dormir",
        "Regularidad: me he acostado/levantado a la misma hora",
        "He cenado al menos 3 horas antes de dormir",
        "Movimiento físico diario (caminar, entrenar)",
        "Contacto con la naturaleza (o exposición al frío)",
        "He evitado luz azul/pantallas 2h antes de dormir",
        "He comido 'comida real' (evitando ultraprocesados)",
        "He limitado la cafeína después del mediodía",
        "He priorizado el descanso sobre la productividad",
        "He practicado algún momento de silencio/no hacer",
        "He evitado noticias o estímulos estresantes por la noche"
    ]
    
    seleccionados = []
    for punto in puntos_regulacion:
        if st.checkbox(punto):
            seleccionados.append(punto)
    
    if st.button("Guardar Registro Diario"):
        guardar_respuesta(hoy, "Semana 2", "Hitos biológicos", ", ".join(seleccionados))

# --- SEMANA 3 ---
elif menu == "Semana 3: Marcadores Somáticos":
    st.header("🧘 Semana 3: El Cuerpo no Miente")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.write("¿Dónde sientes la emoción ahora mismo? Escanea tu cuerpo.")
    
    zonas_cuerpo = [
        "Cabeza/Frente", "Garganta (nudo)", "Hombros/Cuello", 
        "Pecho (presión/calor)", "Estómago/Abdomen", "Manos (sudor/frío)",
        "Piernas/Pies (inquietud)", "Mandíbula (tensión)"
    ]
    zona = st.selectbox("Zona principal:", zonas_cuerpo)
    sensacion = st.text_input("Describe la cualidad (pinchanzo, vacío, fuego, peso...):")
    
    if st.button("Guardar Registro"):
        guardar_respuesta(hoy, "Semana 3", f"Marcador: {zona}", sensacion)

# --- SEMANA 4 (Emociones de Azimut Completo) ---
elif menu == "Semana 4: Precisión Emocional":
    st.header("🏷️ Semana 4: Etiquetado de Precisión")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.write("No digas 'estoy mal'. Busca la palabra exacta.")
    
    # Lista extraída de tu documento Azimut
    emociones_azimut = [
        "Miedo / Ansiedad / Pánico",
        "Ira / Frustración / Rabia",
        "Tristeza / Melancolía / Desánimo",
        "Alegría / Entusiasmo / Gratitud",
        "Asco / Rechazo",
        "Sorpresa / Desconcierto",
        "Vergüenza / Culpa / Remordimiento",
        "Amor / Afecto / Ternura",
        "Desesperanza / Vacío"
    ]
    
    emo = st.selectbox("¿Qué emoción predomina?", emociones_azimut)
    
    st.write("### Análisis de la emoción")
    contexto = st.text_area("Rellena: ¿Por qué crees que es esta emoción? ¿Dónde estabas? ¿Qué pasó exactamente?")
    
    if st.button("Guardar Emoción"):
        guardar_respuesta(hoy, "Semana 4", f"Emoción: {emo}", contexto)

# --- SEMANA 5 ---
elif menu == "Semana 5: Gestión de Recursos":
    st.header("🧬 Semana 5: Fórmula de la Resiliencia")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.latex(r''' Resiliencia = \frac{Reto}{Recursos} ''')
    
    st.write("Para equilibrar la balanza, sube tus recursos.")
    recurso = st.selectbox("¿Qué recurso has activado hoy?", [
        "Sueño profundo", "Nutrición densa", "Movimiento/Deporte", 
        "Conexión social/Tribu", "Silencio/Meditación", "Naturaleza",
        "Juego/Hobbies", "Terapia/Escritura", "Tiempo libre"
    ])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pq = st.text_input("¿Por qué elegiste este?")
    with col2:
        como = st.text_input("¿Cómo lo hiciste?")
    with col3:
        sentir = st.text_input("¿Cómo te sientes ahora?")
        
    resumen = f"Por qué: {pq} | Cómo: {como} | Resultado: {sentir}"
    
    if st.button("Añadir Recurso"):
        guardar_respuesta(hoy, "Semana 5", f"Recurso: {recurso}", resumen)

# --- SEMANA 6 (Sesgos de Newsletters) ---
elif menu == "Semana 6: Detector de Sesgos":
    st.header("⚖️ Semana 6: Trampas Mentales")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.write("Identifica qué filtro está distorsionando tu realidad hoy.")
    
    # Sesgos extraídos de tus textos
    sesgos = [
        "Sesgo de Confirmación (solo veo lo que me da la razón)",
        "Aversión a la Pérdida (miedo a soltar lo conocido)",
        "Falacia del Coste Hundido (seguir por no perder lo invertido)",
        "Efecto Zeigarnik (mi mente no suelta lo inacabado)",
        "Indefensión Aprendida (creer que no puedo hacer nada)",
        "Efecto Dunning-Kruger (creer que sé más de lo que sé)",
        "Sesgo de Negatividad (foco en lo malo)",
        "Ilusión de Control (creer que controlo el azar)",
        "Adaptación Hedónica (acostumbrarme rápido a lo bueno)",
        "Efecto Manada (hacer lo que hacen todos)"
    ]
    
    sesgo_detectado = st.selectbox("Sesgo identificado:", sesgos)
    situacion = st.text_area("Describe la situación donde aplicaste este sesgo:")
    
    if st.button("Registrar Sesgo"):
        guardar_respuesta(hoy, "Semana 6", sesgo_detectado, situacion)

# --- SEMANA 7 ---
elif menu == "Semana 7: El Abogado del Diablo":
    st.header("😈 Semana 7: Desmontando Narrativas")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    st.write("Escribe una creencia limitante que te esté frenando.")
    creencia = st.selectbox("Ejemplos comunes (o escribe la tuya abajo):", [
        "Escribe la tuya propia...",
        "No soy suficiente",
        "Es demasiado tarde para cambiar",
        "Si fallo, soy un fracaso",
        "Mostrar emociones es de débiles",
        "Necesito la aprobación de los demás para estar bien",
        "Yo soy así, no puedo cambiar mi carácter"
    ])
    
    if creencia == "Escribe la tuya propia...":
        creencia_real = st.text_input("Tu creencia limitante:")
    else:
        creencia_real = creencia
        
    st.info("💡 PISTA: Piensa en un momento concreto donde esta creencia NO se cumplió. Busca una evidencia real, por pequeña que sea, que demuestre que no es una verdad absoluta.")
    contra = st.text_area("El Abogado del Diablo responde (Evidencia en contra):")
    
    if st.button("Desmontar Creencia"):
        guardar_respuesta(hoy, "Semana 7", f"Creencia: {creencia_real}", f"Desmontada con: {contra}")

# --- SEMANA 8 ---
elif menu == "Semana 8: Antifragilidad":
    st.header("💎 Semana 8: Cosechar del Caos")
    hoy = st.date_input("Fecha del registro:", date.today())
    
    caos = st.text_input("¿Qué imprevisto, error o dificultad ha ocurrido?")
    
    st.info("💡 PISTA: Si tuvieras que sacar una ventaja obligatoria de esto, ¿cuál sería? ¿Qué has aprendido que no sabías? ¿En qué te ha hecho más fuerte?")
    ventaja = st.text_area("¿Qué beneficio o aprendizaje extraes de esto?")
    
    if st.button("Registrar Antifragilidad"):
        guardar_respuesta(hoy, "Semana 8", f"Evento: {caos}", f"Beneficio: {ventaja}")

# --- SEMANA 9 (Cierre y Reflexión Final) ---
elif menu == "Semana 9: El Nuevo Rumbo":
    st.header("🧭 Semana 9: Integración y Azimut")
    
    st.write("### Beneficios alcanzados (Marca de verificación interna):")
    
    # Beneficios extraídos de Azimut
    beneficios = [
        "Mayor consciencia corporal e intercepción",
        "Capacidad de responder en lugar de reaccionar (pausa)",
        "Vocabulario emocional más amplio y preciso",
        "Comprensión de mis mecanismos de defensa",
        "Aceptación de la incertidumbre como parte del proceso",
        "Conexión real entre cuerpo y mente",
        "Mayor autocompasión y menos juicio interno",
        "Capacidad para dejar de huir del malestar"
    ]
    
    for b in beneficios:
        st.markdown(f"- {b}")
        
    st.markdown("---")
    st.write("### Reflexión Final del Programa")
    st.write("Tómate tu tiempo. Sin fecha. Esto es el poso que queda.")
    
    reflexion = st.text_area(
        "¿Qué has aprendido? ¿Cómo has avanzado en cada bloque? ¿Qué te ha costado más y aun así sientes que ahora gestionas mejor?",
        height=200
    )
    
    if st.button("Cerrar Mapa"):
        # Guardamos sin fecha específica o con la de hoy, pero marcada como FINAL
        guardar_respuesta(date.today(), "Semana 9 - FINAL", "Reflexión de Cierre", reflexion)
        st.balloons()
        st.success("¡Enhorabuena! Has completado el recorrido. Tu mapa ahora es tuyo.")

# --- APARTADO: MIS RESPUESTAS (Ordenado y Agrupado) ---
elif menu == "📊 MIS RESPUESTAS":
    st.title("📊 Tu Bitácora de Viaje")
    
    if not st.session_state.historial:
        st.info("Aún no hay registros. Comienza a trabajar en las semanas.")
    else:
        # Agrupar por Fecha y luego por Semana
        # Convertimos la lista en un DataFrame para facilitar, o lo hacemos manual
        # Hacemos manual para no depender de pandas si no se quiere
        
        # Ordenar historial por fecha (asumiendo formato dd/mm/yyyy)
        historial_ordenado = sorted(
            st.session_state.historial, 
            key=lambda x: datetime.strptime(x['Fecha'], "%d/%m/%Y") if 'Fecha' in x else datetime.min, 
            reverse=True
        )
        
        from itertools import groupby
        from datetime import datetime

        # Agrupar por Fecha
        for fecha, items_fecha in groupby(historial_ordenado, key=lambda x: x['Fecha']):
            st.markdown(f"### 📅 {fecha}")
            lista_items = list(items_fecha)
            
            # Dentro de la fecha, agrupar por Semana
            # Ordenamos por semana primero para que groupby funcione
            lista_items.sort(key=lambda x: x['Semana'])
            
            for semana, items_semana in groupby(lista_items, key=lambda x: x['Semana']):
                with st.expander(f"📂 {semana}", expanded=True):
                    for item in items_semana:
                        st.markdown(f"**{item['Concepto']}:**")
                        st.write(item['Respuesta'])
                        st.markdown("---")
