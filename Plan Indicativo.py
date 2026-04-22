"""
Dashboard — Plan Indicativo 2024-2027
Seguimiento de ejecución física y financiera del Plan de Desarrollo.
"""

import io
import streamlit as st
import polars as pl
import polars.selectors as cs
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests

# =========================================================================
# Paleta corporativa
# =========================================================================
COLORS = {
    # Primarios (fila superior)
    "green_light":  "#17743d",
    "green_dark":   "#005931",
    "cyan":         "#47b1d5",
    "blue":         "#1754ab",
    "blue_dark":    "#003d6c",
    # Secundarios cálidos (fila inferior)
    "orange":       "#d88c16",
    "orange_deep":  "#cf7000",
    "amber":        "#d37e00",
    "brown":        "#9b5b1e",
    "coral":        "#e68878",
}

# Tipografías
FONT_DISPLAY = "Fraunces"   # serif editorial con carácter institucional
FONT_BODY    = "Archivo"    # sans refinada, legible para datos
FONT_MONO    = "JetBrains Mono"

# =========================================================================
# Configuración de página
# =========================================================================
st.set_page_config(
    page_title="Plan Indicativo 2024-2027",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================
# CSS institucional
# =========================================================================
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,400&family=Archivo:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --green-light: {COLORS["green_light"]};
    --green-dark:  {COLORS["green_dark"]};
    --cyan:        {COLORS["cyan"]};
    --blue:        {COLORS["blue"]};
    --blue-dark:   {COLORS["blue_dark"]};
    --orange:      {COLORS["orange"]};
    --orange-deep: {COLORS["orange_deep"]};
    --amber:       {COLORS["amber"]};
    --brown:       {COLORS["brown"]};
    --coral:       {COLORS["coral"]};

    --paper:       #fbfaf6;
    --ink:         #0d1b2a;
    --ink-mute:    #4a5a6a;
    --hairline:    #d9d4c7;
    --chip-bg:     #f1ede2;
}}

/* Fondo y tipografía base */
html, body, [class*="css"], .stApp {{
    font-family: '{FONT_BODY}', system-ui, sans-serif !important;
    color: var(--ink);
}}

.stApp {{
    background:
        radial-gradient(1200px 600px at 90% -10%, rgba(23,84,171,0.06), transparent 60%),
        radial-gradient(900px 500px at -10% 110%, rgba(216,140,22,0.05), transparent 60%),
        var(--paper);
}}

/* Encabezados */
h1, h2, h3, h4, h5, h6 {{
    font-family: '{FONT_DISPLAY}', Georgia, serif !important;
    color: var(--ink);
    letter-spacing: -0.01em;
}}
h1 {{ font-weight: 700 !important; }}
h2, h3 {{ font-weight: 600 !important; }}

/* Barra superior / menú oculto */
#MainMenu, header [data-testid="stToolbar"], footer {{ visibility: hidden; }}
header {{ background: transparent !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--blue-dark) 0%, #00284a 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}}
[data-testid="stSidebar"] * {{ color: #e9eef5 !important; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: #fff !important; }}
[data-testid="stSidebar"] label {{
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #b9c6d6 !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    color: #fff !important;
}}
[data-testid="stSidebar"] button {{
    background: var(--orange-deep) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 2px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    transition: background 0.2s ease;
}}
[data-testid="stSidebar"] button:hover {{
    background: var(--amber) !important;
}}

/* Tarjetas de métrica */
[data-testid="stMetric"] {{
    background: #fff;
    border: 1px solid var(--hairline);
    border-left: 3px solid var(--blue);
    padding: 1.1rem 1.25rem;
    border-radius: 2px;
    box-shadow: 0 1px 0 rgba(13,27,42,0.03);
}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    font-size: 0.68rem !important;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--ink-mute) !important;
    font-weight: 600;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-family: '{FONT_DISPLAY}', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 2rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
}}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
    font-family: '{FONT_MONO}', monospace !important;
    font-size: 0.82rem !important;
    color: var(--green-light) !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    border-bottom: 1px solid var(--hairline);
    background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    height: 48px;
    padding: 0 1.3rem;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: var(--ink-mute) !important;
    font-family: '{FONT_BODY}', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    transition: color 0.2s ease, border-color 0.2s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: var(--blue) !important;
}}
.stTabs [aria-selected="true"] {{
    color: var(--blue-dark) !important;
    border-bottom: 2px solid var(--orange-deep) !important;
    background: transparent !important;
}}

/* Dataframes */
.stDataFrame {{
    border: 1px solid var(--hairline);
    border-radius: 2px;
}}

/* Info, warning, error boxes */
.stAlert {{
    border-radius: 2px !important;
    border-left: 3px solid var(--blue) !important;
}}

/* Selects y inputs */
[data-baseweb="select"] > div {{
    border-radius: 2px !important;
    border-color: var(--hairline) !important;
}}

/* Botón de descarga */
.stDownloadButton button {{
    background: var(--blue-dark) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 2px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-size: 0.78rem !important;
    padding: 0.55rem 1.1rem !important;
}}
.stDownloadButton button:hover {{
    background: var(--blue) !important;
}}

/* Encabezado editorial */
.masthead {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 1.2rem 0 0.4rem 0;
    border-bottom: 1px solid var(--ink);
    margin-bottom: 0.4rem;
}}
.masthead .eyebrow {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--orange-deep);
    margin-bottom: 0.4rem;
}}
.masthead h1 {{
    font-size: 3.4rem !important;
    line-height: 0.95 !important;
    margin: 0 !important;
    font-weight: 700 !important;
    font-style: italic;
}}
.masthead .edition {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.72rem;
    color: var(--ink-mute);
    text-align: right;
    letter-spacing: 0.08em;
    line-height: 1.5;
}}
.masthead .edition strong {{
    color: var(--ink);
    font-weight: 600;
}}

.subhead {{
    font-size: 0.9rem;
    color: var(--ink-mute);
    font-style: italic;
    border-bottom: 1px solid var(--hairline);
    padding-bottom: 1.2rem;
    margin-bottom: 1.6rem;
    letter-spacing: 0.02em;
}}

/* Sección */
.section-title {{
    font-family: '{FONT_DISPLAY}', Georgia, serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--ink);
    margin: 1.2rem 0 0.2rem 0;
    letter-spacing: -0.015em;
}}
.section-title .num {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.75rem;
    color: var(--orange-deep);
    letter-spacing: 0.2em;
    vertical-align: middle;
    margin-right: 0.8rem;
}}
.section-kicker {{
    font-size: 0.8rem;
    color: var(--ink-mute);
    font-style: italic;
    margin-bottom: 1rem;
    border-bottom: 1px dotted var(--hairline);
    padding-bottom: 0.8rem;
}}

/* Separador */
hr {{
    border: none !important;
    border-top: 1px solid var(--hairline) !important;
    margin: 2rem 0 !important;
}}

/* Caption */
[data-testid="stCaptionContainer"], .stCaption {{
    color: var(--ink-mute) !important;
    font-style: italic;
    font-size: 0.82rem !important;
}}

