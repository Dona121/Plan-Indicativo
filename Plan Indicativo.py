"""
Dashboard de Reporte de Avance PDD
Basado en el analisis del notebook ReporteAvance.ipynb
"""

import streamlit as st
import polars as pl
import polars.selectors as cs
import pandas as pd
import plotly.graph_objects as go
import io
import requests
from typing import Optional
import tempfile

# -------------------------------------------------
# PALETA CORPORATIVA
# -------------------------------------------------
COLORS = {
    "verde_oscuro":    "#17743d",
    "verde_medio":     "#005931",
    "cyan":            "#47b1d5",
    "azul_medio":      "#1754ab",
    "azul_oscuro":     "#003d6c",
    "naranja_claro":   "#d88c16",
    "naranja":         "#cf7000",
    "naranja_quemado": "#d37e00",
    "cafe":            "#9b5b1e",
    "salmon":          "#e68878",
    "blanco":          "#ffffff",
    "gris_fondo":      "#f4f6f9",
    "gris_texto":      "#2d3142",
}

CAT_COLORS = {
    "Superior":      COLORS["verde_oscuro"],
    "Alto":          COLORS["cyan"],
    "Medio":         COLORS["naranja_claro"],
    "Bajo":          COLORS["naranja"],
    "Critico":       COLORS["salmon"],
    "Sin Programar": COLORS["cafe"],
}

VIGENCIAS = ["2024", "2025", "2026"]

# -------------------------------------------------
# NOMBRES DE COLUMNAS EXACTOS DEL ARCHIVO EXCEL
# Extraidos directamente del notebook ReporteAvance.ipynb
# -------------------------------------------------

# Columnas del Plan Indicativo con sus nombres reales (incluyen tildes)
COLS_PI_REAL = [
    "Codigo Meta",
    "L\u00ednea Estrat\u00e9gica",                          # Línea Estratégica
    "Sector PDD",
    "Numero Programa PDD",
    "Programa PDD",
    "Meta de cuatrenio",
    "Tipo de Acumulaci\u00f3n",                              # Tipo de Acumulación
    "Responsable",
    "Meta F\u00edsica Esperada 2024",                        # Meta Física Esperada 2024
    "Meta F\u00edsica Esperada 2025",
    "Meta F\u00edsica Esperada 2026",
    "Meta F\u00edsica Esperada 2027",
    "PROYECTOS 2024",
    "PROYECTOS 2025",
    "PROYECTOS/GESTIONES PROGRAMADAS 2026",
    "PROYECTOS 2026",
    "PROYECTOS 2027",
    "EJECUCI\u00d3N 2024",                                  # EJECUCIÓN 2024
    "PORCENTAJE DE EJECUCI\u00d3N 2024",                    # PORCENTAJE DE EJECUCIÓN 2024
    "CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA 2024",   # CATEGORÍA DE EJECUCIÓN FÍSICA 2024
    "EJECUCI\u00d3N 2025",
    "PORCENTAJE DE EJECUCI\u00d3N 2025",
    "CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA 2025",
    "EJECUCI\u00d3N 2026",
    "PORCENTAJE DE EJECUCI\u00d3N 2026",
    "CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA 2026",
    "EJECUCI\u00d3N ACUMULADA",
    "PORCENTAJE DE EJECUCI\u00d3N ACUMULADA",
    "CATEGOR\u00cdA DE EJECUCI\u00d3N ACUMULADA",
]

# Columnas de programacion financiera (en lowercase, con tildes, tal como estan en el PI)
# El notebook hace: plan_indicativo.select(...).select(pl.all().name.map(lambda x: x.strip().lower()))
# y luego usa: "programacion recursos propios icld24", "programacion regalias24", etc.
PROG_FIN_COLS = {
    "24": [
        "programaci\u00f3n recursos propios icld24",         # programación recursos propios icld24
        "programaci\u00f3n recursos propios icde24",
        "programaci\u00f3n sgp educaci\u00f3n24",
        "programaci\u00f3n sgp salud24",
        "programaci\u00f3n sgp apsb24",
        "programaci\u00f3n cofinanciaci\u00f3n municipio24",
        "programaci\u00f3n cofinanciaci\u00f3n naci\u00f3n24",
        "programaci\u00f3n cr\u00e9dito24",
        "programaci\u00f3n regal\u00edas24",
        "programaci\u00f3n otras fuentes24",
    ],
    "25": [
        "programaci\u00f3n recursos propios icld25",
        "programaci\u00f3n recursos propios icde25",
        "programaci\u00f3n sgp educaci\u00f3n25",
        "programaci\u00f3n sgp salud25",
        "programaci\u00f3n sgp apsb25",
        "programaci\u00f3n cofinanciaci\u00f3n municipio25",
        "programaci\u00f3n cofinanciaci\u00f3n naci\u00f3n25",
        "programaci\u00f3n cr\u00e9dito25",
        "programaci\u00f3n regal\u00edas25",
        "programaci\u00f3n otras fuentes25",
    ],
    "26": [
        "programaci\u00f3n recursos propios icld26",
        "programaci\u00f3n recursos propios icde26",
        "programaci\u00f3n sgp educaci\u00f3n26",
        "programaci\u00f3n sgp salud26",
        "programaci\u00f3n sgp apsb26",
        "programaci\u00f3n cofinanciaci\u00f3n municipio26",
        "programaci\u00f3n cofinanciaci\u00f3n naci\u00f3n26",
        "programaci\u00f3n cr\u00e9dito26",
        "programaci\u00f3n regal\u00edas26",
        "programaci\u00f3n otras fuentes26",
    ],
    "27": [
        "programaci\u00f3n recursos propios icld27",
        "programaci\u00f3n recursos propios icde27",
        "programaci\u00f3n sgp educaci\u00f3n27",
        "programaci\u00f3n sgp salud27",
        "programaci\u00f3n sgp apsb27",
        "programaci\u00f3n cofinanciaci\u00f3n municipio27",
        "programaci\u00f3n cofinanciaci\u00f3n naci\u00f3n27",
        "programaci\u00f3n cr\u00e9dito27",
        "programaci\u00f3n regal\u00edas27",
        "programaci\u00f3n otras fuentes27",
    ],
}

# Columna de clasificacion de recursos en hacienda y regalias (con tilde)
COL_CLASIF_RECURSOS = "CLASIFICACI\u00d3N RECURSOS"  # CLASIFICACIÓN RECURSOS

# Nombres de columnas calculadas (con tildes, igual que en el notebook)
def col_prog_fin(year: str) -> str:
    return f"Programaci\u00f3n Financiera {year}"      # Programación Financiera 2024

def col_ejec_fin(year: str) -> str:
    return f"Ejecuci\u00f3n Financiera {year}"         # Ejecución Financiera 2024

def col_meta_esp(year: str) -> str:
    return f"Meta F\u00edsica Esperada {year}"         # Meta Física Esperada 2024

def col_pct_fis(year: str) -> str:
    return f"PORCENTAJE DE EJECUCI\u00d3N {year}"      # PORCENTAJE DE EJECUCIÓN 2024

def col_cat_fis(year: str) -> str:
    return f"CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA {year}"

COL_LINEA     = "L\u00ednea Estrat\u00e9gica"          # Línea Estratégica
COL_PCT_ACUM  = "PORCENTAJE DE EJECUCI\u00d3N ACUMULADA"

