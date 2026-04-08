"""
Dashboard de Reporte de Avance PDD - Plan Indicativo 2024-2027
"""

import streamlit as st
import polars as pl
import pandas as pd
import plotly.graph_objects as go
import io
import requests
from typing import Optional

# ------------------------------------------------------------------
# PALETA CORPORATIVA
# ------------------------------------------------------------------
C = {
    "verde":    "#17743d",
    "cyan":     "#47b1d5",
    "azul":     "#1754ab",
    "azul_osc": "#003d6c",
    "naranja":  "#d88c16",
    "cafe":     "#9b5b1e",
    "salmon":   "#e68878",
    "gris":     "#2d3142",
}

# Semaforización oficial de la institución
# 0-29% Mínimo | 30-59% Medio | 60-99% Alto | >=100% Superior
def semaforo_color(v: float) -> str:
    if v is None: return C["cafe"]
    if v >= 1.0:  return C["verde"]
    if v >= 0.6:  return C["cyan"]
    if v >= 0.3:  return C["naranja"]
    return C["salmon"]

def semaforo_label(v: float) -> str:
    if v is None: return "Sin dato"
    if v >= 1.0:  return "Superior"
    if v >= 0.6:  return "Alto"
    if v >= 0.3:  return "Medio"
    return "Minimo"

SEM_COLORS = {
    "Superior": C["verde"],
    "Alto":     C["cyan"],
    "Medio":    C["naranja"],
    "Minimo":   C["salmon"],
}

VIGENCIAS = ["2024", "2025", "2026"]

# ------------------------------------------------------------------
# URLs FIJAS GitHub (vigencias cerradas 2024-2025)
# ------------------------------------------------------------------
GITHUB_H24 = "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20A%20DICIEMBRE%2031%20DEL%202024%20ENERO%2010%202025.xlsx"
GITHUB_R24 = "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/INFORME%20FINANCIERO%20REGALIAS%20A%2031%20DE%20DICIEMBRE%20DE%202024.xlsx"
GITHUB_H25 = "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20ENERO%20A%20DICIEMBRE%202025.xlsx"
GITHUB_R25 = "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/PAGOS%20REGALIAS%20ENERO%20-%20DICIEMBRE%202025.xlsx"

# ------------------------------------------------------------------
# NOMBRES DE COLUMNA EXACTOS (del notebook, con tildes reales)
# ------------------------------------------------------------------
COL_LINEA    = "L\u00ednea Estrat\u00e9gica"           # Línea Estratégica
COL_PCT_ACUM = "PORCENTAJE DE EJECUCI\u00d3N ACUMULADA"
COL_CLASIF   = "CLASIFICACI\u00d3N RECURSOS"

def col_meta(y):  return f"Meta F\u00edsica Esperada {y}"
def col_pct(y):   return f"PORCENTAJE DE EJECUCI\u00d3N {y}"
def col_cat(y):   return f"CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA {y}"
def col_pf(y):    return f"Programaci\u00f3n Financiera {y}"
def col_ef(y):    return f"Ejecuci\u00f3n Financiera {y}"

COLS_PI_REAL = [
    "Codigo Meta", COL_LINEA, "Sector PDD", "Numero Programa PDD", "Programa PDD",
    "Meta de cuatrenio", "Tipo de Acumulaci\u00f3n", "Responsable",
    col_meta("2024"), col_meta("2025"), col_meta("2026"), col_meta("2027"),
    "PROYECTOS 2024","PROYECTOS 2025","PROYECTOS/GESTIONES PROGRAMADAS 2026","PROYECTOS 2026","PROYECTOS 2027",
    "EJECUCI\u00d3N 2024", col_pct("2024"), col_cat("2024"),
    "EJECUCI\u00d3N 2025", col_pct("2025"), col_cat("2025"),
    "EJECUCI\u00d3N 2026", col_pct("2026"), col_cat("2026"),
    "EJECUCI\u00d3N ACUMULADA", COL_PCT_ACUM, "CATEGOR\u00cdA DE EJECUCI\u00d3N ACUMULADA",
]

PROG_COLS = {s: [
    f"programaci\u00f3n recursos propios icld{s}",
    f"programaci\u00f3n recursos propios icde{s}",
    f"programaci\u00f3n sgp educaci\u00f3n{s}",
    f"programaci\u00f3n sgp salud{s}",
    f"programaci\u00f3n sgp apsb{s}",
    f"programaci\u00f3n cofinanciaci\u00f3n municipio{s}",
    f"programaci\u00f3n cofinanciaci\u00f3n naci\u00f3n{s}",
    f"programaci\u00f3n cr\u00e9dito{s}",
    f"programaci\u00f3n regal\u00edas{s}",
    f"programaci\u00f3n otras fuentes{s}",
] for s in ["24","25","26","27"]}

SCHEMAS = {
    "Plan Indicativo": {
        "table": "tblPlanIndicativo_2",
        "cols": [
            {"col":"Codigo Meta","tipo":"Texto","ejemplo":"MT-ED-0001"},
            {"col":"L\u00ednea Estrat\u00e9gica","tipo":"Texto","ejemplo":"Linea 1 - Bienestar y Equidad Social"},
            {"col":"Sector PDD","tipo":"Texto","ejemplo":"Educacion"},
            {"col":"Programa PDD","tipo":"Texto","ejemplo":"1.1 Educacion con calidad e incluyente"},
            {"col":"Meta de cuatrenio","tipo":"Numero","ejemplo":"10000"},
            {"col":"Meta F\u00edsica Esperada 2026","tipo":"Numero","ejemplo":"2500"},
            {"col":"EJECUCI\u00d3N 2026","tipo":"Numero","ejemplo":"2300"},
            {"col":"PORCENTAJE DE EJECUCI\u00d3N 2026","tipo":"Decimal","ejemplo":"0.92 (representa 92%)"},
            {"col":"CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA 2026","tipo":"Texto","ejemplo":"Superior | Alto | Medio | Minimo"},
            {"col":"PORCENTAJE DE EJECUCI\u00d3N ACUMULADA","tipo":"Decimal","ejemplo":"0.46"},
            {"col":"Programaci\u00f3n recursos propios icld26","tipo":"Numero","ejemplo":"500000000"},
            {"col":"Programaci\u00f3n regal\u00edas26","tipo":"Numero","ejemplo":"200000000"},
        ],
    },
    "Hacienda 2026": {
        "table": "EjecucionHacienda2026",
        "cols": [
            {"col":"RP","tipo":"Numero","ejemplo":"120000000"},
            {"col":"CODIGO META","tipo":"Texto","ejemplo":"MT-ED-0001"},
            {"col":"CLASIFICACI\u00d3N RECURSOS","tipo":"Texto","ejemplo":"ICLD | SGP EDUCACION"},
            {"col":"PROYECTO ARCHIVADO","tipo":"Texto","ejemplo":"(vacio = activo)"},
            {"col":"SE VA A CARGAR EN PI","tipo":"Texto","ejemplo":"(vacio = aplica)"},
            {"col":"DISTRIBUIR DE FORMA EQUITATIVA","tipo":"Texto","ejemplo":"SI | NO"},
        ],
    },
    "Regalias 2026": {
        "table": "Pagos_Regalias_2026",
        "cols": [
            {"col":"PAGO EJECUTADO VALOR","tipo":"Numero","ejemplo":"75000000"},
            {"col":"CODIGO META","tipo":"Texto","ejemplo":"MT-ED-0001"},
            {"col":"CLASIFICACI\u00d3N RECURSOS","tipo":"Texto","ejemplo":"REGALIAS"},
            {"col":"ULTIMA FECHA PAGO","tipo":"Fecha","ejemplo":"2026-03-04"},
        ],
    },
}

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(page_title="Dashboard PDD", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500&display=swap');

html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;color:{C['gris']};}}