/* Plotly containers */
.js-plotly-plot {{
    border: 1px solid var(--hairline);
    border-radius: 2px;
    background: #fff;
    padding: 0.6rem;
}}

/* Radio sidebar */
[data-testid="stSidebar"] [role="radiogroup"] label {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 0.5rem 0.75rem;
    border-radius: 2px;
    margin-bottom: 0.3rem;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.85rem !important;
}}

/* Multiselect chips */
[data-baseweb="tag"] {{
    background: var(--blue-dark) !important;
    color: #fff !important;
    border-radius: 2px !important;
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =========================================================================
# Tema Plotly corporativo
# =========================================================================
CORPORATE_SEQUENCE = [
    COLORS["blue_dark"], COLORS["orange_deep"], COLORS["green_light"],
    COLORS["cyan"], COLORS["brown"], COLORS["blue"],
    COLORS["coral"], COLORS["amber"], COLORS["green_dark"], COLORS["orange"],
]

SCALE_BLUE = [
    [0.0, "#e8eef6"], [0.25, "#a9bedb"],
    [0.5, "#5f85b8"], [0.75, COLORS["blue"]], [1.0, COLORS["blue_dark"]],
]
SCALE_ORANGE = [
    [0.0, "#fbecd4"], [0.25, "#f3c77a"],
    [0.5, COLORS["orange"]], [0.75, COLORS["orange_deep"]], [1.0, COLORS["brown"]],
]
SCALE_GREEN = [
    [0.0, "#e1eee4"], [0.25, "#8ebfa0"],
    [0.5, COLORS["green_light"]], [0.75, COLORS["green_dark"]], [1.0, "#003d22"],
]

corporate_template = go.layout.Template()
corporate_template.layout = go.Layout(
    font=dict(family=f"{FONT_BODY}, sans-serif", color=COLORS["blue_dark"], size=12),
    title=dict(font=dict(family=f"{FONT_DISPLAY}, Georgia, serif", size=16, color="#0d1b2a")),
    paper_bgcolor="white",
    plot_bgcolor="white",
    colorway=CORPORATE_SEQUENCE,
    xaxis=dict(
        gridcolor="#ece7db", linecolor="#bfb8a6", zerolinecolor="#ece7db",
        ticks="outside", tickfont=dict(size=11, color="#4a5a6a"),
        title=dict(font=dict(size=11, color="#4a5a6a")),
    ),
    yaxis=dict(
        gridcolor="#ece7db", linecolor="#bfb8a6", zerolinecolor="#ece7db",
        ticks="outside", tickfont=dict(size=11, color="#4a5a6a"),
        title=dict(font=dict(size=11, color="#4a5a6a")),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", bordercolor="#d9d4c7", borderwidth=1,
        font=dict(size=11, color="#0d1b2a"),
    ),
    margin=dict(l=60, r=30, t=60, b=60),
)
pio.templates["corporate"] = corporate_template
pio.templates.default = "corporate"


# =========================================================================
# URLs GitHub
# =========================================================================
GH = {
    "pi":  "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/Plan%20Indicativo%202024-2027.xlsx",
    "h24": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20A%20DICIEMBRE%2031%20DEL%202024%20ENERO%2010%202025.xlsx",
    "r24": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/INFORME%20FINANCIERO%20REGALIAS%20A%2031%20DE%20DICIEMBRE%20DE%202024.xlsx",
    "h25": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20ENERO%20A%20DICIEMBRE%202025.xlsx",
    "r25": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/PAGOS%20REGALIAS%20ENERO%20-%20DICIEMBRE%202025.xlsx",
    "h26": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20HACIENDA%20PRUEBA%202026.xlsx",
    "r26": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/CG-cttos_04_marzo_20260304.xlsx",
}

# =========================================================================
# Utilidades
# =========================================================================
@st.cache_data(show_spinner=False)
def descargar_desde_github(url: str) -> bytes:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def formato_pesos(valor):
    try:
        v = float(valor)
        if abs(v) >= 1e9:
            return f"$ {v/1e9:,.2f} MM"
        if abs(v) >= 1e6:
            return f"$ {v/1e6:,.1f} M"
        return f"$ {v:,.0f}"
    except Exception:
        return valor


def formato_porcentaje(valor):
    try:
        return f"{valor*100:,.2f}%"
    except Exception:
        return valor


def seccion(numero: str, titulo: str, kicker: str = ""):
    st.markdown(
        f'<div class="section-title"><span class="num">{numero}</span>{titulo}</div>',
        unsafe_allow_html=True,
    )
    if kicker:
        st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)


def programacion_financiera(vigencia: str):
    return (
        pl.col("programación recursos propios icld" + vigencia)
        + pl.col("programación recursos propios icde" + vigencia)
        + pl.col("programación sgp educación" + vigencia)
        + pl.col("programación sgp salud" + vigencia)
        + pl.col("programación sgp apsb" + vigencia)
        + pl.col("programación cofinanciación municipio" + vigencia)
        + pl.col("programación cofinanciación nación" + vigencia)
        + pl.col("programación crédito" + vigencia)
        + pl.col("programación regalías" + vigencia)
        + pl.col("programación otras fuentes" + vigencia)
    )


# =========================================================================
# Procesamiento
# =========================================================================
@st.cache_data(show_spinner="Procesando datos del Plan Indicativo...")
def procesar_datos(pi_bytes, h24_bytes, r24_bytes, h25_bytes, r25_bytes, h26_bytes, r26_bytes):
    plan_indicativo = pl.read_excel(io.BytesIO(pi_bytes), table_name="tblPlanIndicativo_2")
    orden_lineas_pdd = pl.read_excel(io.BytesIO(pi_bytes), table_name="orden_lineas")
    orden_sectores_pdd = pl.read_excel(io.BytesIO(pi_bytes), table_name="orden_sectores")
    orden_programas_pdd = pl.read_excel(io.BytesIO(pi_bytes), table_name="orden_programas")
    homologacion_secretarias = pl.read_excel(io.BytesIO(pi_bytes), table_name="HomologacionSecretarias")

    columnas_prog_ejec_fisica = plan_indicativo.select(
        "Codigo Meta", "Línea Estratégica", "Sector PDD",
        "Numero Programa PDD", "Programa PDD", "Meta de cuatrenio",
        "Tipo de Acumulación", "Responsable", "Meta Física Esperada 2024",
        "Meta Física Esperada 2025", "Meta Física Esperada 2026", "Meta Física Esperada 2027",
        "PROYECTOS 2024", "PROYECTOS 2025", "PROYECTOS/GESTIONES PROGRAMADAS 2026", "PROYECTOS 2026",
        "PROYECTOS 2027", "EJECUCIÓN 2024", "PORCENTAJE DE EJECUCIÓN 2024", "CATEGORÍA DE EJECUCIÓN FÍSICA 2024",
        "EJECUCIÓN 2025", "PORCENTAJE DE EJECUCIÓN 2025", "CATEGORÍA DE EJECUCIÓN FÍSICA 2025",
        "EJECUCIÓN 2026", "PORCENTAJE DE EJECUCIÓN 2026", "CATEGORÍA DE EJECUCIÓN FÍSICA 2026",
        "EJECUCIÓN ACUMULADA", "PORCENTAJE DE EJECUCIÓN ACUMULADA", "CATEGORÍA DE EJECUCIÓN ACUMULADA",
    )

    ejecucion_regalias_2024 = (
        pl.read_excel(io.BytesIO(r24_bytes), table_name="EjecucionRegalias",
                      columns=["CODIGO META", "COMPROMISOS", "CLASIFICACIÓN RECURSOS"])
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "", pl.col("CODIGO META").str.starts_with("MT"))
        .rename({"COMPROMISOS": "RP"})
    )
    ejecucion_hacienda_2024 = (
        pl.read_excel(io.BytesIO(h24_bytes), table_name="EjecucionHaciendaDiciembre",
                      columns=["RP", "CODIGO META", "CLASIFICACIÓN RECURSOS"])
        .with_columns(pl.col("CODIGO META", "CLASIFICACIÓN RECURSOS").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "", pl.col("CLASIFICACIÓN RECURSOS") != "")
    )

    ejecucion_regalias_2025 = (
        pl.read_excel(io.BytesIO(r25_bytes), table_name="Pagos_Regalias_2025")
        .select("PAGOS REGALIAS", "CODIGO META", "CLASIFICACIÓN RECURSOS")
        .rename({"PAGOS REGALIAS": "RP"})
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "")
    )
    ejecucion_hacienda_2025 = (
        pl.read_excel(io.BytesIO(h25_bytes), table_name="EjecucionHaciendaDiciembre2025")
        .with_columns(
            pl.col("PROYECTO ARCHIVADO", "CODIGO META", "CLASIFICACIÓN RECURSOS", "SE VA A CARGAR EN PI").fill_null(pl.lit("")),
            pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA") == "SI").then(pl.col("RP") / 2).otherwise(pl.col("RP")),
        )
        .filter(pl.col("PROYECTO ARCHIVADO") == "", pl.col("CODIGO META") != "",
                pl.col("CLASIFICACIÓN RECURSOS") != "", pl.col("SE VA A CARGAR EN PI") == "")
        .select("CODIGO META", "CLASIFICACIÓN RECURSOS", "RP")
    )

    ejecucion_regalias_2026 = (
        pl.read_excel(io.BytesIO(r26_bytes), table_name="Pagos_Regalias_2026")
        .select(pl.all().name.map(lambda x: x.strip().upper().replace("_X0009_", "")))
        .filter(
            (pl.col("ULTIMA FECHA PAGO") >= pl.date(2026, 1, 1))
            & (pl.col("ULTIMA FECHA PAGO") <= pl.date(2026, 12, 31))
        )
        .select("PAGO EJECUTADO VALOR", "CODIGO META", "CLASIFICACIÓN RECURSOS")
        .rename({"PAGO EJECUTADO VALOR": "RP"})
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "")
    )
    ejecucion_hacienda_2026 = (
        pl.read_excel(io.BytesIO(h26_bytes), table_name="EjecucionHacienda2026")
        .with_columns(
            pl.col("PROYECTO ARCHIVADO", "CODIGO META", "CLASIFICACIÓN RECURSOS", "SE VA A CARGAR EN PI").fill_null(pl.lit("")),
            pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA") == "SI").then(pl.col("RP") / 2).otherwise(pl.col("RP")),
        )
        .filter(pl.col("PROYECTO ARCHIVADO") == "", pl.col("CODIGO META") != "",
                pl.col("CLASIFICACIÓN RECURSOS") != "", pl.col("SE VA A CARGAR EN PI") == "")
        .select("CODIGO META", "CLASIFICACIÓN RECURSOS", "RP")
    )

    ejec_2024 = pl.concat([ejecucion_regalias_2024, ejecucion_hacienda_2024], how="diagonal") \
        .group_by("CODIGO META").agg(pl.col("RP").sum().alias("Ejecución Financiera 2024"))
    ejec_2025 = pl.concat([ejecucion_regalias_2025, ejecucion_hacienda_2025], how="diagonal") \
        .group_by("CODIGO META").agg(pl.col("RP").sum().alias("Ejecución Financiera 2025"))
    ejec_2026 = pl.concat([ejecucion_regalias_2026, ejecucion_hacienda_2026], how="diagonal") \
        .group_by("CODIGO META").agg(pl.col("RP").sum().alias("Ejecución Financiera 2026"))

    columnas_programacion_financiera = (
        plan_indicativo.select("Codigo Meta", cs.starts_with("Programación").cast(pl.Float64))
        .select(pl.all().name.map(lambda x: x.strip().lower()))
        .select(
            "codigo meta",
            programacion_financiera("24").alias("Programación Financiera 2024"),
            programacion_financiera("25").alias("Programación Financiera 2025"),
            programacion_financiera("26").alias("Programación Financiera 2026"),
            programacion_financiera("27").alias("Programación Financiera 2027"),
        )
        .join(ejec_2024, left_on="codigo meta", right_on="CODIGO META", how="left")
        .join(ejec_2025, left_on="codigo meta", right_on="CODIGO META", how="left")
        .join(ejec_2026, left_on="codigo meta", right_on="CODIGO META", how="left")
        .with_columns(pl.col("Ejecución Financiera 2024", "Ejecución Financiera 2025", "Ejecución Financiera 2026").fill_null(pl.lit(0)))
    )

    orden_fuentes = pl.DataFrame({
        "Clasificación Recursos": ["COFINANCIACIÓN MUNICIPIO", "ICDE", "OTRAS FUENTES", "SGP APSB", "SGP SALUD",
                                   "SGP EDUCACION", "REGALÍAS", "COFINANCIACIÓN NACIÓN", "ICLD", "CREDITO"],
        "Orden": [1, 5, 3, 7, 9, 8, 10, 2, 6, 4],
        "Tipo Fuente": ["Otras Fuentes", "Recursos Propios", "Otras Fuentes",
                        "Sistema General de Participaciones (SGP)", "Sistema General de Participaciones (SGP)",
                        "Sistema General de Participaciones (SGP)", "Sistema General de Regalías",
                        "Otras Fuentes", "Recursos Propios", "Recursos del Crédito"],
    })

    prog_financ_tipo = (
        plan_indicativo.select(cs.starts_with("Programación"))
        .select(pl.all().name.map(lambda x: x.strip().lower()))
        .select(cs.exclude("programación total24", "programación total25", "programación total26", "programación total27"))
        .unpivot(on=cs.numeric(), variable_name="Clasificación Recursos", value_name="Programación financiera")
        .group_by("Clasificación Recursos").agg(pl.col("Programación financiera").sum())
        .with_columns(
            pl.col("Clasificación Recursos").str.slice(-2).alias("Vigencia"),
            pl.col("Clasificación Recursos").str.replace_all("programación ", "").str.replace_all(r"(24|25|26|27)", ""),
        )
        .with_columns((pl.lit("Programación Financiera 20") + pl.col("Vigencia")).alias("Vigencia"))
        .pivot(index="Clasificación Recursos", on="Vigencia", aggregate_function="sum")
        .with_columns(
            pl.col("Clasificación Recursos").str.replace_many(
                ["recursos propios icde", "cofinanciación nación", "sgp educación", "cofinanciación municipio",
                 "sgp salud", "sgp apsb", "otras fuentes", "regalías", "recursos propios icld", "crédito"],
                ["ICDE", "COFINANCIACIÓN NACIÓN", "SGP EDUCACION", "COFINANCIACIÓN MUNICIPIO",
                 "SGP SALUD", "SGP APSB", "OTRAS FUENTES", "REGALÍAS", "ICLD", "CREDITO"],
            )
        )
    )

    ejecuciones_financieras = {
        "2024": [ejecucion_regalias_2024, ejecucion_hacienda_2024],
        "2025": [ejecucion_regalias_2025, ejecucion_hacienda_2025],
        "2026": [ejecucion_regalias_2026, ejecucion_hacienda_2026],
    }

    prog_fisica_financiera = (
        columnas_prog_ejec_fisica.join(columnas_programacion_financiera, left_on="Codigo Meta", right_on="codigo meta", how="left")
        .with_columns(
            pl.col("Meta Física Esperada 2024", "Meta Física Esperada 2025",
                   "Meta Física Esperada 2026", "Meta Física Esperada 2027").fill_null(pl.lit(0))
        )
    )

    return {
        "plan_indicativo": plan_indicativo,
        "orden_lineas_pdd": orden_lineas_pdd,
        "orden_sectores_pdd": orden_sectores_pdd,
        "orden_programas_pdd": orden_programas_pdd,
        "homologacion_secretarias": homologacion_secretarias,
        "orden_fuentes": orden_fuentes,
        "prog_financ_tipo": prog_financ_tipo,
        "ejecuciones_financieras": ejecuciones_financieras,
        "prog_fisica_financiera": prog_fisica_financiera,
    }


