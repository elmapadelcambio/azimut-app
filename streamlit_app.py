# app.py
import sqlite3
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================
# Config
# =========================
st.set_page_config(page_title="Azimut", layout="wide")

DB_PATH = "azimut.db"
ACCENT = "#26b7ff"
ACCENT_YELLOW = "#f9e205"


# =========================
# CSS (estética app)
# =========================
def inject_css():
    css = f"""
    <style>
      :root{{
        --bg:#0b1220;
        --panel:#0f1a2b;
        --card:#0c1a2a;
        --text:#e7eefc;
        --muted:#92a4c6;
        --accent:{ACCENT};
        --accent2:{ACCENT_YELLOW};
        --border:rgba(255,255,255,0.08);
      }}
      .stApp{{ background: var(--bg); color: var(--text); }}
      h1,h2,h3,h4{{ color: var(--text)!important; }}
      p,li,span,div{{ color: var(--text); }}

      .muted{{ color: var(--muted); }}
      .card{{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 16px 16px;
        margin: 10px 0;
        box-shadow: 0 10px 26px rgba(0,0,0,0.28);
      }}
      .kpi{{
        display:flex; flex-direction:column; gap:6px;
      }}
      .kpi .label{{ color: var(--muted); font-size: 12px; }}
      .kpi .value{{ font-size: 26px; font-weight: 900; letter-spacing: .2px; }}
      .badge{{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(38,183,255,0.14);
        border: 1px solid rgba(38,183,255,0.35);
        color: var(--accent);
        font-size: 12px;
        font-weight: 700;
      }}
      .badge-yellow{{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(249,226,5,0.10);
        border: 1px solid rgba(249,226,5,0.35);
        color: var(--accent2);
        font-size: 12px;
        font-weight: 800;
      }}

      /* Sidebar */
      section[data-testid="stSidebar"]{{
        background: #070d18;
        border-right: 1px solid var(--border);
      }}
      .sidebar-title{{
        font-weight: 900;
        color: var(--accent2);
        margin: 10px 0 6px 0;
        letter-spacing: .3px;
      }}

      /* Botones */
      .stButton>button {{
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.04);
        color: var(--text);
        font-weight: 800;
        padding: 10px 14px;
      }}
      .stButton>button:hover {{
        border-color: rgba(38,183,255,0.45);
        background: rgba(38,183,255,0.12);
      }}

      /* Dataframe */
      [data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
      }}

      /* Radios: “marca” amarilla */
      div[role="radiogroup"] label span:first-child {{
        border-color: rgba(249,226,5,0.65) !important;
      }}
      div[role="radiogroup"] label[data-checked="true"] span:first-child {{
        background: var(--accent2) !important;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


inject_css()


# =========================
# DB
# =========================
def db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with db_conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts TEXT NOT NULL,
              day TEXT NOT NULL,
              block TEXT NOT NULL,
              emotion TEXT,
              why TEXT,
              where_ TEXT,
              what TEXT
            );
            """
        )
        con.commit()