.main-header{{
  background:linear-gradient(135deg,{C['azul_osc']} 0%,{C['azul']} 60%,{C['cyan']} 100%);
  padding:2.2rem 3rem 1.8rem;border-radius:0 0 2rem 2rem;
  margin:-1rem -1rem 2rem -1rem;color:white;
}}
.main-header h1{{font-family:'Sora',sans-serif;font-weight:700;font-size:2rem;margin:0;letter-spacing:-0.5px;}}
.main-header p{{margin:.35rem 0 0;font-size:.9rem;opacity:.82;}}

.kpi-card{{background:white;border-radius:.9rem;padding:1.2rem 1.5rem;
  box-shadow:0 2px 12px rgba(0,0,0,.07);border-left:5px solid {C['azul']};margin-bottom:.8rem;}}
.kpi-card.v{{border-left-color:{C['verde']};}}
.kpi-card.c{{border-left-color:{C['cyan']};}}
.kpi-card.n{{border-left-color:{C['naranja']};}}
.kpi-card.ca{{border-left-color:{C['cafe']};}}
.kpi-value{{font-family:'Sora',sans-serif;font-size:2rem;font-weight:700;line-height:1.1;}}
.kpi-label{{font-size:.78rem;text-transform:uppercase;letter-spacing:.8px;color:#6b7280;margin-top:.25rem;}}
.kpi-tip{{font-size:.72rem;color:#9ca3af;margin-top:.45rem;border-top:1px solid #f3f4f6;padding-top:.4rem;}}

.sec-title{{font-family:'Sora',sans-serif;font-size:1.05rem;font-weight:600;color:{C['azul_osc']};
  border-bottom:2px solid {C['cyan']};padding-bottom:.35rem;margin:1.8rem 0 .9rem;}}

section[data-testid="stSidebar"]{{background:{C['azul_osc']};}}
section[data-testid="stSidebar"] *{{color:white!important;}}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{{color:{C['cyan']}!important;font-family:'Sora',sans-serif;}}
section[data-testid="stSidebar"] label{{color:#cbd5e1!important;font-size:.8rem;text-transform:uppercase;letter-spacing:.5px;}}

.err-box{{background:#fff7f0;border:1.5px solid {C['salmon']};border-radius:.8rem;padding:1.1rem 1.4rem;margin:.9rem 0;}}
.err-box h4{{color:#c0392b;margin:0 0 .5rem;font-family:'Sora',sans-serif;}}
.sch-tbl{{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:.7rem;}}
.sch-tbl th{{background:{C['azul_osc']};color:white;padding:.45rem .75rem;text-align:left;}}
.sch-tbl td{{padding:.35rem .75rem;border-bottom:1px solid #e5e7eb;}}
.sch-tbl tr:nth-child(even) td{{background:#f9fafb;}}

/* Tabla formateada */
.dash-table{{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:.5rem;}}
.dash-table thead th{{background:{C['azul_osc']};color:white;padding:.5rem .9rem;
  text-align:left;font-family:'Sora',sans-serif;font-size:.78rem;letter-spacing:.3px;
  position:sticky;top:0;}}
.dash-table tbody tr:hover td{{background:#f0f7ff;}}
.dash-table td{{padding:.45rem .9rem;border-bottom:1px solid #e5e7eb;vertical-align:middle;}}
.dash-table tbody tr:nth-child(even) td{{background:#f9fafb;}}
.pill{{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.74rem;font-weight:600;}}

.upload-zone{{background:#f8fafc;border:2px dashed {C['cyan']};border-radius:1rem;
  padding:1.4rem;margin:.5rem 0 1rem;text-align:center;color:#6b7280;}}
hr.sep{{border:none;border-top:1px solid #e5e7eb;margin:1.4rem 0;}}
.footer{{text-align:center;font-size:.75rem;color:#9ca3af;margin-top:2.5rem;
  padding-top:.8rem;border-top:1px solid #e5e7eb;}}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def fmt_pct(v):
    return "N/A" if v is None else f"{v*100:.1f}%"

def kpi(label, value, cls="", tip=""):
    t = f'<div class="kpi-tip">Como se calcula: {tip}</div>' if tip else ""
    st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-value">{value}</div>'
                f'<div class="kpi-label">{label}</div>{t}</div>', unsafe_allow_html=True)

def sec(text):
    st.markdown(f'<div class="sec-title">{text}</div>', unsafe_allow_html=True)

def pill_html(label, color):
    return (f'<span class="pill" style="background:{color}22;color:{color};'
            f'border:1px solid {color}">{label}</span>')

def show_schema_error(name, schema, table=""):
    tnote = (f'<p style="margin:0 0 .5rem;font-size:.83rem"><b>Tabla Excel esperada:</b> '
             f'<code>{table}</code></p>') if table else ""
    rows = "".join(f"<tr><td><code>{r['col']}</code></td><td>{r['tipo']}</td>"
                   f"<td>{r['ejemplo']}</td></tr>" for r in schema)
    st.markdown(f"""<div class="err-box"><h4>Error al leer {name}</h4>
    <p>Verifica que el archivo contenga estas columnas:</p>{tnote}
    <table class="sch-tbl"><thead><tr><th>Columna</th><th>Tipo</th><th>Ejemplo real</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <p style="margin-top:.7rem;font-size:.79rem;color:#6b7280"><b>Tip:</b> El archivo debe
    contener una tabla Excel (Insert &gt; Table) con el nombre indicado. Las tildes y mayusculas
    deben coincidir exactamente.</p></div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# I/O
# ------------------------------------------------------------------
def to_bio(src):
    if isinstance(src, (bytes, bytearray)): return io.BytesIO(src)
    if isinstance(src, io.BytesIO): src.seek(0); return src
    return io.BytesIO(src)

def read_xl(src, table, cols=None):
    try:
        kw = {"table_name": table}
        if cols: kw["columns"] = cols
        return pl.read_excel(src if isinstance(src,str) else to_bio(src), **kw)
    except Exception:
        return None

def fetch(url):
    try:
        r = requests.get(url, timeout=40)
        r.raise_for_status()
        return r.content
    except Exception:
        return None

# ------------------------------------------------------------------
# PROCESAMIENTO
# ------------------------------------------------------------------
def prog_fin_expr(df_low, suf):
    existing = [c for c in PROG_COLS[suf] if c in df_low.columns]
    if not existing: return pl.lit(0.0)
    e = pl.col(existing[0]).cast(pl.Float64)
    for c in existing[1:]: e = e + pl.col(c).cast(pl.Float64)
    return e

def proc_regalias(src, year):
    tbl = {"2024":"EjecucionRegalias","2025":"Pagos_Regalias_2025","2026":"Pagos_Regalias_2026"}
    df = read_xl(src, tbl[year])
    if df is None: return None
    try:
        df = df.select(pl.all().name.map(lambda x: x.strip().upper().replace("_X0009_","")))
        if year == "2024":
            df = (df.select(["CODIGO META","COMPROMISOS",COL_CLASIF.upper()])
                    .with_columns(pl.col("CODIGO META").fill_null(""))
                    .filter(pl.col("CODIGO META")!="", pl.col("CODIGO META").str.starts_with("MT"))
                    .rename({"COMPROMISOS":"RP"}))
        elif year == "2025":
            df = (df.select(["PAGOS REGALIAS","CODIGO META",COL_CLASIF.upper()])
                    .rename({"PAGOS REGALIAS":"RP"})
                    .with_columns(pl.col("CODIGO META").fill_null(""))
                    .filter(pl.col("CODIGO META")!=""))
        elif year == "2026":
            df = (df.filter((pl.col("ULTIMA FECHA PAGO")>=pl.date(2026,1,1))&
                            (pl.col("ULTIMA FECHA PAGO")<=pl.date(2026,12,31)))
                    .select(["PAGO EJECUTADO VALOR","CODIGO META",COL_CLASIF.upper()])
                    .rename({"PAGO EJECUTADO VALOR":"RP"})
                    .with_columns(pl.col("CODIGO META").fill_null(""))
                    .filter(pl.col("CODIGO META")!=""))
        return df.select(["CODIGO META","RP"])
    except Exception:
        return None

def proc_hacienda(src, year):
    tbl = {"2024":"EjecucionHaciendaDiciembre","2025":"EjecucionHaciendaDiciembre2025","2026":"EjecucionHacienda2026"}
    df = read_xl(src, tbl[year])
    if df is None: return None
    try:
        if year == "2024":
            df = (df.select(["RP","CODIGO META",COL_CLASIF])
                    .with_columns(pl.col("CODIGO META",COL_CLASIF).fill_null(""))
                    .filter(pl.col("CODIGO META")!="", pl.col(COL_CLASIF)!=""))
        else:
            df = (df.with_columns(
                      pl.col("PROYECTO ARCHIVADO","CODIGO META",COL_CLASIF,"SE VA A CARGAR EN PI").fill_null(""),
                      pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA")=="SI")
                        .then(pl.col("RP")/2).otherwise(pl.col("RP")))
                    .filter(pl.col("PROYECTO ARCHIVADO")=="", pl.col("CODIGO META")!="",
                            pl.col(COL_CLASIF)!="", pl.col("SE VA A CARGAR EN PI")==""))
        return df.select(["CODIGO META","RP"])
    except Exception:
        return None

def merge_ef(reg, hac, name):
    frames = [f for f in [reg,hac] if f is not None and not f.is_empty()]
    if not frames:
        return pl.DataFrame({"CODIGO META":pl.Series([],dtype=pl.Utf8),
                              name:pl.Series([],dtype=pl.Float64)})
    return (pl.concat(frames,how="diagonal")
              .group_by("CODIGO META").agg(pl.col("RP").sum().alias(name)))

@st.cache_data(show_spinner=False)
def load_all(pi_b, h24_b, r24_b, h25_b, r25_b, h26_b, r26_b):
    # Plan Indicativo
    pi = read_xl(pi_b, "tblPlanIndicativo_2")
    if pi is None: return None, ["Plan Indicativo"]

    orden_lin  = read_xl(pi_b, "orden_lineas")
    orden_sec  = read_xl(pi_b, "orden_sectores")
    orden_prog = read_xl(pi_b, "orden_programas")
    homolog    = read_xl(pi_b, "HomologacionSecretarias")

    avail = [c for c in COLS_PI_REAL if c in pi.columns]
    fisicas = pi.select(avail)

    pi_low = pi.select(pl.all().name.map(lambda x: x.strip().lower()))
    exprs = [pl.col("codigo meta")]
    for suf, yr in [("24","2024"),("25","2025"),("26","2026"),("27","2027")]:
        exprs.append(prog_fin_expr(pi_low, suf).alias(col_pf(yr)))
    prog = pi_low.select(exprs)

    # Ejecuciones financieras
    ef24 = merge_ef(proc_regalias(r24_b,"2024"), proc_hacienda(h24_b,"2024"), col_ef("2024"))
    ef25 = merge_ef(proc_regalias(r25_b,"2025"), proc_hacienda(h25_b,"2025"), col_ef("2025"))
    ef26 = merge_ef(proc_regalias(r26_b,"2026"), proc_hacienda(h26_b,"2026"), col_ef("2026"))

    prog = (prog.join(ef24,left_on="codigo meta",right_on="CODIGO META",how="left")
                .join(ef25,left_on="codigo meta",right_on="CODIGO META",how="left")
                .join(ef26,left_on="codigo meta",right_on="CODIGO META",how="left")
                .with_columns(pl.col(col_ef("2024"),col_ef("2025"),col_ef("2026")).fill_null(0)))

    pff = fisicas.join(prog, left_on="Codigo Meta", right_on="codigo meta", how="left")
    meta_cs = [col_meta(y) for y in ["2024","2025","2026","2027"] if col_meta(y) in pff.columns]
    if meta_cs: pff = pff.with_columns([pl.col(c).fill_null(0) for c in meta_cs])

    return {"pff":pff,"orden_lin":orden_lin,"orden_sec":orden_sec,
            "orden_prog":orden_prog,"homolog":homolog}, []

# ------------------------------------------------------------------
# GRAFICO GAUGE
# ------------------------------------------------------------------
def gauge(val, title, color):
    # El gauge muestra hasta 120 para que Superior (>=100%) sea visible
    display_val = min(val * 100, 120)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=display_val,
        number={"suffix":"%","font":{"size":30,"color":color,"family":"Sora"},
                "valueformat":".1f"},
        title={"text":title,"font":{"size":12,"color":"#6b7280"}},
        gauge={
            "axis":{"range":[0,120],"tickvals":[0,29,59,99,120],
                    "ticktext":["0%","29%","59%","99%","≥100%"],
                    "tickfont":{"size":9}},
            "bar":{"color":color,"thickness":.28},
            "bgcolor":"#f3f4f6","borderwidth":0,
            # Semaforización oficial: Mínimo 0-29 | Medio 30-59 | Alto 60-99 | Superior ≥100
            "steps":[
                {"range":[0,  29], "color":"#fee2e2"},   # Mínimo  - salmon
                {"range":[29, 59], "color":"#fef3c7"},   # Medio   - amarillo
                {"range":[59, 99], "color":"#dbeafe"},   # Alto    - azul claro
                {"range":[99,120], "color":"#d1fae5"},   # Superior- verde
            ],
            "threshold":{"line":{"color":"#374151","width":2},"thickness":.75,"value":display_val},
        }
    ))
    fig.update_layout(height=210, margin=dict(t=40,b=5,l=15,r=15), paper_bgcolor="white")
    return fig

# ------------------------------------------------------------------
# TABLA FORMATEADA HTML
# ------------------------------------------------------------------
def html_table(df: pd.DataFrame, col_pct: list = None, col_money: list = None,
               col_sem: str = None, tooltips: dict = None) -> str:
    col_pct   = col_pct   or []
    col_money = col_money or []
    tooltips  = tooltips  or {}

    def th(name):
        tip = tooltips.get(name,"")
        tip_attr = f' title="{tip}"' if tip else ""
        style = ' style="cursor:help;border-bottom:1px dashed rgba(255,255,255,.5)"' if tip else ""
        return f"<th{tip_attr}{style}>{name}</th>"

    headers = "".join(th(c) for c in df.columns)
    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for c in df.columns:
            v = row[c]
            if c in col_pct and pd.notna(v):
                # Acepta float 0-1 (ej. 0.92) o float >1 ya multiplicado (ej. 92.0)
                try:
                    raw_f = float(str(v).replace("%","").strip())
                    # Si el valor está en escala 0-1, lo dejamos; si está en 0-100, dividimos
                    raw = raw_f if raw_f <= 1.5 else raw_f / 100.0
                except (ValueError, TypeError):
                    raw = 0.0
                color = semaforo_color(raw)
                lbl   = semaforo_label(raw)
                cells += f'<td>{pill_html(lbl,color)} &nbsp; {fmt_pct(raw)}</td>'
            elif c in col_money and pd.notna(v):
                try:
                    cells += f'<td>${float(v):,.0f}</td>'
                except (ValueError, TypeError):
                    cells += f"<td>{v}</td>"
            elif c == col_sem and pd.notna(v):
                color = SEM_COLORS.get(str(v), C["cafe"])
                cells += f'<td>{pill_html(str(v),color)}</td>'
            else:
                cells += f"<td>{v if pd.notna(v) else ''}</td>"
        rows += f"<tr>{cells}</tr>"

    return (f'<div style="overflow-x:auto;max-height:420px;overflow-y:auto">'
            f'<table class="dash-table"><thead><tr>{headers}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Dashboard PDD")
    st.markdown("#### Reporte de Avance 2024-2027")
    st.markdown("---")
    st.markdown("### Fuente de datos")
    modo = st.radio("Como cargar archivos:", ["GitHub (2026 + PI)", "Todo manual"], index=0)
    st.markdown("---")
    st.markdown("### Filtros")
    vig = st.selectbox("Vigencia:", VIGENCIAS, index=2)
    ph_lin = st.empty()
    ph_sec = st.empty()
    ph_res = st.empty()
    st.markdown("---")
    st.markdown('<div style="font-size:.73rem;color:#94a3b8;line-height:1.6">'
                'Los archivos 2024 y 2025 se cargan automaticamente desde GitHub.<br>'
                'Solo necesitas subir el Plan Indicativo y los archivos 2026.</div>',
                unsafe_allow_html=True)

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
  <h1>Reporte de Avance del Plan de Desarrollo</h1>
  <p>Ejecucion Fisica y Financiera &middot; Vigencia <strong>{vig}</strong> &middot; Cuatrienio 2024&ndash;2027</p>
</div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# CARGA DE ARCHIVOS
# ------------------------------------------------------------------
pi_b = h24_b = r24_b = h25_b = r25_b = h26_b = r26_b = None

if modo == "GitHub (2026 + PI)":
    st.markdown("### Carga de Archivos")
    with st.expander("Archivos necesarios (Plan Indicativo + Vigencia 2026)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pi_file  = st.file_uploader("Plan Indicativo 2024-2027", type=["xlsx"], key="pi")
        with c2:
            h26_file = st.file_uploader("Hacienda 2026",             type=["xlsx"], key="h26")
        with c3:
            r26_file = st.file_uploader("Regalias 2026",             type=["xlsx"], key="r26")

    pi_b  = pi_file.read()  if pi_file  else None
    h26_b = h26_file.read() if h26_file else None
    r26_b = r26_file.read() if r26_file else None

    if pi_b:
        with st.spinner("Descargando archivos 2024-2025 desde GitHub..."):
            h24_b = fetch(GITHUB_H24)
            r24_b = fetch(GITHUB_R24)
            h25_b = fetch(GITHUB_H25)
            r25_b = fetch(GITHUB_R25)
        failed = [n for n,b in [("Hacienda 2024",h24_b),("Regalias 2024",r24_b),
                                  ("Hacienda 2025",h25_b),("Regalias 2025",r25_b)] if b is None]
        if failed:
            st.warning(f"No se pudieron descargar desde GitHub: {', '.join(failed)}. "
                       "Los datos financieros de esas vigencias no estaran disponibles.")
    else:
        st.markdown('<div class="upload-zone">Carga el <strong>Plan Indicativo</strong> para comenzar.'
                    '<br><small>Los archivos 2024 y 2025 se descargan automaticamente.</small></div>',
                    unsafe_allow_html=True)

else:
    st.markdown("### Carga de Archivos")
    with st.expander("Todos los archivos", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            pi_file  = st.file_uploader("Plan Indicativo 2024-2027", type=["xlsx"], key="pi2")
            h24_file = st.file_uploader("Hacienda 2024",             type=["xlsx"], key="h24")
            r24_file = st.file_uploader("Regalias 2024",             type=["xlsx"], key="r24")
            h25_file = st.file_uploader("Hacienda 2025",             type=["xlsx"], key="h25")
        with c2:
            r25_file = st.file_uploader("Regalias 2025",             type=["xlsx"], key="r25")
            h26_file = st.file_uploader("Hacienda 2026",             type=["xlsx"], key="h26b")
            r26_file = st.file_uploader("Regalias 2026",             type=["xlsx"], key="r26b")

    pi_b  = pi_file.read()  if pi_file  else None
    h24_b = h24_file.read() if h24_file else None
    r24_b = r24_file.read() if r24_file else None
    h25_b = h25_file.read() if h25_file else None
    r25_b = r25_file.read() if r25_file else None
    h26_b = h26_file.read() if h26_file else None
    r26_b = r26_file.read() if r26_file else None

    if not pi_b:
        st.markdown('<div class="upload-zone">Carga el <strong>Plan Indicativo</strong> para comenzar.</div>',
                    unsafe_allow_html=True)

if not pi_b:
    st.stop()

# ------------------------------------------------------------------
# PROCESAMIENTO
# ------------------------------------------------------------------
with st.spinner("Procesando datos..."):
    res, errs = load_all(pi_b, h24_b, r24_b, h25_b, r25_b, h26_b, r26_b)

if res is None:
    show_schema_error("Plan Indicativo", SCHEMAS["Plan Indicativo"]["cols"],
                      SCHEMAS["Plan Indicativo"]["table"])
    st.stop()

pff    = res["pff"]
ol     = res["orden_lin"]
os_    = res["orden_sec"]
op     = res["orden_prog"]
hom    = res["homolog"]

# Columnas activas
CM  = col_meta(vig)
CP  = col_pct(vig)
CCA = col_cat(vig)
CEF = col_ef(vig)
CPF = col_pf(vig)
cL  = COL_LINEA if COL_LINEA in pff.columns else "Linea Estrategica"

# Filtros sidebar
lo = sorted(pff[cL].drop_nulls().unique().to_list()) if cL in pff.columns else []
so = sorted(pff["Sector PDD"].drop_nulls().unique().to_list()) if "Sector PDD" in pff.columns else []
ro = sorted(pff["Responsable"].drop_nulls().unique().to_list()) if "Responsable" in pff.columns else []
with ph_lin: fl = st.multiselect("Linea:", lo, placeholder="Todas")
with ph_sec: fs = st.multiselect("Sector:", so, placeholder="Todos")
with ph_res: fr = st.multiselect("Dependencia:", ro, placeholder="Todas")

pf = pff.clone()
if fl and cL in pf.columns:    pf = pf.filter(pl.col(cL).is_in(fl))
if fs and "Sector PDD" in pf.columns: pf = pf.filter(pl.col("Sector PDD").is_in(fs))
if fr and "Responsable" in pf.columns: pf = pf.filter(pl.col("Responsable").is_in(fr))

# ------------------------------------------------------------------
# CALCULOS GLOBALES (sección: Ejecución Física por Categorías - notebook)
# ------------------------------------------------------------------
n_total = len(pf)
n_prog  = int(pf.filter(pl.col(CM).fill_null(0)!=0).height) if CM in pf.columns else 0

avance_vig = 0.0
if CP in pf.columns and CM in pf.columns and n_prog > 0:
    avance_vig = float(pf.filter(pl.col(CM).fill_null(0)!=0)
                         .select(pl.col(CP).fill_null(0).mean()).item() or 0)

avance_acum = 0.0
if COL_PCT_ACUM in pf.columns:
    avance_acum = float(pf.select(pl.col(COL_PCT_ACUM).fill_null(0).mean()).item() or 0)

n_sup = 0
if CCA in pf.columns and CM in pf.columns:
    n_sup = int(pf.filter(pl.col(CM).fill_null(0)!=0).filter(pl.col(CCA)=="Superior").height)

ejec_fin = 0.0; prog_fin = 0.0; pct_fin = 0.0
if CEF in pf.columns: ejec_fin = float(pf.select(pl.col(CEF).sum()).item() or 0)
if CPF in pf.columns: prog_fin = float(pf.select(pl.col(CPF).sum()).item() or 0)
if prog_fin > 0: pct_fin = ejec_fin / prog_fin

# Distribucion de metas (del notebook: distribucion_metas_pdd)
meta_cuatrenio = float(pf.select(pl.col("Meta de cuatrenio").fill_null(0).sum()).item() or 0) \
    if "Meta de cuatrenio" in pf.columns else 0
dist_metas = {}
for y in ["2024","2025","2026","2027"]:
    mc = col_meta(y)
    if mc in pf.columns and meta_cuatrenio > 0:
        dist_metas[y] = float(pf.select(pl.col(mc).fill_null(0).sum()).item() or 0) / meta_cuatrenio
    else:
        dist_metas[y] = 0.0

# Avance ponderado vigencia y cuatrienio (del notebook)
avance_pond_vig  = 0.0
avance_pond_acum = 0.0

# avance_pond_vig: ponderado por peso de cada programa en metas programadas de la vigencia
if n_prog > 0 and CP in pf.columns and "Programa PDD" in pf.columns:
    pv = (pf.filter(pl.col(CM).fill_null(0) != 0)
            .group_by("Programa PDD")
            .agg(pl.col(CP).fill_null(0).mean().alias("prom"),
                 pl.col("Codigo Meta").len().alias("n_prog_p"))
            .with_columns((pl.col("n_prog_p") / n_prog).alias("peso")))
    avance_pond_vig = float(pv.select((pl.col("prom") * pl.col("peso")).sum()).item() or 0)

# avance_pond_acum: ponderado por peso de cada programa sobre el total de metas
if COL_PCT_ACUM in pf.columns and "Programa PDD" in pf.columns and len(pf) > 0:
    n_tot = len(pf)
    pc = (pf.group_by("Programa PDD")
            .agg(pl.col(COL_PCT_ACUM).fill_null(0).mean().alias("prom"),
                 pl.col("Codigo Meta").len().alias("n_p"))
            .with_columns((pl.col("n_p") / n_tot).alias("peso")))
    avance_pond_acum = float(pc.select((pl.col("prom") * pl.col("peso")).sum()).item() or 0)

# ------------------------------------------------------------------
# TABS
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Resumen General", "Ejecucion Financiera", "Ejecucion Fisica", "Por Dependencia"
])

# ================================================================
# TAB 1: RESUMEN GENERAL
# ================================================================
with tab1:
    sec(f"Indicadores Clave - Vigencia {vig}")

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: kpi("Metas Totales", str(n_total), "",
                 "Total de indicadores de producto del PDD con los filtros aplicados.")
    with k2: kpi(f"Metas Programadas {vig}", str(n_prog), "c",
                 f"Indicadores cuya Meta Fisica Esperada {vig} es mayor a cero.")
    with k3: kpi(f"Avance Ponderado {vig}", fmt_pct(avance_pond_vig), "v",
                 f"Suma de (metas_prog_programa / total_metas_prog) × promedio_avance_programa. "
                 "Pondera cada programa segun su peso relativo en la vigencia.")
    with k4: kpi("Avance Ponderado Cuatrienio", fmt_pct(avance_pond_acum), "n",
                 "Suma de (metas_programa / total_metas) × promedio_avance_acumulado_programa. "
                 "Pondera el aporte de cada programa al cuatrienio completo.")
    with k5: kpi(f"Metas Superiores {vig}", str(n_sup), "ca",
                 f"Indicadores con CATEGORIA DE EJECUCION FISICA {vig} igual a 'Superior' "
                 "(ejecucion mayor o igual al 100%).")

    st.markdown('<hr class="sep">', unsafe_allow_html=True)

    # Gauges
    cg1,cg2,cg3 = st.columns(3)
    with cg1: st.plotly_chart(gauge(avance_pond_vig, f"Avance Ponderado {vig}",
                                     semaforo_color(avance_pond_vig)),
                               width="stretch", key="g1")
    with cg2: st.plotly_chart(gauge(avance_pond_acum, "Avance Ponderado Cuatrienio",
                                     semaforo_color(avance_pond_acum)),
                               width="stretch", key="g2")
    with cg3: st.plotly_chart(gauge(pct_fin, f"Ejecucion Financiera {vig}",
                                     semaforo_color(pct_fin)),
                               width="stretch", key="g3")

    st.caption(
        f"Avance Ponderado Vigencia: cada programa PDD aporta segun la proporcion de sus metas "
        f"programadas en {vig}. "
        "Avance Cuatrienio: cada programa aporta segun su proporcion sobre el total de metas del PDD. "
        "Ejecucion Financiera: (RP Hacienda + Pagos Regalias) / Programacion Financiera de la vigencia."
    )

    st.markdown('<hr class="sep">', unsafe_allow_html=True)

    # Distribucion de metas PDD (del notebook: distribucion_metas_pdd)
    sec("Distribucion de Metas del Plan de Cuatrenio")
    dcol1, dcol2 = st.columns([1.4, 1])
    with dcol1:
        fig_dist = go.Figure()
        years_d  = list(dist_metas.keys())
        vals_d   = [dist_metas[y] * 100 for y in years_d]
        colors_d = [semaforo_color(dist_metas[y]) for y in years_d]
        fig_dist.add_trace(go.Bar(
            x=years_d, y=vals_d,
            marker_color=colors_d,
            text=[f"{v:.1f}%" for v in vals_d],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Distribucion: %{y:.1f}%<extra></extra>",
        ))
        fig_dist.update_layout(
            title="Porcentaje de la meta cuatrienal programada por vigencia",
            yaxis_title="% sobre Meta Cuatrienal", yaxis_range=[0, max(vals_d or [0])*1.2+5],
            height=320, paper_bgcolor="white", plot_bgcolor="#fafafa",
            font={"family":"DM Sans"}, margin=dict(t=50,b=20,l=20,r=20),
        )
        st.plotly_chart(fig_dist, width="stretch", key="dist_bar")

    with dcol2:
        st.markdown("**Como se interpreta**")
        st.markdown(
            "Cada barra muestra que porcentaje de la meta total del cuatrienio "
            "fue programado para esa vigencia.<br>"
            "Se calcula como: <code>Suma(Meta Fisica Esperada año) / Suma(Meta de cuatrenio)</code>.<br><br>"
            "Una distribucion ideal seria balanceada entre los 4 años. "
            "Vigencias con mayor porcentaje tienen mayor exigencia de ejecucion.",
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown("**Semaforización oficial**")
        for lbl, rango in [("Superior","Mayor o igual al 100%"),("Alto","60% – 99%"),
                             ("Medio","30% – 59%"),("Minimo","0% – 29%")]:
            col = SEM_COLORS[lbl]
            st.markdown(
                f'<span class="pill" style="background:{col}22;color:{col};border:1px solid {col}">'
                f'{lbl}</span> &nbsp; {rango}', unsafe_allow_html=True)
            st.write("")

    # Categoria de ejecucion (semaforización oficial)
    if CCA in pf.columns and CM in pf.columns:
        sec(f"Semaforización de Metas - Vigencia {vig}")
        cat_df = (pf.filter(pl.col(CM).fill_null(0)!=0)
                    .group_by(CCA).agg(pl.col("Codigo Meta").len().alias("n"))
                    .drop_nulls().to_pandas())
        if not cat_df.empty:
            cp1,cp2 = st.columns([1.2,1])
            with cp1:
                labels = cat_df[CCA].tolist()
                vals   = cat_df["n"].tolist()
                cols_p = [SEM_COLORS.get(l, C["cafe"]) for l in labels]
                fig_pie = go.Figure(go.Pie(
                    labels=labels, values=vals, marker_colors=cols_p,
                    hole=.44, textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>%{value} metas<br>%{percent}<extra></extra>",
                ))
                fig_pie.update_layout(title=f"Categorias de ejecucion {vig}",
                                       height=340, paper_bgcolor="white",
                                       font={"family":"DM Sans"},
                                       margin=dict(t=50,b=10,l=10,r=10))
                st.plotly_chart(fig_pie, width="stretch", key="pie_cat")
            with cp2:
                # Tabla resumen categorias
                total_prog = cat_df["n"].sum()
                rows_cat = []
                for _, row in cat_df.iterrows():
                    rows_cat.append({
                        "Categoria": row[CCA],
                        "Metas": int(row["n"]),
                        "% del total programado": f"{row['n']/total_prog*100:.1f}%"
                    })
                cat_pd = pd.DataFrame(rows_cat)
                cat_pd = cat_pd.sort_values("Metas", ascending=False).reset_index(drop=True)
                st.markdown(html_table(cat_pd, col_sem="Categoria",
                    tooltips={"Categoria":f"Clasificacion segun la semaforización oficial. "
                                           "Superior ≥100% | Alto 60-99% | Medio 30-59% | Minimo <30%",
                              "% del total programado":"Proporcion sobre las metas con programacion en la vigencia."}),
                    unsafe_allow_html=True)

# ================================================================
# TAB 2: EJECUCION FINANCIERA
# ================================================================
with tab2:
    fin_ok = CEF in pf.columns and CPF in pf.columns
    if not fin_ok:
        st.info(f"No hay datos financieros para {vig}. Verifica que los archivos de hacienda y regalias esten cargados.")
    else:
        # Lineas
        sec(f"Ejecucion Financiera por Linea Estrategica - {vig}")
        if cL in pf.columns and ol is not None:
            ord_c = "Orden Linea" if "Orden Linea" in ol.columns else ol.columns[1]
            jc    = cL if cL in ol.columns else ol.columns[0]
            lf = (pf.group_by(cL).agg(pl.col(CPF).sum(), pl.col(CEF).sum())
                    .join(ol, left_on=cL, right_on=jc, how="inner")
                    .with_columns(pl.when(pl.col(CPF)==0).then(0.0)
                                    .otherwise(pl.col(CEF)/pl.col(CPF)).alias("Pct"))
                    .sort(ord_c).to_pandas())
            if not lf.empty:
                gtab1, gtab2 = st.tabs(["Grafico", "Tabla"])
                with gtab1:
                    fig_lf = go.Figure(go.Bar(
                        x=lf[CEF], y=lf[cL], orientation="h",
                        marker_color=[semaforo_color(v) for v in lf["Pct"]],
                        text=[fmt_pct(v) for v in lf["Pct"]], textposition="outside",
                        customdata=lf[[CPF,CEF,"Pct"]].values,
                        hovertemplate=(
                            "<b>%{y}</b><br>Programacion: $%{customdata[0]:,.0f}<br>"
                            "Ejecucion: $%{customdata[1]:,.0f}<br>Avance: %{text}<extra></extra>"),
                    ))
                    fig_lf.update_layout(xaxis_title="Ejecucion ($)",
                        height=max(320,len(lf)*46), paper_bgcolor="white",
                        plot_bgcolor="#fafafa", font={"family":"DM Sans"},
                        margin=dict(l=20,r=100,t=30,b=20))
                    st.plotly_chart(fig_lf, width="stretch", key="bar_lf")
                    st.caption("Ejecucion / Programacion de la vigencia. Semaforización oficial aplicada.")
                with gtab2:
                    lf_show = lf[[cL, CPF, CEF, "Pct"]].copy()
                    lf_show.columns = ["Linea Estrategica","Programacion ($)","Ejecucion ($)","% Avance"]
                    st.markdown(html_table(lf_show,
                        col_money=["Programacion ($)","Ejecucion ($)"],
                        col_pct=["% Avance"],
                        tooltips={"% Avance":"Ejecucion Financiera / Programacion Financiera de la vigencia.",
                                  "Programacion ($)":"Suma de todas las fuentes: ICLD, ICDE, SGP, Regalias, Credito, Cofinanciacion, Otras Fuentes.",
                                  "Ejecucion ($)":"RP registrados en Hacienda mas Pagos de Regalias."}),
                        unsafe_allow_html=True)

        # Sectores
        sec(f"Ejecucion Financiera por Sector PDD - {vig}")
        if "Sector PDD" in pf.columns and os_ is not None:
            ord_cs = "Orden Sector" if "Orden Sector" in os_.columns else os_.columns[1]
            sf = (pf.group_by("Sector PDD").agg(pl.col(CPF).sum(), pl.col(CEF).sum())
                    .join(os_, on="Sector PDD", how="inner")
                    .with_columns(pl.when(pl.col(CPF)==0).then(0.0)
                                    .otherwise(pl.col(CEF)/pl.col(CPF)).alias("Pct"))
                    .sort(ord_cs).to_pandas())
            if not sf.empty:
                gtab1, gtab2 = st.tabs(["Grafico", "Tabla"])
                with gtab1:
                    fig_sf = go.Figure(go.Bar(
                        x=sf[CEF], y=sf["Sector PDD"], orientation="h",
                        marker_color=[semaforo_color(v) for v in sf["Pct"]],
                        text=[fmt_pct(v) for v in sf["Pct"]], textposition="outside",
                        customdata=sf[[CPF,CEF,"Pct"]].values,
                        hovertemplate=(
                            "<b>%{y}</b><br>Programacion: $%{customdata[0]:,.0f}<br>"
                            "Ejecucion: $%{customdata[1]:,.0f}<br>Avance: %{text}<extra></extra>"),
                    ))
                    fig_sf.update_layout(xaxis_title="Ejecucion ($)",
                        height=max(320,len(sf)*46), paper_bgcolor="white",
                        plot_bgcolor="#fafafa", font={"family":"DM Sans"},
                        margin=dict(l=20,r=100,t=30,b=20))
                    st.plotly_chart(fig_sf, width="stretch", key="bar_sf")
                with gtab2:
                    sf_show = sf[["Sector PDD",CPF,CEF,"Pct"]].copy()
                    sf_show.columns = ["Sector PDD","Programacion ($)","Ejecucion ($)","% Avance"]
                    st.markdown(html_table(sf_show,
                        col_money=["Programacion ($)","Ejecucion ($)"], col_pct=["% Avance"],
                        tooltips={"% Avance":"Ejecucion / Programacion de la vigencia por sector."}),
                        unsafe_allow_html=True)

        # Comparativo anual
        sec("Ejecucion Financiera Acumulada 2024-2026")
        yrs = [y for y in ["2024","2025","2026"] if col_ef(y) in pf.columns]
        if yrs:
            ev = [float(pf.select(pl.col(col_ef(y)).sum()).item() or 0) for y in yrs]
            pv = [float(pf.select(pl.col(col_pf(y)).sum()).item() or 0)
                  if col_pf(y) in pf.columns else 0 for y in yrs]
            fig_acum = go.Figure()
            fig_acum.add_trace(go.Bar(name="Programacion",x=yrs,y=pv,
                                       marker_color=C["cyan"],opacity=.75))
            fig_acum.add_trace(go.Bar(name="Ejecucion",x=yrs,y=ev,
                                       marker_color=C["azul"]))
            fig_acum.update_layout(barmode="group",
                title="Programacion vs Ejecucion Financiera por Año",
                yaxis_title="Valor ($)", height=360, paper_bgcolor="white",
                plot_bgcolor="#fafafa", font={"family":"DM Sans"},
                legend=dict(orientation="h",y=1.1),
                margin=dict(l=20,r=20,t=60,b=20))
            st.plotly_chart(fig_acum, width="stretch", key="bar_acum")
            st.caption("Programacion: suma ICLD+ICDE+SGP+Regalias+Credito+Cofinanciacion+Otras Fuentes. "
                       "Ejecucion: RP Hacienda + Pagos Regalias.")

# ================================================================
# TAB 3: EJECUCION FISICA
# ================================================================
with tab3:
    # Lineas
    sec(f"Eficacia Operativa por Linea Estrategica - {vig}")
    if CP in pf.columns and cL in pf.columns and CM in pf.columns and n_prog > 0:
        pv_lin2 = (
            pf.filter(pl.col(CM).fill_null(0)!=0)
              .group_by(cL)
              .agg(pl.col(CP).fill_null(0).mean().alias("Avance"),
                   pl.col("Codigo Meta").len().alias("N Metas"))
              .to_pandas().sort_values("Avance",ascending=True)
        )
        gtab1, gtab2 = st.tabs(["Grafico","Tabla"])
        with gtab1:
            fig_fl = go.Figure(go.Bar(
                x=pv_lin2["Avance"]*100, y=pv_lin2[cL], orientation="h",
                marker_color=[semaforo_color(v) for v in pv_lin2["Avance"]],
                text=[fmt_pct(v) for v in pv_lin2["Avance"]], textposition="outside",
                customdata=pv_lin2[["N Metas"]].values,
                hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<br>Metas programadas: %{customdata[0]}<extra></extra>",
            ))
            fig_fl.update_layout(xaxis_title="% Promedio Ejecucion Fisica",
                height=max(320,len(pv_lin2)*48), paper_bgcolor="white",
                plot_bgcolor="#fafafa", font={"family":"DM Sans"},
                margin=dict(l=20,r=100,t=30,b=20))
            st.plotly_chart(fig_fl, width="stretch", key="bar_fl")
            st.caption(f"Promedio del PORCENTAJE DE EJECUCION {vig} de las metas con Meta Fisica Esperada > 0.")
        with gtab2:
            pv_show = pv_lin2[[cL,"Avance","N Metas"]].copy()
            pv_show["Semaforo"] = pv_show["Avance"].apply(semaforo_label)
            pv_show["Avance"]   = pv_show["Avance"].apply(fmt_pct)
            pv_show.columns     = ["Linea Estrategica","% Avance","Metas Prog.","Semaforo"]
            st.markdown(html_table(pv_show, col_pct=["% Avance"], col_sem="Semaforo",
                tooltips={"% Avance":f"Promedio de PORCENTAJE DE EJECUCION {vig} de metas con programacion.",
                          "Semaforo":"Semaforización oficial: Superior ≥100% | Alto 60-99% | Medio 30-59% | Minimo <30%"}),
                unsafe_allow_html=True)
    else:
        st.info("No hay columnas de ejecucion fisica para esta vigencia.")

    # Sectores
    sec(f"Ejecucion Fisica por Sector PDD - {vig}")
    if CP in pf.columns and "Sector PDD" in pf.columns and CM in pf.columns:
        sf_fis = (pf.filter(pl.col(CM).fill_null(0)!=0)
                    .group_by("Sector PDD")
                    .agg(pl.col(CP).fill_null(0).mean().alias("Avance"),
                         pl.col("Codigo Meta").len().alias("N Metas"))
                    .to_pandas().sort_values("Avance",ascending=True))
        if not sf_fis.empty:
            gtab1, gtab2 = st.tabs(["Grafico","Tabla"])
            with gtab1:
                fig_sf_fis = go.Figure(go.Bar(
                    x=sf_fis["Avance"]*100, y=sf_fis["Sector PDD"], orientation="h",
                    marker_color=[semaforo_color(v) for v in sf_fis["Avance"]],
                    text=[fmt_pct(v) for v in sf_fis["Avance"]], textposition="outside",
                    customdata=sf_fis[["N Metas"]].values,
                    hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<br>Metas: %{customdata[0]}<extra></extra>",
                ))
                fig_sf_fis.update_layout(xaxis_title="% Promedio Ejecucion Fisica",
                    height=max(320,len(sf_fis)*48), paper_bgcolor="white",
                    plot_bgcolor="#fafafa", font={"family":"DM Sans"},
                    margin=dict(l=20,r=100,t=30,b=20))
                st.plotly_chart(fig_sf_fis, width="stretch", key="bar_sf_fis")
            with gtab2:
                sf_show = sf_fis[["Sector PDD","Avance","N Metas"]].copy()
                sf_show["Semaforo"] = sf_show["Avance"].apply(semaforo_label)
                sf_show["Avance"]   = sf_show["Avance"].apply(fmt_pct)
                sf_show.columns     = ["Sector PDD","% Avance","Metas Prog.","Semaforo"]
                st.markdown(html_table(sf_show, col_pct=["% Avance"], col_sem="Semaforo"),
                    unsafe_allow_html=True)

    # Tabla completa de metas
    sec("Detalle de Metas PDD")
    dcols = [c for c in ["Codigo Meta",cL,"Sector PDD","Programa PDD","Responsable",
                          CM,CP,CCA,COL_PCT_ACUM] if c in pf.columns]
    tbl = pf.select(dcols).to_pandas()
    for pc in [CP, COL_PCT_ACUM]:
        if pc in tbl.columns:
            tbl[pc] = tbl[pc].fillna(0)
    tbl_show = tbl.copy()
    # Asegurar que la columna de categoria existe antes de usarla en html_table
    col_sem_det = CCA if CCA in tbl_show.columns else None
    st.markdown(html_table(tbl_show,
        col_pct=[CP, COL_PCT_ACUM] if COL_PCT_ACUM in tbl_show.columns else [CP],
        col_sem=col_sem_det,
        tooltips={
            CP: f"PORCENTAJE DE EJECUCION {vig} del indicador (0.92 = 92%).",
            COL_PCT_ACUM: "Avance acumulado frente a la meta total del cuatrienio 2024-2027.",
            CCA: f"Semaforización: Superior ≥100% | Alto 60-99% | Medio 30-59% | Minimo <30%",
            CM: f"Meta Fisica Esperada en {vig} para este indicador.",
        }),
        unsafe_allow_html=True)

# ================================================================
# TAB 4: POR DEPENDENCIA
# ================================================================
with tab4:
    sec(f"Avance por Dependencia Responsable - {vig}")

    if CP not in pf.columns or CM not in pf.columns:
        st.info("No hay datos suficientes para mostrar el avance por dependencia.")
    else:
        # avance_por_dependencia del notebook
        cat_e = (pl.when(pl.col(CCA)=="Superior").then(1).otherwise(0).alias("Sup")
                 if CCA in pf.columns else pl.lit(0).alias("Sup"))
        acum_e = (pl.col(COL_PCT_ACUM).fill_null(0).mean().alias("Ejec_Acum")
                  if COL_PCT_ACUM in pf.columns else pl.lit(0.0).alias("Ejec_Acum"))

        dep = (pf.filter(pl.col(CM).fill_null(0)!=0)
                 .with_columns(cat_e, pl.lit(1).alias("mp"))
                 .group_by(pl.col("Responsable").str.strip_chars())
                 .agg(pl.col(CP).fill_null(0).mean().alias("Avance"),
                      pl.col("mp").sum().alias("N Metas"),
                      pl.col("Sup").sum().alias("N Superiores"),
                      acum_e))

        if hom is not None:
            rc = next((c for c in hom.columns if "Responsable" in c and "PI" in c), None)
            if rc: dep = dep.join(hom.rename({rc:"Responsable"}), on="Responsable", how="left")

        dep_pd = dep.to_pandas()
        if dep_pd.empty:
            st.info("No se encontraron datos.")
        else:
            dep_pd["Avance"]     = dep_pd["Avance"].fillna(0)
            dep_pd["Ejec_Acum"]  = dep_pd["Ejec_Acum"].fillna(0)
            dep_pd["Semaforo"]   = dep_pd["Avance"].apply(semaforo_label)
            name_c = "Dependencia Responsable" if "Dependencia Responsable" in dep_pd.columns else "Responsable"
            dep_s  = dep_pd.sort_values("Avance",ascending=True)

            gtab1,gtab2 = st.tabs(["Grafico","Tabla"])
            with gtab1:
                fig_dep = go.Figure(go.Bar(
                    x=dep_s["Avance"]*100, y=dep_s[name_c], orientation="h",
                    marker_color=[semaforo_color(v) for v in dep_s["Avance"]],
                    text=[fmt_pct(v) for v in dep_s["Avance"]], textposition="outside",
                    customdata=dep_s[["N Metas","N Superiores","Ejec_Acum"]].values,
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        f"Avance {vig}: %{{x:.1f}}%<br>"
                        "Metas programadas: %{customdata[0]}<br>"
                        "Metas superiores: %{customdata[1]}<br>"
                        "Avance acumulado: %{customdata[2]:.1%}<extra></extra>"),
                ))
                fig_dep.update_layout(xaxis_title=f"% Promedio Ejecucion {vig}",
                    height=max(360,len(dep_s)*48), paper_bgcolor="white",
                    plot_bgcolor="#fafafa", font={"family":"DM Sans"},
                    margin=dict(l=20,r=100,t=30,b=20))
                st.plotly_chart(fig_dep, width="stretch", key="bar_dep")
                st.caption(
                    f"Promedio del PORCENTAJE DE EJECUCION {vig} de las metas programadas a cargo de cada dependencia. "
                    "Metas superiores: indicadores con categoria 'Superior'. "
                    "Avance acumulado: promedio del PORCENTAJE DE EJECUCION ACUMULADA (2024-2027)."
                )
            with gtab2:
                tbl_dep = dep_pd[[name_c,"N Metas","N Superiores","Avance","Ejec_Acum","Semaforo"]].copy()
                tbl_dep.columns = ["Dependencia","Metas Prog.","Metas Superiores",
                                    f"% Avance {vig}","% Avance Acumulado","Semaforo"]
                # Dejar como float 0-1 para que html_table aplique la semaforización correctamente
                tbl_dep = tbl_dep.sort_values(f"% Avance {vig}", ascending=False).reset_index(drop=True)
                st.markdown(html_table(tbl_dep,
                    col_pct=[f"% Avance {vig}","% Avance Acumulado"],
                    col_sem="Semaforo",
                    tooltips={
                        f"% Avance {vig}":f"Promedio del PORCENTAJE DE EJECUCION {vig} de las metas programadas.",
                        "% Avance Acumulado":"Promedio del PORCENTAJE DE EJECUCION ACUMULADA (cuatrienio completo).",
                        "Metas Superiores":f"Metas con CATEGORIA DE EJECUCION FISICA {vig} igual a 'Superior'.",
                    }),
                    unsafe_allow_html=True)

# ------------------------------------------------------------------
# ARCHIVOS FALTANTES 2026
# ------------------------------------------------------------------
miss = []
if h26_b is None: miss.append(("Hacienda 2026","Hacienda 2026"))
if r26_b is None: miss.append(("Regalias 2026","Regalias 2026"))
if miss:
    with st.expander("Archivos 2026 no cargados - datos financieros incompletos", expanded=False):
        for nm,k in miss:
            show_schema_error(nm, SCHEMAS[k]["cols"], SCHEMAS[k]["table"])

st.markdown('<div class="footer">Dashboard de Avance PDD &middot; Streamlit &middot; Polars &middot; Plotly</div>',
            unsafe_allow_html=True)