# =========================================================================
# Constructores de reportes por vigencia
# =========================================================================
def construir_ejecucion_financ_tipo(datos, vigencia):
    ejecuciones = datos["ejecuciones_financieras"][vigencia]
    orden_fuentes = datos["orden_fuentes"]
    prog_financ_tipo = datos["prog_financ_tipo"]

    return (
        orden_fuentes.join(
            pl.concat(ejecuciones, how="diagonal"),
            left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left",
        )
        .group_by("Clasificación Recursos").agg(pl.col("RP").sum().alias(f"Ejecución Financiera {vigencia}"))
        .join(orden_fuentes, on="Clasificación Recursos", how="inner")
        .join(prog_financ_tipo, on="Clasificación Recursos", how="inner")
        .select("Orden", "Tipo Fuente", "Clasificación Recursos",
                f"Programación Financiera {vigencia}", f"Ejecución Financiera {vigencia}")
        .with_columns(
            (pl.when(pl.col(f"Programación Financiera {vigencia}") == 0)
             .then(pl.lit(0))
             .otherwise(pl.col(f"Ejecución Financiera {vigencia}") / pl.col(f"Programación Financiera {vigencia}"))
             ).alias("Porcentaje de Ejecución Financiera")
        )
        .sort(by="Orden")
    )


