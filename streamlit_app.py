# (Se omite cabecera sin cambios)
# Mantengo todo el código inicial intacto hasta apply_theme()

def apply_theme(dark: bool):
    if dark:
        bg = "#0b1220"
        text = "#e9eef7"
        muted = "#b8c2d6"
        card = "#101a2b"
        border = "rgba(255,255,255,0.08)"
    else:
        bg = BRAND_WHITE
        text = "#0b0f1a"
        muted = "#4b5563"
        card = "#ffffff"
        border = "rgba(10,20,40,0.10)"

    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {bg};
            color: {text};
          }}

          section[data-testid="stSidebar"] {{
            background: {BRAND_BLUE};
          }}

          /* Sidebar estilo */
          section[data-testid="stSidebar"] label {{
            margin: 10px 0px !important;
          }}

          /* Separación visual */
          section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
            padding: 12px 10px !important;
            margin: 8px 0px !important;
            border-radius: 12px !important;
          }}

          /* Tarjetas */
          .az-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 18px;
          }}

          /* Título de bloque */
          .az-block-title {{
            font-size: 28px;
            font-weight: 900;
            color: #000;
            border-bottom: 4px solid {BRAND_BLUE};
            display: inline-block;
            padding-bottom: 4px;
          }}

          /* Subtítulo sección */
          .az-section-title {{
            font-size: 20px;
            font-weight: 800;
            color: #000;
            border-bottom: 3px solid {BRAND_YELLOW};
            display: inline-block;
            padding-bottom: 3px;
            margin-top: 10px;
          }}

          /* Enunciado */
          .az-instruction {{
            font-weight: 700;
            color: #000;
            margin-top: 6px;
            margin-bottom: 12px;
          }}

          /* Botón */
          div.stButton > button {{
            background-color: {BRAND_BLUE} !important;
            color: {BRAND_YELLOW} !important;
            border: 0px !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            padding: 0.65rem 1.05rem !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_theme(st.session_state.dark_mode)

# =========================================================
# Sidebar + luna integrada
# =========================================================
st.sidebar.title("🧭 Programa Azimut")
MENU_ITEMS = [
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
]
menu = st.sidebar.radio("Ir a:", MENU_ITEMS, key="nav_menu")

st.sidebar.markdown("---")
if st.sidebar.button("🌙", help="Modo oscuro"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# =========================================================
# PANTALLAS
# =========================================================
df_all = history_df()

# ===================== INICIO =====================
if menu == "Inicio":
    st.markdown('<div class="az-card">', unsafe_allow_html=True)
    st.markdown('<div class="az-block-title">Azimut</div>', unsafe_allow_html=True)

    st.write(
        "Esta aplicación es un **cuaderno de navegación diaria**. "
        "Cada día completas el bloque correspondiente. Al principio costará, "
        "pero con los días notarás algo muy concreto: **identificarás antes lo que te pasa** "
        "y tus explicaciones serán más precisas.\n\n"
        "Esa mejora se ve en la claridad, en la rapidez con la que nombras una emoción, "
        "detectas un sesgo o localizas una tensión corporal.\n\n"
        "Tus respuestas se guardan en **MIS RESPUESTAS**, donde podrás ver patrones "
        "y tu progreso.\n\n"
        "Deja el **Bloque 9** para el final del programa."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("### Acceso directo a bloques")

    cols = st.columns(3)
    blocks = MENU_ITEMS[1:10]

    for i, b in enumerate(blocks):
        if cols[i % 3].button(b.split(":")[0]):
            goto(b)

# ===================== BLOQUE 3 ejemplo =====================
elif menu == "Bloque 3: Marcadores Somáticos":
    st.markdown('<div class="az-block-title">Bloque 3: Marcadores somáticos</div>', unsafe_allow_html=True)
    st.markdown('<div class="az-instruction">El cuerpo habla en dialectos: tensión, nudo, calor, vacío.</div>', unsafe_allow_html=True)

    f = fecha_bloque(3)

    st.markdown('<div class="az-section-title">Mapa corporal</div>', unsafe_allow_html=True)
    st.markdown('<div class="az-instruction">Localiza y nombra la sensación.</div>', unsafe_allow_html=True)

    zona = st.selectbox(
        "¿Dónde lo sientes?",
        ["Pecho", "Garganta", "Abdomen", "Mandíbula", "Hombros", "Cabeza", "Cuello", "Espalda", "Manos", "Brazos", "Piernas", "Pies"],
    )
    tipo = st.text_input("Describe la sensación:")

    if st.button("Guardar registro"):
        guardar_respuesta(3, f, f"Marcador somático — {zona}", tipo)

# ===================== BLOQUE 9 =====================
elif menu == "Bloque 9: El Nuevo Rumbo":
    st.markdown('<div class="az-block-title">Bloque 9: El Nuevo Rumbo</div>', unsafe_allow_html=True)

    st.markdown('<div class="az-section-title">Beneficios de haber completado Azimut</div>', unsafe_allow_html=True)
    for b in BENEFITS_BLOCK9:
        st.write(f"- {b}")

    reflexion = st.text_area("Reflexión final:", height=180)

    if st.button("Guardar reflexión final"):
        guardar_respuesta(9, "", "Reflexión final", reflexion)
        st.balloons()

# ===================== MIS RESPUESTAS =====================
elif menu == "📊 MIS RESPUESTAS":
    st.markdown('<div class="az-block-title">Mis respuestas</div>', unsafe_allow_html=True)

    df = df_all.copy()
    if df.empty:
        st.write("Aún no hay registros.")
    else:
        tab1, tab2, tab3 = st.tabs(["Historial", "Gráficos", "Insights"])

        with tab1:
            dff = df.sort_values(by=["bloque", "timestamp"])
            for _, row in dff.iterrows():
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown(f"**Bloque {row['bloque']}** — {row.get('fecha','')}")
                st.write(row.get("concepto", ""))
                st.write(row.get("respuesta", ""))
                meta = row.get("meta", {})
                if isinstance(meta, dict) and meta:
                    for k, v in meta.items():
                        if v:
                            st.write(f"**{k}:** {v}")
                st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            dom_emo, dom_ctx = dominant_emotion_and_context(df)
            recs = recommendations(dom_emo)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown('<div class="az-section-title">Detección de patrones</div>', unsafe_allow_html=True)
                st.write(f"**Emoción dominante:** {dom_emo if dom_emo else '—'}")
                st.write(f"**Contexto recurrente:** {dom_ctx if dom_ctx else '—'}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown('<div class="az-section-title">Recomendaciones dinámicas</div>', unsafe_allow_html=True)
                for r in recs[:4]:
                    st.write(f"- {r}")
                st.markdown("</div>", unsafe_allow_html=True)