def insert_record(rec: Dict[str, Any]):
    with db_conn() as con:
        con.execute(
            """
            INSERT INTO records (ts, day, block, emotion, why, where_, what)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec["ts"],
                rec["day"],
                rec["block"],
                rec.get("emotion"),
                rec.get("why"),
                rec.get("where"),
                rec.get("what"),
            ),
        )
        con.commit()


def load_records() -> pd.DataFrame:
    with db_conn() as con:
        df = pd.read_sql_query("SELECT * FROM records ORDER BY ts DESC", con)
    if df.empty:
        return df
    df["ts"] = pd.to_datetime(df["ts"])
    df["day"] = pd.to_datetime(df["day"]).dt.date
    return df


init_db()


# =========================
# Helpers
# =========================
def card(title: str, subtitle: Optional[str] = None, badge: Optional[str] = None, badge_yellow: bool = False):
    b = ""
    if badge:
        klass = "badge-yellow" if badge_yellow else "badge"
        b = f'<span class="{klass}">{badge}</span><br>'
    s = f'<div class="muted">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="card">{b}<div style="font-size:18px;font-weight:900">{title}</div>{s}</div>',
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str):
    st.markdown(
        f"""
        <div class="card kpi">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def compute_streak(days_with_records: List[date]) -> int:
    if not days_with_records:
        return 0
    s = set(days_with_records)
    streak = 0
    d = date.today()
    while d in s:
        streak += 1
        d = d - timedelta(days=1)
    return streak


def filter_by_range(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    if df.empty:
        return df
    mask = (df["day"] >= start) & (df["day"] <= end)
    return df.loc[mask].copy()


def recommendations(df_range: pd.DataFrame) -> List[str]:
    """
    Reglas simples (interpretables):
    - Si predominan emociones de alta activación/negativas -> sugerir Bloque 2 o 4.
    - Si hay mucha repetición del mismo disparador (“what”) -> sugerir Bloque 6 (patrones).
    - Si streak bajo -> sugerir foco en consistencia (Bloque 1/8).
    """
    if df_range.empty:
        return ["Empieza con un registro hoy. La precisión nace del primer dato, no del primer insight."]

    # Etiquetas simples (ajústalas a tu taxonomía real)
    high_stress = {"Anxious", "Angry", "Sad", "Overwhelmed", "Fear"}
    emotions = df_range["emotion"].dropna().astype(str).tolist()
    emo_counts = pd.Series(emotions).value_counts() if emotions else pd.Series(dtype=int)

    recs = []

    # 1) Dominancia de emociones “difíciles”
    if not emo_counts.empty:
        difficult_ratio = sum(emo_counts.get(e, 0) for e in high_stress) / max(1, emo_counts.sum())
        if difficult_ratio >= 0.45:
            recs.append("Se repiten emociones de alta carga: vuelve a fundamentos (Bloque 2) y precisión contextual (Bloque 4).")

    # 2) Repetición de disparadores
    what = df_range["what"].dropna().astype(str)
    if not what.empty:
        top_what = what.value_counts().head(1)
        if len(top_what) == 1 and top_what.iloc[0] >= 3:
            recs.append("Hay un disparador recurrente: conviértelo en patrón explícito y diseña respuesta (Bloque 6).")

    # 3) Señal de baja densidad de datos
    if len(df_range) < 4:
        recs.append("Pocos registros en el rango: prioriza consistencia mínima (2–3 min/día) antes de complicar el modelo.")

    if not recs:
        recs.append("Buen equilibrio: sube nivel. Revisa patrones y prueba micro-ajustes (Bloque 6 → Bloque 8).")

    return recs


# =========================
# Screens
# =========================
def screen_dashboard(df_all: pd.DataFrame, start: date, end: date):
    st.markdown("## Azimut Dashboard")
    st.markdown('<div class="muted">Métricas, patrones y recomendaciones basadas en tus registros.</div>', unsafe_allow_html=True)

    df = filter_by_range(df_all, start, end)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Registros (rango)", str(len(df)))
    with c2:
        days = sorted(set(df["day"].tolist())) if not df.empty else []
        kpi("Días con registros", str(len(days)))
    with c3:
        streak = compute_streak(sorted(set(df_all["day"].tolist())) if not df_all.empty else [])
        kpi("Streak actual", f"{streak} días")
    with c4:
        dom = "-"
        if not df.empty and df["emotion"].notna().any():
            dom = df["emotion"].dropna().astype(str).value_counts().idxmax()
        kpi("Emoción dominante", dom)

    # Charts
    left, right = st.columns([1.2, 1.0])

    with left:
        card("Distribución de emociones", "Frecuencia en el rango seleccionado.", badge="INSIGHTS")
        if df.empty or df["emotion"].dropna().empty:
            st.info("Aún no hay emociones registradas en este rango.")
        else:
            emo = df["emotion"].dropna().astype(str).value_counts().reset_index()
            emo.columns = ["emotion", "count"]
            fig = px.bar(emo, x="emotion", y="count")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        card("Actividad por día", "Cuántos registros haces y cuándo.", badge="TREND")
        if df.empty:
            st.info("Sin actividad en el rango.")
        else:
            daily = df.groupby("day").size().reset_index(name="count")
            fig2 = px.line(daily, x="day", y="count", markers=True)
            fig2.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

    with right:
        card("Recomendaciones", "Sugerencias automáticas basadas en patrones simples.", badge="SYSTEM", badge_yellow=True)
        for r in recommendations(df):
            st.markdown(f"- {r}")

        card("Últimas respuestas", "Vista rápida de lo más reciente.", badge="RECENT")
        if df_all.empty:
            st.info("Aún no hay registros.")
        else:
            st.dataframe(df_all.head(8)[["ts", "block", "emotion", "what"]], use_container_width=True)


def screen_block4_form():
    st.markdown("## Bloque 4 · Emotional Precision")
    st.markdown('<div class="muted">Refina tu estado actual con precisión y claridad.</div>', unsafe_allow_html=True)

    with st.form("block4"):
        emotion = st.selectbox(
            "Emoción detectada",
            ["", "Calm", "Motivated", "Anxious", "Angry", "Sad", "Overwhelmed", "Fear"],
        )
        why = st.text_area("¿Por qué?", placeholder="Describe la causa raíz (sin novela, con bisturí).")
        where = st.text_area("¿Dónde?", placeholder="Localización corporal y/o contexto (pecho, garganta, trabajo, casa…).")
        what = st.text_area("¿Qué pasó?", placeholder="Evento disparador: qué ocurrió, con qué persona, en qué momento.")

        submitted = st.form_submit_button("Guardar registro")
        if submitted:
            now = datetime.now()
            rec = {
                "ts": now.isoformat(timespec="seconds"),
                "day": now.date().isoformat(),
                "block": "Bloque 4",
                "emotion": emotion if emotion else None,
                "why": why.strip() if why else None,
                "where": where.strip() if where else None,
                "what": what.strip() if what else None,
            }
            insert_record(rec)
            st.success("Guardado. La consistencia es el músculo invisible.")


def screen_responses(df_all: pd.DataFrame, start: date, end: date):
    st.markdown("## Mis respuestas")
    st.markdown('<div class="muted">Tus registros guardados. Filtra por fechas para ver patrones.</div>', unsafe_allow_html=True)

    df = filter_by_range(df_all, start, end)
    if df.empty:
        st.info("No hay registros en este rango.")
        return

    st.dataframe(
        df[["ts", "day", "block", "emotion", "why", "where_", "what"]],
        use_container_width=True,
        hide_index=True,
    )


# =========================
# Sidebar: navegación + filtros tiempo
# =========================
df_all = load_records()

with st.sidebar:
    st.markdown('<div class="sidebar-title">Bloques</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navegación",
        ["Dashboard", "Bloque 4", "Mis respuestas"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown('<div class="sidebar-title">Filtro de tiempo</div>', unsafe_allow_html=True)

    # Default: últimos 7 días
    today = date.today()
    default_start = today - timedelta(days=6)

    start = st.date_input("Desde", value=default_start)
    end = st.date_input("Hasta", value=today)

    if start > end:
        st.error("Rango inválido: 'Desde' no puede ser posterior a 'Hasta'.")


# =========================
# Router
# =========================
if page == "Dashboard":
    screen_dashboard(df_all, start, end)
elif page == "Bloque 4":
    screen_block4_form()
else:
    screen_responses(df_all, start, end)