def construir_ejecucion_acumulada_tipo(datos):
    orden_fuentes = datos["orden_fuentes"]
    prog_financ_tipo = datos["prog_financ_tipo"]

    agrp = {}
    for v in ["2024", "2025", "2026"]:
        agrp[v] = (
            pl.concat(datos["ejecuciones_financieras"][v], how="diagonal")
            .group_by("CLASIFICACIÓN RECURSOS")
            .agg(pl.col("RP").sum().alias(f"Ejecución Financiera {v}"))
        )

    return (
        orden_fuentes
        .join(agrp["2024"], left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left")
        .join(agrp["2025"], left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left")
        .join(agrp["2026"], left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left")
        .join(prog_financ_tipo, on="Clasificación Recursos")
        .with_columns(
            pl.col("Ejecución Financiera 2024", "Ejecución Financiera 2025", "Ejecución Financiera 2026").fill_null(pl.lit(0))
        )
        .with_columns(
            (pl.col("Ejecución Financiera 2024") + pl.col("Ejecución Financiera 2025")
             + pl.col("Ejecución Financiera 2026")).alias("Ejecución Financiera Acumulada"),
            (pl.col("Programación Financiera 2024") + pl.col("Programación Financiera 2025")
             + pl.col("Programación Financiera 2026") + pl.col("Programación Financiera 2027")
             ).alias("Programación Cuatrienio"),
        )
        .select("Orden", "Tipo Fuente", "Clasificación Recursos",
                "Programación Financiera 2024", "Programación Financiera 2025", "Programación Financiera 2026",
                "Ejecución Financiera 2024", "Ejecución Financiera 2025", "Ejecución Financiera 2026",
                "Programación Cuatrienio", "Ejecución Financiera Acumulada")
        .sort(by="Orden")
    )


def construir_prog_financ_categorias(datos, vigencia):
    prog_ff = datos["prog_fisica_financiera"]
    orden_lineas = datos["orden_lineas_pdd"]
    orden_sectores = datos["orden_sectores_pdd"]
    orden_programas = datos["orden_programas_pdd"]

    def agregar(grupo, orden_df, col_orden):
        return (
            prog_ff.group_by(grupo).agg(
                pl.col(f"Programación Financiera {vigencia}").sum(),
                pl.col(f"Ejecución Financiera {vigencia}").sum(),
            )
            .join(orden_df, on=grupo, how="inner")
            .with_columns(
                (pl.when(pl.col(f"Programación Financiera {vigencia}") == 0)
                 .then(pl.lit(0))
                 .otherwise(pl.col(f"Ejecución Financiera {vigencia}") / pl.col(f"Programación Financiera {vigencia}"))
                 ).alias("Porcentaje de Ejecución Financiera")
            )
            .sort(col_orden)
            .select(col_orden, grupo, f"Programación Financiera {vigencia}",
                    f"Ejecución Financiera {vigencia}", "Porcentaje de Ejecución Financiera")
        )

    return {
        "lineas": agregar("Línea Estratégica", orden_lineas, "Orden Linea"),
        "sectores": agregar("Sector PDD", orden_sectores, "Orden Sector"),
        "programas": agregar("Programa PDD", orden_programas, "Orden Programa PDD"),
    }


def construir_ejec_por_dependencia(datos, vigencia):
    prog_ff = datos["prog_fisica_financiera"]
    homologacion = datos["homologacion_secretarias"]

    ejec_acumulada = (
        prog_ff.select(pl.col("Responsable").str.strip_chars(), "PORCENTAJE DE EJECUCIÓN ACUMULADA")
        .group_by("Responsable")
        .agg(pl.col("PORCENTAJE DE EJECUCIÓN ACUMULADA").fill_null(pl.lit(0)).mean().alias("Porcentaje de Ejecución Acumulada"))
    )

    return (
        prog_ff.select(
            pl.col("Responsable").str.strip_chars(), f"Meta Física Esperada {vigencia}",
            f"PORCENTAJE DE EJECUCIÓN {vigencia}", f"CATEGORÍA DE EJECUCIÓN FÍSICA {vigencia}"
        )
        .filter(pl.col(f"Meta Física Esperada {vigencia}").fill_null(pl.lit(0)) != 0)
        .with_columns(
            (pl.when(pl.col(f"Meta Física Esperada {vigencia}") != 0).then(pl.lit(1)).otherwise(pl.lit(0))
             ).alias(f"Metas Programadas {vigencia}"),
            (pl.when(pl.col(f"CATEGORÍA DE EJECUCIÓN FÍSICA {vigencia}") == "Superior").then(pl.lit(1)).otherwise(pl.lit(0))
             ).alias(f"Metas Cumplidas al 100% {vigencia}"),
        )
        .group_by("Responsable").agg(
            pl.col(f"PORCENTAJE DE EJECUCIÓN {vigencia}").fill_null(pl.lit(0)).mean().alias(f"Porcentaje de Ejecución {vigencia}"),
            pl.col(f"Metas Programadas {vigencia}").sum(),
            pl.col(f"Metas Cumplidas al 100% {vigencia}").sum(),
        )
        .join(homologacion, left_on="Responsable", right_on="Responsable en PI", how="left")
        .join(ejec_acumulada, on="Responsable", how="left")
        .select("Varias Secretarías", "Dependencia Responsable",
                f"Metas Programadas {vigencia}", f"Metas Cumplidas al 100% {vigencia}",
                f"Porcentaje de Ejecución {vigencia}", "Porcentaje de Ejecución Acumulada")
    )


def construir_avances_fisicos(datos, vigencia):
    prog_ff = datos["prog_fisica_financiera"]

    numero_total_metas = prog_ff.get_column("Codigo Meta").count()
    numero_metas_prog_vigencia = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0).get_column("Codigo Meta").count()
    )

    promedio_programas = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0)
        .group_by("Programa PDD").agg(pl.col(f"PORCENTAJE DE EJECUCIÓN {vigencia}").mean())
        .rename({f"PORCENTAJE DE EJECUCIÓN {vigencia}": "Promedio de avance de ejecución de la vigencia"})
    )

    num_metas_lineas_cp = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0)
        .group_by("Línea Estratégica").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto con Programacion"})
    )
    num_metas_lineas = (
        prog_ff.group_by("Línea Estratégica").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto"})
    )
    num_metas_sectores_cp = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0)
        .group_by("Sector PDD").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto con Programacion"})
    )
    num_metas_sectores = (
        prog_ff.group_by("Sector PDD").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto"})
    )
    num_metas_programas = (
        prog_ff.group_by("Programa PDD").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto"})
    )

    ponderado_vigencia = (
        prog_ff
        .with_columns(
            (pl.when(pl.col(f"Meta Física Esperada {vigencia}") != 0).then(pl.lit(1)).otherwise(pl.lit(0))
             ).alias(f"Metas Programadas {vigencia}")
        )
        .group_by("Línea Estratégica", "Sector PDD", "Programa PDD")
        .agg(pl.col(f"Metas Programadas {vigencia}").sum())
        .with_columns(
            (pl.col(f"Metas Programadas {vigencia}") / max(numero_metas_prog_vigencia, 1)
             ).alias("Sobre Numero Total de Metas Programadas")
        )
        .join(promedio_programas, on="Programa PDD", how="left")
        .with_columns(pl.col("Promedio de avance de ejecución de la vigencia").fill_null(pl.lit(0)))
        .rename({f"Metas Programadas {vigencia}": "Total Indicadores de Producto Programados"})
    )

    ponderado_cuatrienio = (
        prog_ff.group_by("Línea Estratégica", "Sector PDD", "Programa PDD")
        .agg(pl.col("PORCENTAJE DE EJECUCIÓN ACUMULADA").fill_null(pl.lit(0)).mean())
        .join(num_metas_programas, on="Programa PDD")
        .with_columns((pl.col("Total Indicadores de Producto") / max(numero_total_metas, 1)).alias("Sobre Numero Total de Metas"))
        .rename({"PORCENTAJE DE EJECUCIÓN ACUMULADA": "Promedio de avance de ejecución acumulada"})
    )

    avance_vig_ponderado = ponderado_vigencia.select(
        pl.col("Promedio de avance de ejecución de la vigencia") * pl.col("Sobre Numero Total de Metas Programadas")
    ).sum().item()

    avance_cuatrienio_total = ponderado_cuatrienio.select(
        pl.col("Promedio de avance de ejecución acumulada") * pl.col("Sobre Numero Total de Metas")
    ).sum().item()

    def avance_por_dim(ponderado, grupo, num_metas_df, total, col_avance, col_metas):
        return (
            ponderado.group_by(grupo)
            .agg((pl.col(col_avance) * pl.col(col_metas)).sum())
            .rename({col_avance: "% Aporte Cumplimiento PDD"})
            .join(num_metas_df, on=grupo)
            .with_columns((pl.col(num_metas_df.columns[1]) / max(total, 1)).alias("Sobre Numero Total de Indicadores"))
            .with_columns(
                (pl.when(pl.col("Sobre Numero Total de Indicadores") == 0)
                 .then(pl.lit(0))
                 .otherwise(pl.col("% Aporte Cumplimiento PDD") / pl.col("Sobre Numero Total de Indicadores"))
                 ).alias("% Eficacia Operativa")
            )
        )

    return {
        "avance_vig_ponderado": avance_vig_ponderado,
        "avance_cuatrienio_total": avance_cuatrienio_total,
        "avance_vig_lineas": avance_por_dim(
            ponderado_vigencia, "Línea Estratégica", num_metas_lineas_cp, numero_metas_prog_vigencia,
            "Promedio de avance de ejecución de la vigencia", "Sobre Numero Total de Metas Programadas"),
        "avance_cuatri_lineas": avance_por_dim(
            ponderado_cuatrienio, "Línea Estratégica", num_metas_lineas, numero_total_metas,
            "Promedio de avance de ejecución acumulada", "Sobre Numero Total de Metas"),
        "avance_vig_sectores": avance_por_dim(
            ponderado_vigencia, "Sector PDD", num_metas_sectores_cp, numero_metas_prog_vigencia,
            "Promedio de avance de ejecución de la vigencia", "Sobre Numero Total de Metas Programadas"),
        "avance_cuatri_sectores": avance_por_dim(
            ponderado_cuatrienio, "Sector PDD", num_metas_sectores, numero_total_metas,
            "Promedio de avance de ejecución acumulada", "Sobre Numero Total de Metas"),
        "numero_total_metas": numero_total_metas,
        "numero_metas_prog_vigencia": numero_metas_prog_vigencia,
    }


