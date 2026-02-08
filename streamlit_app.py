dff2["bloque"].unique()):
                st.markdown(f"### Bloque {bloque}")
                bdf = dff2[dff2["bloque"] == bloque].copy()

                if bloque == 9:
                    for _, row in bdf.iterrows():
                        st.markdown(f"**{row.get('concepto','')}**")
                        resp = str(row.get("respuesta", "")).strip()
                        if resp:
                            st.write(resp)
                        meta = row.get("meta", {})
                        render_meta(meta)
                        st.divider()
                else:
                    bdf["group_date"] = bdf["fecha"].where(bdf["fecha"].astype(str).str.strip() != "", None)
                    bdf["group_date"] = bdf["group_date"].fillna(bdf["ts_date"].astype(str))

                    for gd in bdf["group_date"].unique():
                        st.markdown(f"#### {gd}")
                        gdf = bdf[bdf["group_date"] == gd]
                        for _, row in gdf.iterrows():
                            st.markdown(f"**{row.get('concepto','')}**")
                            resp = str(row.get("respuesta", "")).strip()
                            if resp:
                                st.write(resp)
                            meta = row.get("meta", {})
                            render_meta(meta)
                            st.divider()

        # -------- GRÁFICOS (barra de frecuencia + línea actividad)
        with tab2:
            section_title("Visualización de datos")

            daily = dff.dropna(subset=["ts_date"]).groupby("ts_date").size().reset_index(name="registros")
            daily = daily.sort_values("ts_date")

            section_title("Actividad diaria (periodo)")
            if PLOTLY_AVAILABLE:
                fig_line = px.line(
                    daily,
                    x="ts_date",
                    y="registros",
                    markers=True,
                    title="",
                )
                fig_line.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                if len(daily):
                    chart_df = daily.set_index("ts_date")
                    st.line_chart(chart_df)

            section_title("Frecuencia de emociones (Bloque 4)")
            d4 = dff[dff["bloque"] == 4].copy()
            d4["emo"] = d4["respuesta"].fillna("").astype(str).str.strip()
            d4 = d4[d4["emo"] != ""]
            if len(d4):
                emo_counts = d4["emo"].value_counts().reset_index()
                emo_counts.columns = ["Emoción", "Frecuencia"]

                if PLOTLY_AVAILABLE:
                    fig_bar = px.bar(
                        emo_counts,
                        x="Frecuencia",
                        y="Emoción",
                        orientation="h",
                        title="",
                    )
                    fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.bar_chart(emo_counts.set_index("Emoción"))
            else:
                st.info("Aún no hay registros suficientes en el Bloque 4 para la distribución emocional.")

        # -------- INSIGHTS (más destacado, sin la frase redundante, con espacio)
        with tab3:
            section_title("Sistema de análisis e inteligencia (Insights)")

            dom_emo, dom_ctx = dominant_emotion_and_context(dff)
            recs = recommendations(dom_emo)

            c1, c2 = st.columns(2)

            with c1:
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown("### Detección de patrones")
                st.write("")  # espacio
                st.markdown(f"**Emoción dominante:** {dom_emo if dom_emo else '—'}")
                st.markdown(f"**Contexto recurrente:** {dom_ctx if dom_ctx else '—'}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="az-card">', unsafe_allow_html=True)
                st.markdown("### Recomendaciones dinámicas")
                st.write("")  # espacio
                for r in recs[:4]:
                    st.write(f"- {r}")
                st.markdown("</div>", unsafe_allow_html=True)

        # ===== Acciones inferiores
        st.write("")
        c1, c2, c3 = st.columns([0.45, 0.35, 0.2])

        with c1:
            export_path = DATA_DIR / "history_export.csv"
            export_cols = ["timestamp", "bloque", "fecha", "concepto", "respuesta", "meta"]
            dff_export = dff.copy()[export_cols]
            dff_export.to_csv(export_path, index=False, encoding="utf-8")
            st.download_button(
                "Descargar CSV (filtrado)",
                data=export_path.read_bytes(),
                file_name="azimut_historial_filtrado.csv",
            )

        with c2:
            with st.expander("Ver tabla completa (debug)"):
                show = dff.drop(columns=["fecha_sort"], errors="ignore")
                st.dataframe(show, use_container_width=True)

        with c3:
            if st.button("Limpiar historial"):
                st.session_state.historial = []
                save_history([])
                st.rerun()