# -------------------------------------------------
# CONFIGURACION DE PAGINA
# -------------------------------------------------
st.set_page_config(
    page_title="Dashboard PDD - Reporte de Avance",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# CSS PERSONALIZADO
# -------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: {COLORS['gris_texto']};
}}

.main-header {{
    background: linear-gradient(135deg, {COLORS['azul_oscuro']} 0%, {COLORS['azul_medio']} 60%, {COLORS['cyan']} 100%);
    padding: 2.5rem 3rem 2rem;
    border-radius: 0 0 2rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    color: white;
}}
.main-header h1 {{
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 2.1rem;
    margin: 0;
    letter-spacing: -0.5px;
}}
.main-header p {{
    margin: 0.4rem 0 0;
    font-size: 0.95rem;
    opacity: 0.82;
}}

.kpi-card {{
    background: white;
    border-radius: 1rem;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 5px solid {COLORS['azul_medio']};
    margin-bottom: 1rem;
}}
.kpi-card.verde   {{ border-left-color: {COLORS['verde_oscuro']}; }}
.kpi-card.cyan    {{ border-left-color: {COLORS['cyan']}; }}
.kpi-card.naranja {{ border-left-color: {COLORS['naranja_claro']}; }}
.kpi-card.cafe    {{ border-left-color: {COLORS['cafe']}; }}
.kpi-value {{
    font-family: 'Sora', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
}}
.kpi-label {{
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6b7280;
    margin-top: 0.3rem;
}}
.kpi-tooltip {{
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 0.5rem;
    border-top: 1px solid #f3f4f6;
    padding-top: 0.5rem;
}}

.section-title {{
    font-family: 'Sora', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: {COLORS['azul_oscuro']};
    border-bottom: 2px solid {COLORS['cyan']};
    padding-bottom: 0.4rem;
    margin: 2rem 0 1rem;
}}

section[data-testid="stSidebar"] {{
    background: {COLORS['azul_oscuro']};
}}
section[data-testid="stSidebar"] * {{
    color: white !important;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stRadio label {{
    color: #cbd5e1 !important;
    font-size: 0.85rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {COLORS['cyan']} !important;
    font-family: 'Sora', sans-serif;
}}

.error-box {{
    background: #fff7f0;
    border: 1.5px solid {COLORS['salmon']};
    border-radius: 0.8rem;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}}
.error-box h4 {{
    color: #c0392b;
    margin: 0 0 0.5rem;
    font-family: 'Sora', sans-serif;
}}
.schema-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    margin-top: 0.8rem;
}}
.schema-table th {{
    background: {COLORS['azul_oscuro']};
    color: white;
    padding: 0.5rem 0.8rem;
    text-align: left;
}}
.schema-table td {{
    padding: 0.4rem 0.8rem;
    border-bottom: 1px solid #e5e7eb;
}}
.schema-table tr:nth-child(even) td {{
    background: #f9fafb;
}}

.upload-zone {{
    background: #f8fafc;
    border: 2px dashed {COLORS['cyan']};
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 0.5rem 0 1rem;
    text-align: center;
    color: #6b7280;
}}

hr.custom {{ border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }}