# =========================================================================
# Sidebar
# =========================================================================
st.sidebar.markdown(
    f"""
    <div style='padding: 0.8rem 0 1.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1rem;'>
        <div style='font-family: {FONT_MONO}, monospace; font-size: 0.68rem; letter-spacing: 0.22em;
                    color: {COLORS["orange"]}; text-transform: uppercase;'>
            Plan de Desarrollo
        </div>
        <div style='font-family: {FONT_DISPLAY}, Georgia, serif; font-size: 1.5rem;
                    font-weight: 700; color: #fff; line-height: 1; margin-top: 0.2rem;
                    font-style: italic;'>
            2024<span style='color: {COLORS["orange"]}'>—</span>2027
        </div>
        <div style='font-family: {FONT_BODY}, sans-serif; font-size: 0.75rem;
                    color: #b9c6d6; margin-top: 0.4rem; letter-spacing: 0.04em;'>
            Sistema de Seguimiento
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Origen de los datos")
fuente = st.sidebar.radio(
    "Fuente",
    options=["Repositorio GitHub", "Cargar archivos"],
    index=0,
    label_visibility="collapsed",
)

archivos_bytes = {}

if fuente == "Repositorio GitHub":
    if st.sidebar.button("Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    try:
        with st.spinner("Descargando archivos del repositorio..."):
            for key, url in GH.items():
                archivos_bytes[key] = descargar_desde_github(url)
    except Exception as e:
        st.sidebar.error(f"Error al descargar: {e}")
        st.stop()
else:
    st.sidebar.markdown("**Archivos requeridos**")
    uploads = {
        "pi": st.sidebar.file_uploader("Plan Indicativo", type=["xlsx"], key="pi"),
        "h24": st.sidebar.file_uploader("Hacienda 2024", type=["xlsx"], key="h24"),
        "r24": st.sidebar.file_uploader("Regalías 2024", type=["xlsx"], key="r24"),
        "h25": st.sidebar.file_uploader("Hacienda 2025", type=["xlsx"], key="h25"),
        "r25": st.sidebar.file_uploader("Regalías 2025", type=["xlsx"], key="r25"),
        "h26": st.sidebar.file_uploader("Hacienda 2026", type=["xlsx"], key="h26"),
        "r26": st.sidebar.file_uploader("Regalías 2026", type=["xlsx"], key="r26"),
    }
    if not all(uploads.values()):
        st.warning("Sube los siete archivos en la barra lateral para continuar.")
        st.stop()
    archivos_bytes = {k: v.getvalue() for k, v in uploads.items()}

# Procesamiento
try:
    datos = procesar_datos(
        archivos_bytes["pi"], archivos_bytes["h24"], archivos_bytes["r24"],
        archivos_bytes["h25"], archivos_bytes["r25"],
        archivos_bytes["h26"], archivos_bytes["r26"],
    )
except Exception as e:
    st.error(f"Error procesando los archivos: {e}")
    st.exception(e)
    st.stop()

st.sidebar.markdown("### Vigencia de análisis")
filtro_vigencia = st.sidebar.selectbox(
    "Vigencia",
    options=["2024", "2025", "2026"],
    index=2,
    label_visibility="collapsed",
)

# =========================================================================
# Masthead editorial
# =========================================================================
st.markdown(
    f"""
    <div class="masthead">
        <div>
            <div class="eyebrow">Informe de Seguimiento  /  Número {filtro_vigencia[-2:]}</div>
            <h1>Plan <em>Indicativo</em></h1>
        </div>
        <div class="edition">
            <strong>Vigencia en análisis</strong><br/>
            {filtro_vigencia} · Cuatrienio 2024—2027<br/>
            Ejecución física y financiera
        </div>
    </div>
    <div class="subhead">
        Instrumento de seguimiento al cumplimiento de metas del Plan de Desarrollo.
        Consolida la programación y ejecución de los indicadores de producto y sus fuentes de financiación.
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================================
# Cálculos
# =========================================================================
ejec_financ_tipo = construir_ejecucion_financ_tipo(datos, filtro_vigencia)
ejec_acumulada_tipo = construir_ejecucion_acumulada_tipo(datos)
categorias_pdd = construir_prog_financ_categorias(datos, filtro_vigencia)
ejec_dependencia = construir_ejec_por_dependencia(datos, filtro_vigencia)
avances_fisicos = construir_avances_fisicos(datos, filtro_vigencia)

# =========================================================================
# KPIs
# =========================================================================
prog_vig = ejec_financ_tipo.select(pl.col(f"Programación Financiera {filtro_vigencia}").sum()).item() or 0
ejec_vig = ejec_financ_tipo.select(pl.col(f"Ejecución Financiera {filtro_vigencia}").sum()).item() or 0
pct_vig = (ejec_vig / prog_vig) if prog_vig else 0

prog_cuatri = ejec_acumulada_tipo.select(pl.col("Programación Cuatrienio").sum()).item() or 0
ejec_acum = ejec_acumulada_tipo.select(pl.col("Ejecución Financiera Acumulada").sum()).item() or 0
pct_cuatri = (ejec_acum / prog_cuatri) if prog_cuatri else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Programación {filtro_vigencia}", formato_pesos(prog_vig))
c2.metric(f"Ejecución {filtro_vigencia}", formato_pesos(ejec_vig), formato_porcentaje(pct_vig))
c3.metric("Programación Cuatrienio", formato_pesos(prog_cuatri))
c4.metric("Ejecución Acumulada", formato_pesos(ejec_acum), formato_porcentaje(pct_cuatri))

st.markdown("<hr/>", unsafe_allow_html=True)

# =========================================================================
# Pestañas
# =========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Ejecución Física",
    "Ejecución Financiera",
    "Distribución de Metas",
    "Ejecución por Dependencia",
    "Detalle por Meta",
])