.footer {{
    text-align: center;
    font-size: 0.78rem;
    color: #9ca3af;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------
def fmt_pct(v: float) -> str:
    if v is None:
        return "N/A"
    return f"{v*100:.1f}%"


def color_pct(v: float) -> str:
    if v is None:
        return COLORS["cafe"]
    if v >= 0.9:
        return COLORS["verde_oscuro"]
    if v >= 0.6:
        return COLORS["cyan"]
    if v >= 0.3:
        return COLORS["naranja_claro"]
    return COLORS["salmon"]


def kpi_card(label: str, value: str, color_class: str = "", tooltip: str = ""):
    tip_html = f'<div class="kpi-tooltip">Como se calcula: {tooltip}</div>' if tooltip else ""
    st.markdown(f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {tip_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def show_schema_error(file_name: str, schema: list, table_name: str = ""):
    table_note = (
        f'<p style="margin:0 0 0.6rem;font-size:0.85rem">'
        f'<strong>Nombre de tabla esperado dentro del Excel:</strong> <code>{table_name}</code></p>'
        if table_name else ""
    )
    rows = "".join(
        f"<tr><td><code>{r['col']}</code></td><td>{r['tipo']}</td><td>{r['ejemplo']}</td></tr>"
        for r in schema
    )
    st.markdown(f"""
    <div class="error-box">
        <h4>Error al leer {file_name}</h4>
        <p>No se pudo procesar el archivo. Verifica que contenga exactamente las siguientes columnas:</p>
        {table_note}
        <table class="schema-table">
            <thead><tr><th>Columna en el archivo Excel</th><th>Tipo</th><th>Ejemplo de dato real</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:0.8rem;font-size:0.82rem;color:#6b7280;">
            <strong>Tip:</strong> El archivo debe tener una tabla de Excel (Insert &gt; Table) con el nombre
            indicado arriba. Las columnas deben coincidir exactamente, incluyendo tildes, mayusculas y espacios.
        </p>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------
# ESQUEMAS CON DATOS REALES DEL ARCHIVO
# Los ejemplos reflejan el tipo de informacion real que contiene cada columna
# -------------------------------------------------
SCHEMAS = {
    "Plan Indicativo": {
        "table": "tblPlanIndicativo_2",
        "cols": [
            {"col": "Codigo Meta",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001"},
            {"col": "L\u00ednea Estrat\u00e9gica",
             "tipo": "Texto",
             "ejemplo": "Linea 1 - Bienestar y Equidad Social"},
            {"col": "Sector PDD",
             "tipo": "Texto",
             "ejemplo": "Educacion"},
            {"col": "Programa PDD",
             "tipo": "Texto",
             "ejemplo": "1.1 Educacion con calidad e incluyente"},
            {"col": "Meta de cuatrenio",
             "tipo": "Numero",
             "ejemplo": "10000"},
            {"col": "Tipo de Acumulaci\u00f3n",
             "tipo": "Texto",
             "ejemplo": "Acumulado  |  Ultimo Dato"},
            {"col": "Responsable",
             "tipo": "Texto",
             "ejemplo": "SECRETARIA DE EDUCACION"},
            {"col": "Meta F\u00edsica Esperada 2024",
             "tipo": "Numero",
             "ejemplo": "2500  (porcion de la meta del cuatrienio esperada en 2024)"},
            {"col": "EJECUCI\u00d3N 2024",
             "tipo": "Numero",
             "ejemplo": "2300  (valor ejecutado en la unidad de medida del indicador)"},
            {"col": "PORCENTAJE DE EJECUCI\u00d3N 2024",
             "tipo": "Decimal",
             "ejemplo": "0.92  (equivale al 92% - siempre entre 0 y 1 o mayor)"},
            {"col": "CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA 2024",
             "tipo": "Texto",
             "ejemplo": "Superior  |  Alto  |  Medio  |  Bajo  |  Critico"},
            {"col": "PORCENTAJE DE EJECUCI\u00d3N ACUMULADA",
             "tipo": "Decimal",
             "ejemplo": "0.46  (avance acumulado frente a la meta del cuatrienio)"},
            {"col": "Programaci\u00f3n recursos propios icld24",
             "tipo": "Numero",
             "ejemplo": "500000000  (pesos colombianos)"},
            {"col": "Programaci\u00f3n regal\u00edas24",
             "tipo": "Numero",
             "ejemplo": "200000000"},
            {"col": "Programaci\u00f3n sgp educaci\u00f3n24",
             "tipo": "Numero",
             "ejemplo": "1500000000"},
        ],
    },
    "Hacienda 2024": {
        "table": "EjecucionHaciendaDiciembre",
        "cols": [
            {"col": "RP",
             "tipo": "Numero",
             "ejemplo": "150000000  (registro presupuestal en pesos)"},
            {"col": "CODIGO META",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001"},
            {"col": "CLASIFICACI\u00d3N RECURSOS",
             "tipo": "Texto",
             "ejemplo": "ICLD  |  SGP EDUCACION  |  REGALIAS  |  CREDITO"},
        ],
    },
    "Hacienda 2025": {
        "table": "EjecucionHaciendaDiciembre2025",
        "cols": [
            {"col": "RP",
             "tipo": "Numero",
             "ejemplo": "180000000"},
            {"col": "CODIGO META",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001"},
            {"col": "CLASIFICACI\u00d3N RECURSOS",
             "tipo": "Texto",
             "ejemplo": "ICLD  |  SGP EDUCACION"},
            {"col": "PROYECTO ARCHIVADO",
             "tipo": "Texto",
             "ejemplo": "(celda vacia = activo)  |  SI = no se incluye"},
            {"col": "SE VA A CARGAR EN PI",
             "tipo": "Texto",
             "ejemplo": "(celda vacia = se carga)  |  SI = se omite"},
            {"col": "DISTRIBUIR DE FORMA EQUITATIVA",
             "tipo": "Texto",
             "ejemplo": "SI = se divide el RP entre 2  |  NO o vacio = se usa el valor completo"},
        ],
    },
    "Hacienda 2026": {
        "table": "EjecucionHacienda2026",
        "cols": [
            {"col": "RP",
             "tipo": "Numero",
             "ejemplo": "120000000"},
            {"col": "CODIGO META",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001"},
            {"col": "CLASIFICACI\u00d3N RECURSOS",
             "tipo": "Texto",
             "ejemplo": "ICLD  |  SGP EDUCACION"},
            {"col": "PROYECTO ARCHIVADO",
             "tipo": "Texto",
             "ejemplo": "(celda vacia = activo)"},
            {"col": "SE VA A CARGAR EN PI",
             "tipo": "Texto",
             "ejemplo": "(celda vacia = aplica)"},
            {"col": "DISTRIBUIR DE FORMA EQUITATIVA",
             "tipo": "Texto",
             "ejemplo": "SI  |  NO"},
        ],
    },
    "Regalias 2024": {
        "table": "EjecucionRegalias",
        "cols": [
            {"col": "COMPROMISOS",
             "tipo": "Numero",
             "ejemplo": "80000000  (compromisos de regalias en pesos)"},
            {"col": "CODIGO META",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001  (debe iniciar con las letras MT)"},
            {"col": "CLASIFICACI\u00d3N RECURSOS",
             "tipo": "Texto",
             "ejemplo": "REGALIAS"},
        ],
    },
    "Regalias 2025": {
        "table": "Pagos_Regalias_2025",
        "cols": [
            {"col": "PAGOS REGALIAS",
             "tipo": "Numero",
             "ejemplo": "95000000  (pagos efectivos de regalias en pesos)"},
            {"col": "CODIGO META",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001"},
            {"col": "CLASIFICACI\u00d3N RECURSOS",
             "tipo": "Texto",
             "ejemplo": "REGALIAS"},
        ],
    },
    "Regalias 2026": {
        "table": "Pagos_Regalias_2026",
        "cols": [
            {"col": "PAGO EJECUTADO VALOR",
             "tipo": "Numero",
             "ejemplo": "75000000"},
            {"col": "CODIGO META",
             "tipo": "Texto",
             "ejemplo": "MT-ED-0001"},
            {"col": "CLASIFICACI\u00d3N RECURSOS",
             "tipo": "Texto",
             "ejemplo": "REGALIAS"},
            {"col": "ULTIMA FECHA PAGO",
             "tipo": "Fecha",
             "ejemplo": "2026-03-04  (solo se incluyen pagos con fecha en 2026)"},
        ],
    },
}

# -------------------------------------------------
# LECTURA ROBUSTA DE ARCHIVOS
# -------------------------------------------------
def to_bytesio(source) -> io.BytesIO:
    """Convierte cualquier fuente (bytes, bytearray, BytesIO, file-uploader) a BytesIO."""
    if isinstance(source, (bytes, bytearray)):
        return io.BytesIO(source)
    if isinstance(source, io.BytesIO):
        source.seek(0)
        return source
    # Objeto tipo file (e.g. UploadedFile de Streamlit) - ya fue .read() antes de llegar aqui
    return io.BytesIO(source)


def read_excel_safe(source, table_name: str, columns: list = None):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(source)
            tmp_path = tmp.name

        kwargs = {"table_name": table_name}
        if columns:
            kwargs["columns"] = columns

        return pl.read_excel(tmp_path, **kwargs)

    except Exception:
        return None


def fetch_github_file(url: str) -> Optional[bytes]:
    """Descarga bytes desde una URL raw de GitHub."""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


# -------------------------------------------------
# PROCESAMIENTO DE DATOS
# -------------------------------------------------
def build_prog_fin_expr(df_lower: pl.DataFrame, suffix: str) -> pl.Expr:
    """Suma las columnas de programacion financiera de una vigencia dada."""
    cols_wanted = PROG_FIN_COLS[suffix]
    existing = [c for c in cols_wanted if c in df_lower.columns]
    if not existing:
        return pl.lit(0.0)
    expr = pl.col(existing[0]).cast(pl.Float64)
    for c in existing[1:]:
        expr = expr + pl.col(c).cast(pl.Float64)
    return expr


def process_regalias(source_bytes: bytes, year: str) -> Optional[pl.DataFrame]:
    table_map = {
        "2024": "EjecucionRegalias",
        "2025": "Pagos_Regalias_2025",
        "2026": "Pagos_Regalias_2026",
    }
    df = read_excel_safe(source_bytes, table_map[year])
    if df is None:
        return None
    try:
        # Normalizar nombres: strip, upper, quitar artefactos de encoding
        df = df.select(pl.all().name.map(lambda x: x.strip().upper().replace("_X0009_", "")))

        if year == "2024":
            df = (df
                  .select(["CODIGO META", "COMPROMISOS", COL_CLASIF_RECURSOS.upper()])
                  .with_columns(pl.col("CODIGO META").fill_null(""))
                  .filter(pl.col("CODIGO META") != "", pl.col("CODIGO META").str.starts_with("MT"))
                  .rename({"COMPROMISOS": "RP"}))

        elif year == "2025":
            df = (df
                  .select(["PAGOS REGALIAS", "CODIGO META", COL_CLASIF_RECURSOS.upper()])
                  .rename({"PAGOS REGALIAS": "RP"})
                  .with_columns(pl.col("CODIGO META").fill_null(""))
                  .filter(pl.col("CODIGO META") != ""))

        elif year == "2026":
            df = (df
                  .filter(
                      (pl.col("ULTIMA FECHA PAGO") >= pl.date(2026, 1, 1)) &
                      (pl.col("ULTIMA FECHA PAGO") <= pl.date(2026, 12, 31))
                  )
                  .select(["PAGO EJECUTADO VALOR", "CODIGO META", COL_CLASIF_RECURSOS.upper()])
                  .rename({"PAGO EJECUTADO VALOR": "RP"})
                  .with_columns(pl.col("CODIGO META").fill_null(""))
                  .filter(pl.col("CODIGO META") != ""))

        return df.select(["CODIGO META", "RP"])
    except Exception:
        return None


def process_hacienda(source_bytes: bytes, year: str) -> Optional[pl.DataFrame]:
    table_map = {
        "2024": "EjecucionHaciendaDiciembre",
        "2025": "EjecucionHaciendaDiciembre2025",
        "2026": "EjecucionHacienda2026",
    }
    df = read_excel_safe(source_bytes, table_map[year])
    if df is None:
        return None
    try:
        if year == "2024":
            df = (df
                  .select(["RP", "CODIGO META", COL_CLASIF_RECURSOS])
                  .with_columns(pl.col("CODIGO META", COL_CLASIF_RECURSOS).fill_null(""))
                  .filter(pl.col("CODIGO META") != "", pl.col(COL_CLASIF_RECURSOS) != ""))
        else:
            df = (df
                  .with_columns(
                      pl.col("PROYECTO ARCHIVADO", "CODIGO META",
                             COL_CLASIF_RECURSOS, "SE VA A CARGAR EN PI").fill_null(""),
                      pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA") == "SI")
                        .then(pl.col("RP") / 2)
                        .otherwise(pl.col("RP"))
                  )
                  .filter(
                      pl.col("PROYECTO ARCHIVADO") == "",
                      pl.col("CODIGO META") != "",
                      pl.col(COL_CLASIF_RECURSOS) != "",
                      pl.col("SE VA A CARGAR EN PI") == "",
                  ))
        return df.select(["CODIGO META", "RP"])
    except Exception:
        return None


def merge_ejecucion(reg: Optional[pl.DataFrame],
                    hac: Optional[pl.DataFrame],
                    col_name: str) -> pl.DataFrame:
    frames = [f for f in [reg, hac] if f is not None and not f.is_empty()]
    if not frames:
        return pl.DataFrame({
            "CODIGO META": pl.Series([], dtype=pl.Utf8),
            col_name: pl.Series([], dtype=pl.Float64),
        })
    return (
        pl.concat(frames, how="diagonal")
        .group_by("CODIGO META")
        .agg(pl.col("RP").sum().alias(col_name))
    )


@st.cache_data(show_spinner=False)
def load_and_process(
    pi_bytes: bytes,
    h24_bytes, r24_bytes,
    h25_bytes, r25_bytes,
    h26_bytes, r26_bytes,
):
    errors = []

    # ── Plan Indicativo ─────────────────────────────────────
    pi = read_excel_safe(pi_bytes, "tblPlanIndicativo_2")

    pi = pi.select(
        pl.all().name.map(
            lambda x: x.strip().replace("\n"," ").replace("  "," ")
        )
    )
    if pi is None:
        errors.append("Plan Indicativo")
        return None, errors

    orden_lineas    = read_excel_safe(pi_bytes, "orden_lineas")
    orden_sectores  = read_excel_safe(pi_bytes, "orden_sectores")
    orden_programas = read_excel_safe(pi_bytes, "orden_programas")
    homologacion    = read_excel_safe(pi_bytes, "HomologacionSecretarias")

    # Seleccionar columnas fisicas con nombres reales (tildes incluidas)
    available = [c for c in COLS_PI_REAL if c in pi.columns]
    columnas_fisicas = pi.select(available)

    # ── Programacion financiera ──────────────────────────────
    # El notebook normaliza los nombres a lowercase para usar los de PROG_FIN_COLS
    pi_lower = pi.select(pl.all().name.map(lambda x: x.strip().lower()))

    suffix_map = [("24", "2024"), ("25", "2025"), ("26", "2026"), ("27", "2027")]
    select_exprs = [pl.col("codigo meta")]
    for suf, yr in suffix_map:
        expr = build_prog_fin_expr(pi_lower, suf)
        select_exprs.append(expr.alias(col_prog_fin(yr)))

    prog_financ = pi_lower.select(select_exprs)

    # ── Ejecuciones financieras por vigencia ─────────────────
    reg24 = process_regalias(r24_bytes, "2024") if r24_bytes else None
    hac24 = process_hacienda(h24_bytes, "2024") if h24_bytes else None
    reg25 = process_regalias(r25_bytes, "2025") if r25_bytes else None
    hac25 = process_hacienda(h25_bytes, "2025") if h25_bytes else None
    reg26 = process_regalias(r26_bytes, "2026") if r26_bytes else None
    hac26 = process_hacienda(h26_bytes, "2026") if h26_bytes else None

    ef24 = merge_ejecucion(reg24, hac24, col_ejec_fin("2024"))
    ef25 = merge_ejecucion(reg25, hac25, col_ejec_fin("2025"))
    ef26 = merge_ejecucion(reg26, hac26, col_ejec_fin("2026"))

    prog_financ = (prog_financ
        .join(ef24, left_on="codigo meta", right_on="CODIGO META", how="left")
        .join(ef25, left_on="codigo meta", right_on="CODIGO META", how="left")
        .join(ef26, left_on="codigo meta", right_on="CODIGO META", how="left")
        .with_columns(
            pl.col(col_ejec_fin("2024"),
                   col_ejec_fin("2025"),
                   col_ejec_fin("2026")).fill_null(0)
        )
    )

    # ── DataFrame principal ──────────────────────────────────
    pff = columnas_fisicas.join(
        prog_financ,
        left_on="Codigo Meta",
        right_on="codigo meta",
        how="left",
    )

    meta_cols = [col_meta_esp(y) for y in ["2024","2025","2026","2027"] if col_meta_esp(y) in pff.columns]
    if meta_cols:
        pff = pff.with_columns([pl.col(c).fill_null(0) for c in meta_cols])

    return {
        "pff": pff,
        "orden_lineas": orden_lineas,
        "orden_sectores": orden_sectores,
        "orden_programas": orden_programas,
        "homologacion": homologacion,
    }, errors


# -------------------------------------------------
# GRAFICOS
# -------------------------------------------------
def gauge_chart(value: float, title: str, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        number={"suffix": "%", "font": {"size": 32, "color": color, "family": "Sora"}},
        title={"text": title, "font": {"size": 13, "color": "#6b7280"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 10}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#f3f4f6",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  30],  "color": "#fee2e2"},
                {"range": [30, 60],  "color": "#fef3c7"},
                {"range": [60, 90],  "color": "#d1fae5"},
                {"range": [90, 100], "color": "#a7f3d0"},
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(t=40, b=10, l=20, r=20), paper_bgcolor="white")
    return fig


def bar_h(df: pd.DataFrame, x_col: str, y_col: str, pct_col: str,
          title: str, prog_col: str = None, ejec_col: str = None):
    colors = [color_pct(v) for v in df[pct_col].tolist()]
    if prog_col and ejec_col and prog_col in df.columns and ejec_col in df.columns:
        customdata = df[[prog_col, ejec_col]].values
        hover = (
            "<b>%{y}</b><br>"
            "Programacion: $%{customdata[0]:,.0f}<br>"
            "Ejecucion: $%{customdata[1]:,.0f}<br>"
            "Avance: %{text}<extra></extra>"
        )
    else:
        customdata = None
        hover = "<b>%{y}</b><br>Avance: %{text}<extra></extra>"

    fig = go.Figure(go.Bar(
        x=df[x_col],
        y=df[y_col],
        orientation="h",
        marker_color=colors,
        text=[f"{v*100:.1f}%" for v in df[pct_col]],
        textposition="outside",
        hovertemplate=hover,
        customdata=customdata,
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Ejecucion ($)" if ejec_col else "% Ejecucion",
        height=max(300, len(df) * 44),
        margin=dict(l=20, r=90, t=50, b=20),
        paper_bgcolor="white",
        plot_bgcolor="#fafafa",
        font={"family": "DM Sans"},
    )
    return fig


def pie_chart(labels, values, title, colors_list):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker_colors=colors_list,
        hole=0.45,
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        title=title, height=370,
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor="white",
        font={"family": "DM Sans"},
    )
    return fig


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Dashboard PDD")
    st.markdown("#### Reporte de Avance 2024-2027")
    st.markdown("---")

    st.markdown("### Fuente de datos")
    modo_carga = st.radio(
        "Como cargar los archivos:",
        ["GitHub (datos en vivo)", "Subir archivos manualmente"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### Filtros")
    filtro_vigencia = st.selectbox("Vigencia:", VIGENCIAS, index=2)

    ph_linea  = st.empty()
    ph_sector = st.empty()
    ph_resp   = st.empty()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#94a3b8; line-height:1.6'>
    Los archivos 2024 y 2025 son vigencias cerradas y no se modifican.<br>
    El archivo 2026 se actualiza periodicamente.
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# ENCABEZADO
# -------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <h1>Reporte de Avance del Plan de Desarrollo</h1>
    <p>Ejecucion Fisica y Financiera &middot; Vigencia <strong>{filtro_vigencia}</strong> &middot; Cuatrienio 2024&ndash;2027</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CARGA DE ARCHIVOS
# -------------------------------------------------
pi_bytes = h24_bytes = r24_bytes = h25_bytes = r25_bytes = h26_bytes = r26_bytes = None

if modo_carga == "GitHub (datos en vivo)":
    with st.expander("Configurar URLs de GitHub", expanded=False):
        st.info("Pega las URLs crudas (raw) de los archivos en tu repositorio de GitHub.")
        c1, c2 = st.columns(2)
        with c1:
            url_pi  = st.text_input("Plan Indicativo (.xlsx)",  key="url_pi",  placeholder="https://raw.githubusercontent.com/...")
            url_h24 = st.text_input("Hacienda 2024 (.xlsx)",    key="url_h24", placeholder="https://raw.githubusercontent.com/...")
            url_r24 = st.text_input("Regalias 2024 (.xlsx)",    key="url_r24", placeholder="https://raw.githubusercontent.com/...")
            url_h25 = st.text_input("Hacienda 2025 (.xlsx)",    key="url_h25", placeholder="https://raw.githubusercontent.com/...")
        with c2:
            url_r25 = st.text_input("Regalias 2025 (.xlsx)",    key="url_r25", placeholder="https://raw.githubusercontent.com/...")
            url_h26 = st.text_input("Hacienda 2026 (.xlsx)",    key="url_h26", placeholder="https://raw.githubusercontent.com/...")
            url_r26 = st.text_input("Regalias 2026 (.xlsx)",    key="url_r26", placeholder="https://raw.githubusercontent.com/...")

    if st.session_state.get("url_pi"):
        with st.spinner("Descargando archivos desde GitHub..."):
            pi_bytes  = fetch_github_file(st.session_state["url_pi"])
            h24_bytes = fetch_github_file(st.session_state["url_h24"]) if st.session_state.get("url_h24") else None
            r24_bytes = fetch_github_file(st.session_state["url_r24"]) if st.session_state.get("url_r24") else None
            h25_bytes = fetch_github_file(st.session_state["url_h25"]) if st.session_state.get("url_h25") else None
            r25_bytes = fetch_github_file(st.session_state["url_r25"]) if st.session_state.get("url_r25") else None
            h26_bytes = fetch_github_file(st.session_state["url_h26"]) if st.session_state.get("url_h26") else None
            r26_bytes = fetch_github_file(st.session_state["url_r26"]) if st.session_state.get("url_r26") else None

        if pi_bytes is None:
            st.error("No se pudo descargar el Plan Indicativo. Verifica la URL.")
    else:
        st.markdown("""
        <div class="upload-zone">
            Ingresa las URLs de los archivos en GitHub para comenzar.<br>
            <small>Usa el panel <strong>Configurar URLs</strong> de arriba.</small>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("### Carga de Archivos")
    with st.expander("Archivos de vigencias cerradas (2024-2025)", expanded=True):
        st.caption("Estos archivos corresponden a vigencias ya cerradas y no se modifican.")
        c1, c2 = st.columns(2)
        with c1:
            pi_file  = st.file_uploader("Plan Indicativo 2024-2027", type=["xlsx"], key="pi")
            h24_file = st.file_uploader("Ejecucion Hacienda 2024",   type=["xlsx"], key="h24")
            r24_file = st.file_uploader("Regalias 2024",              type=["xlsx"], key="r24")
        with c2:
            h25_file = st.file_uploader("Ejecucion Hacienda 2025",   type=["xlsx"], key="h25")
            r25_file = st.file_uploader("Regalias 2025",              type=["xlsx"], key="r25")

    with st.expander("Archivo de vigencia actual (2026)", expanded=True):
        st.caption("Estos archivos se actualizan periodicamente.")
        c1, c2 = st.columns(2)
        with c1:
            h26_file = st.file_uploader("Ejecucion Hacienda 2026",   type=["xlsx"], key="h26")
        with c2:
            r26_file = st.file_uploader("Regalias 2026",              type=["xlsx"], key="r26")

    pi_bytes  = pi_file.read()  if pi_file  else None
    h24_bytes = h24_file.read() if h24_file else None
    r24_bytes = r24_file.read() if r24_file else None
    h25_bytes = h25_file.read() if h25_file else None
    r25_bytes = r25_file.read() if r25_file else None
    h26_bytes = h26_file.read() if h26_file else None
    r26_bytes = r26_file.read() if r26_file else None

    if not pi_bytes:
        st.markdown("""
        <div class="upload-zone">
            Carga el <strong>Plan Indicativo</strong> para comenzar a visualizar el dashboard.<br>
            <small>Los demas archivos son opcionales. El dashboard mostrara los datos disponibles.</small>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------
# PROCESAMIENTO
# -------------------------------------------------
if not pi_bytes:
    st.stop()

with st.spinner("Procesando datos..."):
    result, load_errors = load_and_process(
        pi_bytes,
        h24_bytes, r24_bytes,
        h25_bytes, r25_bytes,
        h26_bytes, r26_bytes,
    )

if result is None:
    show_schema_error(
        "Plan Indicativo",
        SCHEMAS["Plan Indicativo"]["cols"],
        SCHEMAS["Plan Indicativo"]["table"],
    )
    st.stop()

pff            = result["pff"]
orden_lineas   = result["orden_lineas"]
orden_sectores = result["orden_sectores"]
homologacion   = result["homologacion"]

# Columnas activas segun vigencia seleccionada
C_META     = col_meta_esp(filtro_vigencia)
C_PCT_FIS  = col_pct_fis(filtro_vigencia)
C_CAT      = col_cat_fis(filtro_vigencia)
C_EJEC_FIN = col_ejec_fin(filtro_vigencia)
C_PROG_FIN = col_prog_fin(filtro_vigencia)

# Columna de linea (con tilde si existe, sin tilde como fallback)
c_linea = COL_LINEA if COL_LINEA in pff.columns else "Linea Estrategica"

# ── Filtros del sidebar con opciones reales ─────────────
lineas_opts = sorted(pff[c_linea].drop_nulls().unique().to_list()) if c_linea in pff.columns else []
sector_opts = sorted(pff["Sector PDD"].drop_nulls().unique().to_list()) if "Sector PDD" in pff.columns else []
resp_opts   = sorted(pff["Responsable"].drop_nulls().unique().to_list()) if "Responsable" in pff.columns else []

with ph_linea:
    filtro_linea = st.multiselect("Linea Estrategica:", lineas_opts, placeholder="Todas")
with ph_sector:
    filtro_sector = st.multiselect("Sector PDD:", sector_opts, placeholder="Todos")
with ph_resp:
    filtro_resp = st.multiselect("Dependencia:", resp_opts, placeholder="Todas")

pff_f = pff.clone()
if filtro_linea and c_linea in pff_f.columns:
    pff_f = pff_f.filter(pl.col(c_linea).is_in(filtro_linea))
if filtro_sector and "Sector PDD" in pff_f.columns:
    pff_f = pff_f.filter(pl.col("Sector PDD").is_in(filtro_sector))
if filtro_resp and "Responsable" in pff_f.columns:
    pff_f = pff_f.filter(pl.col("Responsable").is_in(filtro_resp))

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Resumen General",
    "Ejecucion Financiera",
    "Ejecucion Fisica",
    "Detalle por Dependencia",
])

# ==================================================
# TAB 1: RESUMEN GENERAL
# ==================================================
with tab1:
    section_title(f"Indicadores Clave - Vigencia {filtro_vigencia}")

    n_total       = len(pff_f)
    n_programadas = 0
    avance_vig    = 0.0
    avance_acum   = 0.0
    n_superiores  = 0
    ejec_fin_val  = 0.0
    prog_fin_val  = 0.0
    pct_fin       = 0.0

    if C_META in pff_f.columns:
        n_programadas = int(pff_f.filter(pl.col(C_META).fill_null(0) != 0).height)

    if C_PCT_FIS in pff_f.columns and C_META in pff_f.columns:
        avance_vig = float(
            pff_f.filter(pl.col(C_META).fill_null(0) != 0)
                 .select(pl.col(C_PCT_FIS).fill_null(0).mean()).item() or 0
        )

    if COL_PCT_ACUM in pff_f.columns:
        avance_acum = float(pff_f.select(pl.col(COL_PCT_ACUM).fill_null(0).mean()).item() or 0)

    if C_CAT in pff_f.columns and C_META in pff_f.columns:
        n_superiores = int(
            pff_f.filter(pl.col(C_META).fill_null(0) != 0)
                 .filter(pl.col(C_CAT) == "Superior").height
        )

    if C_EJEC_FIN in pff_f.columns:
        ejec_fin_val = float(pff_f.select(pl.col(C_EJEC_FIN).sum()).item() or 0)
    if C_PROG_FIN in pff_f.columns:
        prog_fin_val = float(pff_f.select(pl.col(C_PROG_FIN).sum()).item() or 0)
    if prog_fin_val > 0:
        pct_fin = ejec_fin_val / prog_fin_val

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        kpi_card("Metas Totales", str(n_total), "azul",
                 "Total de filas en el Plan Indicativo con los filtros aplicados.")
    with k2:
        kpi_card(f"Metas Programadas {filtro_vigencia}", str(n_programadas), "cyan",
                 f"Metas cuya columna 'Meta Fisica Esperada {filtro_vigencia}' es mayor a cero.")
    with k3:
        kpi_card(f"Avance Fisico {filtro_vigencia}", fmt_pct(avance_vig), "verde",
                 f"Promedio del campo 'PORCENTAJE DE EJECUCION {filtro_vigencia}' "
                 f"de las metas con Meta Fisica Esperada mayor a cero en {filtro_vigencia}.")
    with k4:
        kpi_card("Avance Acumulado Cuatrienio", fmt_pct(avance_acum), "naranja",
                 "Promedio del campo 'PORCENTAJE DE EJECUCION ACUMULADA' sobre el total de metas, "
                 "que mide el avance frente a la meta del cuatrienio completo 2024-2027.")
    with k5:
        kpi_card(f"Metas al 100% en {filtro_vigencia}", str(n_superiores), "cafe",
                 f"Numero de metas cuya 'CATEGORIA DE EJECUCION FISICA {filtro_vigencia}' "
                 "es igual a 'Superior', lo que indica una ejecucion igual o mayor al 100%.")

    st.markdown('<hr class="custom">', unsafe_allow_html=True)

    cg1, cg2, cg3 = st.columns(3)
    with cg1:
        st.plotly_chart(
            gauge_chart(avance_vig, f"Ejecucion Fisica {filtro_vigencia}", color_pct(avance_vig)),
            use_container_width=True, key="g1",
        )
    with cg2:
        st.plotly_chart(
            gauge_chart(avance_acum, "Ejecucion Acumulada Cuatrienio", color_pct(avance_acum)),
            use_container_width=True, key="g2",
        )
    with cg3:
        st.plotly_chart(
            gauge_chart(pct_fin, f"Ejecucion Financiera {filtro_vigencia}", color_pct(pct_fin)),
            use_container_width=True, key="g3",
        )
    st.caption(
        f"Ejecucion Fisica: promedio del avance de metas con programacion en {filtro_vigencia}. "
        "Ejecucion Financiera: suma de RP (Hacienda) y Pagos de Regalias sobre lo programado. "
        "Acumulada: avance frente a la meta total del cuatrienio 2024-2027."
    )

    if C_CAT in pff_f.columns and C_META in pff_f.columns:
        section_title(f"Distribucion por Categoria de Ejecucion - {filtro_vigencia}")
        cat_df = (
            pff_f
            .filter(pl.col(C_META).fill_null(0) != 0)
            .group_by(C_CAT)
            .agg(pl.col("Codigo Meta").len().alias("n"))
            .drop_nulls()
            .to_pandas()
        )
        if not cat_df.empty:
            cp1, cp2 = st.columns([1.3, 1])
            with cp1:
                cat_labels = cat_df[C_CAT].tolist()
                cat_vals   = cat_df["n"].tolist()
                cat_cols   = [CAT_COLORS.get(l, COLORS["gris_texto"]) for l in cat_labels]
                st.plotly_chart(
                    pie_chart(cat_labels, cat_vals, "Categorias de ejecucion", cat_cols),
                    use_container_width=True, key="pie_cat",
                )
            with cp2:
                st.markdown("**Que significa cada categoria?**")
                categorias_info = {
                    "Superior":      "Ejecucion igual o mayor al 100%",
                    "Alto":          "Ejecucion entre 80% y 99%",
                    "Medio":         "Ejecucion entre 60% y 79%",
                    "Bajo":          "Ejecucion entre 30% y 59%",
                    "Critico":       "Ejecucion menor al 30%",
                    "Sin Programar": "Sin meta fisica asignada en la vigencia",
                }
                for cat, rango in categorias_info.items():
                    color = CAT_COLORS.get(cat, COLORS["gris_texto"])
                    st.markdown(
                        f'<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
                        f'background:{color}22;color:{color};border:1px solid {color};'
                        f'font-size:0.8rem;font-weight:600">{cat}</span> &nbsp; {rango}',
                        unsafe_allow_html=True,
                    )
                    st.write("")

# ==================================================
# TAB 2: EJECUCION FINANCIERA
# ==================================================
with tab2:
    fin_ok = C_EJEC_FIN in pff_f.columns and C_PROG_FIN in pff_f.columns

    if not fin_ok:
        st.info(
            f"No hay datos de ejecucion financiera para {filtro_vigencia}. "
            "Verifica que los archivos de hacienda y regalias esten cargados."
        )
    else:
        section_title(f"Ejecucion Financiera por Linea Estrategica - {filtro_vigencia}")
        if c_linea in pff_f.columns and orden_lineas is not None:
            ord_col   = "Orden Linea"  if "Orden Linea"  in orden_lineas.columns else orden_lineas.columns[1]
            join_col  = c_linea        if c_linea         in orden_lineas.columns else orden_lineas.columns[0]
            lineas_fin = (
                pff_f
                .group_by(c_linea)
                .agg(pl.col(C_PROG_FIN).sum(), pl.col(C_EJEC_FIN).sum())
                .join(orden_lineas, left_on=c_linea, right_on=join_col, how="inner")
                .with_columns(
                    pl.when(pl.col(C_PROG_FIN) == 0)
                      .then(0.0)
                      .otherwise(pl.col(C_EJEC_FIN) / pl.col(C_PROG_FIN))
                      .alias("Pct")
                )
                .sort(ord_col)
                .to_pandas()
            )
            if not lineas_fin.empty:
                st.plotly_chart(
                    bar_h(lineas_fin, C_EJEC_FIN, c_linea, "Pct",
                          f"Ejecucion Financiera por Linea - {filtro_vigencia}",
                          prog_col=C_PROG_FIN, ejec_col=C_EJEC_FIN),
                    use_container_width=True, key="bar_lineas_fin",
                )
                st.caption(
                    "Como se calcula: suma de RP del informe de Hacienda mas Pagos de Regalias, "
                    "dividida entre la suma de todas las fuentes de Programacion Financiera de la vigencia."
                )

        section_title(f"Ejecucion Financiera por Sector PDD - {filtro_vigencia}")
        if "Sector PDD" in pff_f.columns and orden_sectores is not None:
            ord_col_s = "Orden Sector" if "Orden Sector" in orden_sectores.columns else orden_sectores.columns[1]
            sect_fin = (
                pff_f
                .group_by("Sector PDD")
                .agg(pl.col(C_PROG_FIN).sum(), pl.col(C_EJEC_FIN).sum())
                .join(orden_sectores, on="Sector PDD", how="inner")
                .with_columns(
                    pl.when(pl.col(C_PROG_FIN) == 0)
                      .then(0.0)
                      .otherwise(pl.col(C_EJEC_FIN) / pl.col(C_PROG_FIN))
                      .alias("Pct")
                )
                .sort(ord_col_s)
                .to_pandas()
            )
            if not sect_fin.empty:
                st.plotly_chart(
                    bar_h(sect_fin, C_EJEC_FIN, "Sector PDD", "Pct",
                          f"Ejecucion Financiera por Sector - {filtro_vigencia}",
                          prog_col=C_PROG_FIN, ejec_col=C_EJEC_FIN),
                    use_container_width=True, key="bar_sect_fin",
                )

        section_title("Ejecucion Financiera Acumulada 2024-2026")
        years_disp = [y for y in ["2024","2025","2026"] if col_ejec_fin(y) in pff_f.columns]
        if years_disp:
            ejec_vals = [float(pff_f.select(pl.col(col_ejec_fin(y)).sum()).item() or 0) for y in years_disp]
            prog_vals = [
                float(pff_f.select(pl.col(col_prog_fin(y)).sum()).item() or 0)
                if col_prog_fin(y) in pff_f.columns else 0
                for y in years_disp
            ]
            fig_acum = go.Figure()
            fig_acum.add_trace(go.Bar(name="Programacion", x=years_disp, y=prog_vals,
                                       marker_color=COLORS["cyan"], opacity=0.75))
            fig_acum.add_trace(go.Bar(name="Ejecucion",    x=years_disp, y=ejec_vals,
                                       marker_color=COLORS["azul_medio"]))
            fig_acum.update_layout(
                barmode="group",
                title="Programacion vs Ejecucion por Ano",
                yaxis_title="Valor ($)", height=380,
                paper_bgcolor="white", plot_bgcolor="#fafafa",
                font={"family": "DM Sans"},
                legend=dict(orientation="h", y=1.1),
            )
            st.plotly_chart(fig_acum, use_container_width=True, key="bar_acum")
            st.caption(
                "Programacion: suma de ICLD + ICDE + SGP Educacion + SGP Salud + SGP APSB + "
                "Cofinanciacion Municipio + Cofinanciacion Nacion + Credito + Regalias + Otras Fuentes. "
                "Ejecucion: RP de Hacienda mas Pagos de Regalias."
            )

# ==================================================
# TAB 3: EJECUCION FISICA
# ==================================================
with tab3:
    section_title(f"Ejecucion Fisica por Linea Estrategica - {filtro_vigencia}")

    if C_PCT_FIS in pff_f.columns and c_linea in pff_f.columns and C_META in pff_f.columns:
        lineas_fis = (
            pff_f
            .filter(pl.col(C_META).fill_null(0) != 0)
            .group_by(c_linea)
            .agg(
                pl.col(C_PCT_FIS).fill_null(0).mean().alias("Avance"),
                pl.col("Codigo Meta").len().alias("N Metas"),
            )
            .to_pandas()
            .sort_values("Avance", ascending=True)
        )
        if not lineas_fis.empty:
            colors_l = [color_pct(v) for v in lineas_fis["Avance"]]
            fig_fis = go.Figure(go.Bar(
                x=lineas_fis["Avance"] * 100,
                y=lineas_fis[c_linea],
                orientation="h",
                marker_color=colors_l,
                text=[f"{v*100:.1f}%" for v in lineas_fis["Avance"]],
                textposition="outside",
                customdata=lineas_fis[["N Metas"]].values,
                hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<br>Metas programadas: %{customdata[0]}<extra></extra>",
            ))
            fig_fis.update_layout(
                xaxis_title="% Promedio Ejecucion Fisica",
                height=max(300, len(lineas_fis) * 48),
                paper_bgcolor="white", plot_bgcolor="#fafafa",
                font={"family": "DM Sans"},
                margin=dict(l=20, r=90, t=30, b=20),
            )
            st.plotly_chart(fig_fis, use_container_width=True, key="bar_fis_lineas")
            st.caption(
                f"Como se calcula: promedio del campo 'PORCENTAJE DE EJECUCION {filtro_vigencia}' "
                f"de los indicadores cuya 'Meta Fisica Esperada {filtro_vigencia}' es mayor a cero."
            )
    else:
        st.info("No hay columnas de ejecucion fisica disponibles para esta vigencia.")

    section_title(f"Ejecucion Fisica por Sector PDD - {filtro_vigencia}")
    if C_PCT_FIS in pff_f.columns and "Sector PDD" in pff_f.columns and C_META in pff_f.columns:
        sect_fis = (
            pff_f
            .filter(pl.col(C_META).fill_null(0) != 0)
            .group_by("Sector PDD")
            .agg(
                pl.col(C_PCT_FIS).fill_null(0).mean().alias("Avance"),
                pl.col("Codigo Meta").len().alias("N Metas"),
            )
            .to_pandas()
            .sort_values("Avance", ascending=True)
        )
        if not sect_fis.empty:
            colors_s = [color_pct(v) for v in sect_fis["Avance"]]
            fig_sec = go.Figure(go.Bar(
                x=sect_fis["Avance"] * 100,
                y=sect_fis["Sector PDD"],
                orientation="h",
                marker_color=colors_s,
                text=[f"{v*100:.1f}%" for v in sect_fis["Avance"]],
                textposition="outside",
                customdata=sect_fis[["N Metas"]].values,
                hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<br>Metas: %{customdata[0]}<extra></extra>",
            ))
            fig_sec.update_layout(
                xaxis_title="% Promedio Ejecucion Fisica",
                height=max(300, len(sect_fis) * 48),
                paper_bgcolor="white", plot_bgcolor="#fafafa",
                font={"family": "DM Sans"},
                margin=dict(l=20, r=90, t=30, b=20),
            )
            st.plotly_chart(fig_sec, use_container_width=True, key="bar_fis_sect")

    section_title("Tabla de Metas PDD")
    disp_cols = [c for c in [
        "Codigo Meta", c_linea, "Sector PDD", "Programa PDD", "Responsable",
        C_META, C_PCT_FIS, C_CAT, COL_PCT_ACUM,
    ] if c in pff_f.columns]
    tabla = pff_f.select(disp_cols).to_pandas()
    for pct_c in [C_PCT_FIS, COL_PCT_ACUM]:
        if pct_c in tabla.columns:
            tabla[pct_c] = (tabla[pct_c].fillna(0) * 100).round(1).astype(str) + "%"
    st.dataframe(tabla, use_container_width=True, height=440)

# ==================================================
# TAB 4: DEPENDENCIAS
# ==================================================
with tab4:
    section_title(f"Avance por Dependencia Responsable - {filtro_vigencia}")

    if C_PCT_FIS not in pff_f.columns or C_META not in pff_f.columns:
        st.info("No hay datos suficientes para mostrar el avance por dependencia.")
    else:
        cat_expr = (
            pl.when(pl.col(C_CAT) == "Superior").then(1).otherwise(0).alias("Metas_100")
            if C_CAT in pff_f.columns else pl.lit(0).alias("Metas_100")
        )
        acum_expr = (
            pl.col(COL_PCT_ACUM).fill_null(0).mean().alias("Ejec_Acum")
            if COL_PCT_ACUM in pff_f.columns else pl.lit(0.0).alias("Ejec_Acum")
        )

        base_dep = (
            pff_f
            .filter(pl.col(C_META).fill_null(0) != 0)
            .with_columns(cat_expr, pl.lit(1).alias("Metas_Prog"))
            .group_by(pl.col("Responsable").str.strip_chars())
            .agg(
                pl.col(C_PCT_FIS).fill_null(0).mean().alias("Ejec_Vig"),
                pl.col("Metas_Prog").sum().alias("Metas Programadas"),
                pl.col("Metas_100").sum().alias("Metas al 100"),
                acum_expr,
            )
        )

        # Unir tabla de homologacion (Responsable en PI -> Dependencia Responsable)
        if homologacion is not None:
            resp_col_hom = next(
                (c for c in homologacion.columns if "Responsable" in c and "PI" in c), None
            )
            if resp_col_hom:
                base_dep = base_dep.join(
                    homologacion.rename({resp_col_hom: "Responsable"}),
                    on="Responsable",
                    how="left",
                )

        dep_pd = base_dep.to_pandas()

        if dep_pd.empty:
            st.info("No se encontraron datos de dependencias con los filtros actuales.")
        else:
            dep_pd["Ejec_Vig"]  = (dep_pd["Ejec_Vig"]  * 100).round(1)
            dep_pd["Ejec_Acum"] = (dep_pd["Ejec_Acum"] * 100).round(1)

            name_col   = "Dependencia Responsable" if "Dependencia Responsable" in dep_pd.columns else "Responsable"
            dep_sorted = dep_pd.sort_values("Ejec_Vig", ascending=True)
            colors_dep = [color_pct(v / 100) for v in dep_sorted["Ejec_Vig"]]

            fig_dep = go.Figure(go.Bar(
                x=dep_sorted["Ejec_Vig"],
                y=dep_sorted[name_col],
                orientation="h",
                marker_color=colors_dep,
                text=[f"{v:.1f}%" for v in dep_sorted["Ejec_Vig"]],
                textposition="outside",
                customdata=dep_sorted[["Metas Programadas", "Metas al 100", "Ejec_Acum"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"Avance {filtro_vigencia}: %{{x:.1f}}%<br>"
                    "Metas programadas: %{customdata[0]}<br>"
                    "Metas al 100%: %{customdata[1]}<br>"
                    "Avance acumulado: %{customdata[2]:.1f}%<extra></extra>"
                ),
            ))
            fig_dep.update_layout(
                xaxis_title=f"% Promedio Ejecucion {filtro_vigencia}",
                height=max(350, len(dep_sorted) * 48),
                paper_bgcolor="white", plot_bgcolor="#fafafa",
                font={"family": "DM Sans"},
                margin=dict(l=20, r=100, t=30, b=20),
            )
            st.plotly_chart(fig_dep, use_container_width=True, key="bar_dep")
            st.caption(
                f"Como se calcula: promedio del 'PORCENTAJE DE EJECUCION {filtro_vigencia}' "
                "de las metas programadas a cargo de cada dependencia. "
                "Metas al 100%: indicadores con 'CATEGORIA DE EJECUCION FISICA' igual a 'Superior'. "
                "Avance acumulado: promedio del 'PORCENTAJE DE EJECUCION ACUMULADA' (2024-2027)."
            )

            st.markdown('<hr class="custom">', unsafe_allow_html=True)
            st.dataframe(dep_pd, use_container_width=True, height=380)

# -------------------------------------------------
# ERRORES DE ARCHIVOS OPCIONALES
# -------------------------------------------------
missing_files = []
if h26_bytes is None:
    missing_files.append(("Hacienda 2026", "Hacienda 2026"))
if r26_bytes is None:
    missing_files.append(("Regalias 2026", "Regalias 2026"))

if missing_files:
    with st.expander("Archivos faltantes para la vigencia 2026", expanded=False):
        for label, key in missing_files:
            show_schema_error(
                label,
                SCHEMAS[key]["cols"],
                SCHEMAS[key]["table"],
            )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("""
<div class="footer">
    Dashboard de Avance PDD &middot; Desarrollado con Streamlit y Plotly &middot; Datos procesados con Polars
</div>
""", unsafe_allow_html=True)