# -----------------------------------------------------------------
# 01. EJECUCIÓN FÍSICA
# -----------------------------------------------------------------
with tab1:
    seccion("01", "Ejecución Física",
            "Avance ponderado del cumplimiento de metas físicas del Plan de Desarrollo.")

    k1, k2 = st.columns(2)
    k1.metric(f"Avance ponderado — Vigencia {filtro_vigencia}",
              formato_porcentaje(avances_fisicos["avance_vig_ponderado"] or 0))
    k2.metric("Avance ponderado — Cuatrienio",
              formato_porcentaje(avances_fisicos["avance_cuatrienio_total"] or 0))

    st.markdown(" ")
    sub_v, sub_c = st.tabs([f"Vigencia {filtro_vigencia}", "Cuatrienio"])

    def grafica_lineas(df, titulo, color_scale):
        df = df.sort_values("% Eficacia Operativa", ascending=True)
        fig = px.bar(
            df, x="% Eficacia Operativa", y="Línea Estratégica",
            orientation="h", text="% Eficacia Operativa",
            color="% Eficacia Operativa", color_continuous_scale=color_scale,
            title=titulo,
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside",
                          marker_line_color=COLORS["blue_dark"], marker_line_width=0.5)
        fig.update_layout(xaxis_tickformat=".0%", height=480, showlegend=False,
                          coloraxis_showscale=False, bargap=0.35)
        return fig

    def grafica_sectores(df, titulo, color_scale):
        df = df.sort_values("% Eficacia Operativa", ascending=True)
        fig = px.bar(
            df, x="% Eficacia Operativa", y="Sector PDD",
            orientation="h", text="% Eficacia Operativa",
            color="% Eficacia Operativa", color_continuous_scale=color_scale,
            title=titulo,
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside",
                          marker_line_color=COLORS["blue_dark"], marker_line_width=0.5)
        fig.update_layout(xaxis_tickformat=".0%", height=max(500, len(df) * 30),
                          showlegend=False, coloraxis_showscale=False, bargap=0.3)
        return fig

    with sub_v:
        st.markdown("##### Por Línea Estratégica")
        df = avances_fisicos["avance_vig_lineas"].to_pandas()
        if not df.empty:
            st.plotly_chart(
                grafica_lineas(df, f"Eficacia Operativa por Línea Estratégica — {filtro_vigencia}", SCALE_BLUE),
                use_container_width=True,
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Sin datos para la vigencia seleccionada.")

        st.markdown("##### Por Sector PDD")
        df = avances_fisicos["avance_vig_sectores"].to_pandas()
        if not df.empty:
            st.plotly_chart(
                grafica_sectores(df, f"Eficacia Operativa por Sector PDD — {filtro_vigencia}", SCALE_BLUE),
                use_container_width=True,
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

    with sub_c:
        st.markdown("##### Por Línea Estratégica")
        df = avances_fisicos["avance_cuatri_lineas"].to_pandas()
        st.plotly_chart(
            grafica_lineas(df, "Eficacia Operativa por Línea Estratégica — Cuatrienio", SCALE_GREEN),
            use_container_width=True,
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("##### Por Sector PDD")
        df = avances_fisicos["avance_cuatri_sectores"].to_pandas()
        st.plotly_chart(
            grafica_sectores(df, "Eficacia Operativa por Sector PDD — Cuatrienio", SCALE_GREEN),
            use_container_width=True,
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# 02. EJECUCIÓN FINANCIERA
# -----------------------------------------------------------------
with tab2:
    seccion("02", "Ejecución Financiera",
            "Comportamiento de recursos programados frente a ejecutados por fuente y categoría del PDD.")

    sub_v, sub_c = st.tabs([f"Vigencia {filtro_vigencia}", "Cuatrienio"])

    with sub_v:
        k1, k2, k3 = st.columns(3)
        k1.metric("Programación", formato_pesos(prog_vig))
        k2.metric("Ejecución", formato_pesos(ejec_vig))
        k3.metric("Avance", formato_porcentaje(pct_vig))

        st.markdown("##### Por Clasificación de Recursos")
        df_tipo = ejec_financ_tipo.to_pandas()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Programación", x=df_tipo["Clasificación Recursos"],
            y=df_tipo[f"Programación Financiera {filtro_vigencia}"],
            marker=dict(color=COLORS["blue_dark"], line=dict(color="#fff", width=1)),
        ))
        fig.add_trace(go.Bar(
            name="Ejecución", x=df_tipo["Clasificación Recursos"],
            y=df_tipo[f"Ejecución Financiera {filtro_vigencia}"],
            marker=dict(color=COLORS["orange_deep"], line=dict(color="#fff", width=1)),
        ))
        fig.update_layout(
            barmode="group", height=460,
            title=f"Programación vs Ejecución por Fuente — {filtro_vigencia}",
            yaxis_title="Valor (COP)", xaxis_tickangle=-25, bargap=0.25,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_tipo, use_container_width=True, hide_index=True)

        st.markdown("##### Por Categorías del Plan de Desarrollo")
        cat1, cat2, cat3 = st.tabs(["Líneas Estratégicas", "Sectores PDD", "Programas PDD"])

        with cat1:
            df = categorias_pdd["lineas"].to_pandas()
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Programación", x=df["Línea Estratégica"],
                y=df[f"Programación Financiera {filtro_vigencia}"],
                marker_color=COLORS["blue_dark"],
            ))
            fig.add_trace(go.Bar(
                name="Ejecución", x=df["Línea Estratégica"],
                y=df[f"Ejecución Financiera {filtro_vigencia}"],
                marker_color=COLORS["orange_deep"],
            ))
            fig.update_layout(barmode="group", height=460,
                              title=f"Programación vs Ejecución por Línea — {filtro_vigencia}",
                              xaxis_tickangle=-20)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

        with cat2:
            df = categorias_pdd["sectores"].to_pandas()
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Programación", x=df["Sector PDD"],
                y=df[f"Programación Financiera {filtro_vigencia}"],
                marker_color=COLORS["blue_dark"],
            ))
            fig.add_trace(go.Bar(
                name="Ejecución", x=df["Sector PDD"],
                y=df[f"Ejecución Financiera {filtro_vigencia}"],
                marker_color=COLORS["orange_deep"],
            ))
            fig.update_layout(barmode="group", height=560,
                              title=f"Programación vs Ejecución por Sector — {filtro_vigencia}",
                              xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

        with cat3:
            df = categorias_pdd["programas"].to_pandas()
            st.dataframe(df, use_container_width=True, hide_index=True, height=520)

    with sub_c:
        k1, k2, k3 = st.columns(3)
        k1.metric("Programación Cuatrienio", formato_pesos(prog_cuatri))
        k2.metric("Ejecución Acumulada", formato_pesos(ejec_acum))
        k3.metric("Avance", formato_porcentaje(pct_cuatri))

        df_acum = ejec_acumulada_tipo.to_pandas()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Ejecución 2024", x=df_acum["Clasificación Recursos"],
                             y=df_acum["Ejecución Financiera 2024"], marker_color=COLORS["green_light"]))
        fig.add_trace(go.Bar(name="Ejecución 2025", x=df_acum["Clasificación Recursos"],
                             y=df_acum["Ejecución Financiera 2025"], marker_color=COLORS["blue"]))
        fig.add_trace(go.Bar(name="Ejecución 2026", x=df_acum["Clasificación Recursos"],
                             y=df_acum["Ejecución Financiera 2026"], marker_color=COLORS["orange_deep"]))
        fig.update_layout(barmode="stack", height=520,
                          title="Ejecución Acumulada por Fuente (2024-2026)",
                          yaxis_title="Valor (COP)", xaxis_tickangle=-25, bargap=0.25)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_acum, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# 03. DISTRIBUCIÓN DE METAS
# -----------------------------------------------------------------
with tab3:
    seccion("03", "Distribución de Metas",
            "Peso relativo de la programación física en cada vigencia del cuatrienio.")

    prog_ff = datos["prog_fisica_financiera"]
    programacion_cuatrienio = prog_ff.select(pl.col("Meta de cuatrenio").sum()).item() or 1

    distribucion = {
        "2024": (prog_ff.select(pl.col("Meta Física Esperada 2024").sum()).item() or 0) / programacion_cuatrienio,
        "2025": (prog_ff.select(pl.col("Meta Física Esperada 2025").sum()).item() or 0) / programacion_cuatrienio,
        "2026": (prog_ff.select(pl.col("Meta Física Esperada 2026").sum()).item() or 0) / programacion_cuatrienio,
        "2027": (prog_ff.select(pl.col("Meta Física Esperada 2027").sum()).item() or 0) / programacion_cuatrienio,
    }

    df_dist = pd.DataFrame({"Vigencia": list(distribucion.keys()),
                            "Distribución": list(distribucion.values())})

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            df_dist, values="Distribución", names="Vigencia",
            title="Distribución por vigencia", hole=0.55,
            color_discrete_sequence=[COLORS["blue_dark"], COLORS["cyan"],
                                     COLORS["orange_deep"], COLORS["brown"]],
        )
        fig.update_traces(
            textinfo="label+percent",
            textfont=dict(family=FONT_DISPLAY, size=14, color="#fff"),
            marker=dict(line=dict(color="#fff", width=2)),
        )
        fig.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_dist, x="Vigencia", y="Distribución",
            text="Distribución", color="Vigencia",
            title="Distribución por vigencia",
            color_discrete_sequence=[COLORS["blue_dark"], COLORS["cyan"],
                                     COLORS["orange_deep"], COLORS["brown"]],
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside",
                          marker_line_color=COLORS["blue_dark"], marker_line_width=0.5)
        fig.update_layout(yaxis_tickformat=".0%", height=430, showlegend=False,
                          bargap=0.45)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        df_dist.assign(**{"Distribución": df_dist["Distribución"].map(lambda x: f"{x*100:.2f}%")}),
        use_container_width=True, hide_index=True,
    )

    st.markdown(" ")
    st.markdown("##### Conteo de Metas")
    a, b = st.columns(2)
    a.metric("Total de indicadores de producto",
             f"{avances_fisicos['numero_total_metas']:,}")
    b.metric(f"Indicadores con programación en {filtro_vigencia}",
             f"{avances_fisicos['numero_metas_prog_vigencia']:,}")

# -----------------------------------------------------------------
# 04. EJECUCIÓN POR DEPENDENCIA
# -----------------------------------------------------------------
with tab4:
    seccion("04", "Ejecución por Dependencia",
            "Desempeño de las dependencias responsables de la ejecución del Plan de Desarrollo.")

    df_dep = ejec_dependencia.to_pandas()

    varias_opciones = sorted([x for x in df_dep["Varias Secretarías"].dropna().unique()])
    if varias_opciones:
        filtro_sec = st.multiselect(
            "Filtrar por agrupación (Varias Secretarías)",
            options=varias_opciones, default=[],
        )
        if filtro_sec:
            df_dep = df_dep[df_dep["Varias Secretarías"].isin(filtro_sec)]

    if df_dep.empty:
        st.info("No hay dependencias con metas programadas en la vigencia seleccionada.")
    else:
        df_plot = df_dep.sort_values(f"Porcentaje de Ejecución {filtro_vigencia}", ascending=True)
        fig = px.bar(
            df_plot, x=f"Porcentaje de Ejecución {filtro_vigencia}", y="Dependencia Responsable",
            orientation="h", text=f"Porcentaje de Ejecución {filtro_vigencia}",
            color=f"Porcentaje de Ejecución {filtro_vigencia}", color_continuous_scale=SCALE_ORANGE,
            title=f"Porcentaje de Ejecución Física por Dependencia — {filtro_vigencia}",
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside",
                          marker_line_color=COLORS["brown"], marker_line_width=0.5)
        fig.update_layout(xaxis_tickformat=".0%",
                          height=max(450, len(df_plot) * 32),
                          showlegend=False, coloraxis_showscale=False, bargap=0.25)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Resumen por dependencia")
        df_show = df_dep.copy()
        df_show[f"Porcentaje de Ejecución {filtro_vigencia}"] = df_show[f"Porcentaje de Ejecución {filtro_vigencia}"].map(
            lambda x: f"{x*100:.2f}%" if pd.notna(x) else ""
        )
        df_show["Porcentaje de Ejecución Acumulada"] = df_show["Porcentaje de Ejecución Acumulada"].map(
            lambda x: f"{x*100:.2f}%" if pd.notna(x) else ""
        )
        st.dataframe(df_show, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# 05. DETALLE POR META
# -----------------------------------------------------------------
with tab5:
    seccion("05", "Detalle por Meta",
            "Consulta del inventario completo de indicadores de producto del Plan Indicativo.")

    prog_ff = datos["prog_fisica_financiera"]
    df_all = prog_ff.to_pandas()

    f1, f2, f3 = st.columns(3)
    with f1:
        lineas = ["(Todas)"] + sorted(df_all["Línea Estratégica"].dropna().unique().tolist())
        sel_linea = st.selectbox("Línea Estratégica", lineas)
    with f2:
        df_temp = df_all if sel_linea == "(Todas)" else df_all[df_all["Línea Estratégica"] == sel_linea]
        sectores = ["(Todos)"] + sorted(df_temp["Sector PDD"].dropna().unique().tolist())
        sel_sector = st.selectbox("Sector PDD", sectores)
    with f3:
        df_temp2 = df_temp if sel_sector == "(Todos)" else df_temp[df_temp["Sector PDD"] == sel_sector]
        programas = ["(Todos)"] + sorted(df_temp2["Programa PDD"].dropna().unique().tolist())
        sel_programa = st.selectbox("Programa PDD", programas)

    df_filt = df_all.copy()
    if sel_linea != "(Todas)":
        df_filt = df_filt[df_filt["Línea Estratégica"] == sel_linea]
    if sel_sector != "(Todos)":
        df_filt = df_filt[df_filt["Sector PDD"] == sel_sector]
    if sel_programa != "(Todos)":
        df_filt = df_filt[df_filt["Programa PDD"] == sel_programa]

    st.caption(f"Mostrando {len(df_filt):,} metas")
    st.dataframe(df_filt, use_container_width=True, height=600)

    csv_bytes = df_filt.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar CSV",
        data=csv_bytes,
        file_name=f"detalle_metas_{filtro_vigencia}.csv",
        mime="text/csv",
    )

# =========================================================================
# Pie de página
# =========================================================================
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style='display: flex; justify-content: space-between; align-items: center;
                padding: 0.6rem 0 1.2rem 0; font-size: 0.75rem; color: {COLORS["blue_dark"]};
                font-family: {FONT_MONO}, monospace; letter-spacing: 0.08em;
                border-top: 1px solid #d9d4c7;'>
        <span>Plan Indicativo · Sistema de Seguimiento 2024—2027</span>
        <span>Construido con Streamlit · Polars · Plotly</span>
    </div>
    """,
    unsafe_allow_html=True,
)
