"""
Dashboard de Reporte de Avance PDD - Plan Indicativo 2024-2027
Basado fielmente en el notebook ReporteAvance.ipynb
"""

import streamlit as st
import polars as pl
import pandas as pd
import plotly.graph_objects as go
import io, requests
from typing import Optional

# ──────────────────────────────────────────────────────────────────
# PALETA CORPORATIVA Y SEMAFORIZACIÓN OFICIAL
# 0-29% Mínimo | 30-59% Medio | 60-99% Alto | ≥100% Superior
# ──────────────────────────────────────────────────────────────────
C = {
    "verde":    "#17743d", "cyan":    "#47b1d5",
    "azul":     "#1754ab", "azul_osc":"#003d6c",
    "naranja":  "#d88c16", "cafe":    "#9b5b1e",
    "salmon":   "#e68878", "gris":    "#2d3142",
}

def sem_color(v):
    if v is None: return C["cafe"]
    if v >= 1.0:  return C["verde"]
    if v >= 0.6:  return C["cyan"]
    if v >= 0.3:  return C["naranja"]
    return C["salmon"]

def sem_label(v):
    if v is None: return "Sin dato"
    if v >= 1.0:  return "Superior"
    if v >= 0.6:  return "Alto"
    if v >= 0.3:  return "Medio"
    return "Minimo"

VIGENCIAS = ["2024","2025","2026"]

# ──────────────────────────────────────────────────────────────────
# URLs GITHUB - todos los archivos fijos
# ──────────────────────────────────────────────────────────────────
GH = {
    "pi":  "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/Plan%20Indicativo%202024-2027.xlsx",
    "h24": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20A%20DICIEMBRE%2031%20DEL%202024%20ENERO%2010%202025.xlsx",
    "r24": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/INFORME%20FINANCIERO%20REGALIAS%20A%2031%20DE%20DICIEMBRE%20DE%202024.xlsx",
    "h25": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20ENERO%20A%20DICIEMBRE%202025.xlsx",
    "r25": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/PAGOS%20REGALIAS%20ENERO%20-%20DICIEMBRE%202025.xlsx",
    "h26": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20HACIENDA%20PRUEBA%202026.xlsx",
    "r26": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/CG-cttos_04_marzo_20260304.xlsx",
}

# ──────────────────────────────────────────────────────────────────
# NOMBRES DE COLUMNA EXACTOS (con tildes, del notebook)
# ──────────────────────────────────────────────────────────────────
CL   = "L\u00ednea Estrat\u00e9gica"          # Línea Estratégica
CPAC = "PORCENTAJE DE EJECUCI\u00d3N ACUMULADA"
CCLA = "CLASIFICACI\u00d3N RECURSOS"

def cMeta(y): return f"Meta F\u00edsica Esperada {y}"
def cPct(y):  return f"PORCENTAJE DE EJECUCI\u00d3N {y}"
def cCat(y):  return f"CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA {y}"
def cPF(y):   return f"Programaci\u00f3n Financiera {y}"
def cEF(y):   return f"Ejecuci\u00f3n Financiera {y}"

COLS_PI = [
    "Codigo Meta", CL, "Sector PDD", "Numero Programa PDD", "Programa PDD",
    "Meta de cuatrenio", "Tipo de Acumulaci\u00f3n", "Responsable",
    cMeta("2024"), cMeta("2025"), cMeta("2026"), cMeta("2027"),
    "PROYECTOS 2024","PROYECTOS 2025","PROYECTOS/GESTIONES PROGRAMADAS 2026","PROYECTOS 2026","PROYECTOS 2027",
    "EJECUCI\u00d3N 2024", cPct("2024"), cCat("2024"),
    "EJECUCI\u00d3N 2025", cPct("2025"), cCat("2025"),
    "EJECUCI\u00d3N 2026", cPct("2026"), cCat("2026"),
    "EJECUCI\u00d3N ACUMULADA", CPAC, "CATEGOR\u00cdA DE EJECUCI\u00d3N ACUMULADA",
]

# programación ... con tildes, en lowercase
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

# ──────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard PDD", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;color:{C['gris']};}}

.main-header{{background:linear-gradient(135deg,{C['azul_osc']} 0%,{C['azul']} 60%,{C['cyan']} 100%);
  padding:2.2rem 3rem 1.8rem;border-radius:0 0 2rem 2rem;margin:-1rem -1rem 2rem -1rem;color:white;}}
.main-header h1{{font-family:'Sora',sans-serif;font-weight:700;font-size:2rem;margin:0;letter-spacing:-.5px;}}
.main-header p{{margin:.3rem 0 0;font-size:.9rem;opacity:.82;}}

.kpi-card{{background:white;border-radius:.9rem;padding:1.2rem 1.5rem;box-shadow:0 2px 12px rgba(0,0,0,.07);
  border-left:5px solid {C['azul']};margin-bottom:.8rem;}}
.kpi-card.v{{border-left-color:{C['verde']};}} .kpi-card.c{{border-left-color:{C['cyan']};}}
.kpi-card.n{{border-left-color:{C['naranja']};}} .kpi-card.ca{{border-left-color:{C['cafe']};}}
.kpi-value{{font-family:'Sora',sans-serif;font-size:2rem;font-weight:700;line-height:1.1;}}
.kpi-label{{font-size:.78rem;text-transform:uppercase;letter-spacing:.8px;color:#6b7280;margin-top:.25rem;}}
.kpi-tip{{font-size:.72rem;color:#9ca3af;margin-top:.45rem;border-top:1px solid #f3f4f6;padding-top:.4rem;}}

.sec-title{{font-family:'Sora',sans-serif;font-size:1.05rem;font-weight:600;color:{C['azul_osc']};
  border-bottom:2px solid {C['cyan']};padding-bottom:.35rem;margin:1.8rem 0 .9rem;}}

/* Sidebar: fondo oscuro con texto visible */
section[data-testid="stSidebar"]{{background:{C['azul_osc']};}}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4{{color:white!important;}}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{{color:{C['cyan']}!important;font-family:'Sora',sans-serif;}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio div{{color:#cbd5e1!important;font-size:.8rem;}}
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div{{background:#1e3a5f;border-color:#2d5a8e;color:white;}}

.err-box{{background:#fff7f0;border:1.5px solid {C['salmon']};border-radius:.8rem;padding:1.1rem 1.4rem;margin:.9rem 0;}}
.err-box h4{{color:#c0392b;margin:0 0 .5rem;font-family:'Sora',sans-serif;}}
.sch-tbl{{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:.7rem;}}
.sch-tbl th{{background:{C['azul_osc']};color:white;padding:.45rem .75rem;text-align:left;}}
.sch-tbl td{{padding:.35rem .75rem;border-bottom:1px solid #e5e7eb;}}
.sch-tbl tr:nth-child(even) td{{background:#f9fafb;}}

.dash-table{{width:100%;border-collapse:collapse;font-size:.82rem;}}
.dash-table thead th{{background:{C['azul_osc']};color:white;padding:.5rem .9rem;text-align:left;
  font-family:'Sora',sans-serif;font-size:.78rem;position:sticky;top:0;z-index:1;cursor:help;}}
.dash-table tbody tr:hover td{{background:#f0f7ff;}}
.dash-table td{{padding:.45rem .9rem;border-bottom:1px solid #e5e7eb;vertical-align:middle;}}
.dash-table tbody tr:nth-child(even) td{{background:#f9fafb;}}
.pill{{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.73rem;font-weight:600;white-space:nowrap;}}

.upload-zone{{background:#f8fafc;border:2px dashed {C['cyan']};border-radius:1rem;
  padding:1.4rem;margin:.5rem 0 1rem;text-align:center;color:#6b7280;}}
hr.sep{{border:none;border-top:1px solid #e5e7eb;margin:1.4rem 0;}}
.footer{{text-align:center;font-size:.75rem;color:#9ca3af;margin-top:2.5rem;padding-top:.8rem;border-top:1px solid #e5e7eb;}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# HELPERS UI
# ──────────────────────────────────────────────────────────────────
def fmt_pct(v): return "N/A" if v is None else f"{v*100:.1f}%"
def fmt_cop(v):
    try:
        f = float(v)
        if abs(f) >= 1e9: return f"${f/1e9:.1f}B"
        if abs(f) >= 1e6: return f"${f/1e6:.1f}M"
        return f"${f:,.0f}"
    except: return str(v)

def pill(lbl, color):
    return f'<span class="pill" style="background:{color}22;color:{color};border:1px solid {color}">{lbl}</span>'

def kpi_card(label, value, cls="", tip=""):
    t = f'<div class="kpi-tip">Como se calcula: {tip}</div>' if tip else ""
    st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-value">{value}</div>'
                f'<div class="kpi-label">{label}</div>{t}</div>', unsafe_allow_html=True)

def sec(text):
    st.markdown(f'<div class="sec-title">{text}</div>', unsafe_allow_html=True)

def htable(df: pd.DataFrame, col_pct=None, col_money=None, tooltips=None):
    """
    Tabla HTML con semaforización integrada en columnas de porcentaje.
    col_pct: columnas float 0-1 → pill+valor en misma celda.
    col_money: columnas numéricas → formato $ millones.
    tooltips: dict {col: texto} → aparece al hacer hover sobre el encabezado.
    """
    col_pct   = col_pct   or []
    col_money = col_money or []
    tooltips  = tooltips  or {}

    ths = ""
    for c in df.columns:
        tip = tooltips.get(c, "")
        ths += f'<th title="{tip}">{c}</th>'

    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for c in df.columns:
            v = row[c]
            if c in col_pct and pd.notna(v):
                try:
                    raw = float(v)
                    if raw > 1.5: raw /= 100.0
                except: raw = 0.0
                clr = sem_color(raw); lbl = sem_label(raw)
                cells += (f'<td style="white-space:nowrap">{pill(lbl,clr)}'
                          f'<span style="margin-left:6px">{fmt_pct(raw)}</span></td>')
            elif c in col_money and pd.notna(v):
                try: cells += f'<td style="text-align:right">{fmt_cop(float(v))}</td>'
                except: cells += f"<td>{v}</td>"
            else:
                cells += f"<td>{v if pd.notna(v) else ''}</td>"
        rows += f"<tr>{cells}</tr>"

    return (f'<div style="overflow-x:auto;max-height:450px;overflow-y:auto">'
            f'<table class="dash-table"><thead><tr>{ths}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')

def show_err(name, schema, table=""):
    tnote = f'<p style="margin:0 0 .5rem;font-size:.83rem"><b>Tabla Excel:</b> <code>{table}</code></p>' if table else ""
    rows  = "".join(f"<tr><td><code>{r['col']}</code></td><td>{r['tipo']}</td><td>{r['ej']}</td></tr>" for r in schema)
    st.markdown(f"""<div class="err-box"><h4>Error al leer {name}</h4>
    <p>Verifica que el archivo contenga estas columnas:</p>{tnote}
    <table class="sch-tbl"><thead><tr><th>Columna</th><th>Tipo</th><th>Ejemplo</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <p style="margin-top:.7rem;font-size:.79rem;color:#6b7280"><b>Tip:</b>
    El archivo debe tener una tabla Excel nombrada exactamente como se indica. Las tildes importan.</p>
    </div>""", unsafe_allow_html=True)

SCHEMAS = {
    "Plan Indicativo": ("tblPlanIndicativo_2", [
        {"col":"Codigo Meta","tipo":"Texto","ej":"MT-ED-0001"},
        {"col":"L\u00ednea Estrat\u00e9gica","tipo":"Texto","ej":"Linea 1 - Bienestar"},
        {"col":"Sector PDD","tipo":"Texto","ej":"Educacion"},
        {"col":"Programa PDD","tipo":"Texto","ej":"1.1 Educacion con calidad"},
        {"col":"Meta F\u00edsica Esperada 2026","tipo":"Numero","ej":"2500"},
        {"col":"PORCENTAJE DE EJECUCI\u00d3N 2026","tipo":"Decimal","ej":"0.92"},
        {"col":"CATEGOR\u00cdA DE EJECUCI\u00d3N F\u00cdSICA 2026","tipo":"Texto","ej":"Superior|Alto|Medio|Minimo"},
        {"col":"Programaci\u00f3n recursos propios icld26","tipo":"Numero","ej":"500000000"},
        {"col":"Programaci\u00f3n regal\u00edas26","tipo":"Numero","ej":"200000000"},
    ]),
    "Hacienda 2026": ("EjecucionHacienda2026", [
        {"col":"RP","tipo":"Numero","ej":"120000000"},
        {"col":"CODIGO META","tipo":"Texto","ej":"MT-ED-0001"},
        {"col":"CLASIFICACI\u00d3N RECURSOS","tipo":"Texto","ej":"ICLD"},
        {"col":"PROYECTO ARCHIVADO","tipo":"Texto","ej":"(vacio=activo)"},
        {"col":"SE VA A CARGAR EN PI","tipo":"Texto","ej":"(vacio=aplica)"},
        {"col":"DISTRIBUIR DE FORMA EQUITATIVA","tipo":"Texto","ej":"SI|NO"},
    ]),
    "Regalias 2026": ("Pagos_Regalias_2026", [
        {"col":"PAGO EJECUTADO VALOR","tipo":"Numero","ej":"75000000"},
        {"col":"CODIGO META","tipo":"Texto","ej":"MT-ED-0001"},
        {"col":"CLASIFICACI\u00d3N RECURSOS","tipo":"Texto","ej":"REGALIAS"},
        {"col":"ULTIMA FECHA PAGO","tipo":"Fecha","ej":"2026-03-04"},
    ]),
}

# ──────────────────────────────────────────────────────────────────
# I/O
# ──────────────────────────────────────────────────────────────────
def to_bio(src):
    if isinstance(src,(bytes,bytearray)): return io.BytesIO(src)
    if isinstance(src,io.BytesIO): src.seek(0); return src
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
        r = requests.get(url, timeout=40); r.raise_for_status(); return r.content
    except: return None

# ──────────────────────────────────────────────────────────────────
# PROCESAMIENTO DE ARCHIVOS FINANCIEROS
# ──────────────────────────────────────────────────────────────────
def proc_reg(src, year):
    tbl = {"2024":"EjecucionRegalias","2025":"Pagos_Regalias_2025","2026":"Pagos_Regalias_2026"}
    df  = read_xl(src, tbl[year])
    if df is None: return None
    try:
        df = df.select(pl.all().name.map(lambda x: x.strip().upper().replace("_X0009_","")))
        if year=="2024":
            df = (df.select(["CODIGO META","COMPROMISOS",CCLA.upper()])
                    .with_columns(pl.col("CODIGO META").fill_null(""))
                    .filter(pl.col("CODIGO META")!="", pl.col("CODIGO META").str.starts_with("MT"))
                    .rename({"COMPROMISOS":"RP"}))
        elif year=="2025":
            df = (df.select(["PAGOS REGALIAS","CODIGO META",CCLA.upper()])
                    .rename({"PAGOS REGALIAS":"RP"})
                    .with_columns(pl.col("CODIGO META").fill_null(""))
                    .filter(pl.col("CODIGO META")!=""))
        elif year=="2026":
            df = (df.filter((pl.col("ULTIMA FECHA PAGO")>=pl.date(2026,1,1))&
                            (pl.col("ULTIMA FECHA PAGO")<=pl.date(2026,12,31)))
                    .select(["PAGO EJECUTADO VALOR","CODIGO META",CCLA.upper()])
                    .rename({"PAGO EJECUTADO VALOR":"RP"})
                    .with_columns(pl.col("CODIGO META").fill_null(""))
                    .filter(pl.col("CODIGO META")!=""))
        return df.select(["CODIGO META","RP"])
    except: return None

def proc_hac(src, year):
    tbl = {"2024":"EjecucionHaciendaDiciembre","2025":"EjecucionHaciendaDiciembre2025","2026":"EjecucionHacienda2026"}
    df  = read_xl(src, tbl[year])
    if df is None: return None
    try:
        if year=="2024":
            df = (df.select(["RP","CODIGO META",CCLA])
                    .with_columns(pl.col("CODIGO META",CCLA).fill_null(""))
                    .filter(pl.col("CODIGO META")!="", pl.col(CCLA)!=""))
        else:
            df = (df.with_columns(
                      pl.col("PROYECTO ARCHIVADO","CODIGO META",CCLA,"SE VA A CARGAR EN PI").fill_null(""),
                      pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA")=="SI")
                        .then(pl.col("RP")/2).otherwise(pl.col("RP")))
                    .filter(pl.col("PROYECTO ARCHIVADO")=="", pl.col("CODIGO META")!="",
                            pl.col(CCLA)!="", pl.col("SE VA A CARGAR EN PI")==""))
        return df.select(["CODIGO META","RP"])
    except: return None

def merge_ef(reg, hac, name):
    frames = [f for f in [reg,hac] if f is not None and not f.is_empty()]
    if not frames:
        return pl.DataFrame({"CODIGO META":pl.Series([],dtype=pl.Utf8), name:pl.Series([],dtype=pl.Float64)})
    return pl.concat(frames,how="diagonal").group_by("CODIGO META").agg(pl.col("RP").sum().alias(name))

# ──────────────────────────────────────────────────────────────────
# CARGA PRINCIPAL
# ──────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_all(pi_b, h24_b, r24_b, h25_b, r25_b, h26_b, r26_b):
    pi = read_xl(pi_b, "tblPlanIndicativo_2")
    if pi is None: return None, True

    ol  = read_xl(pi_b, "orden_lineas")
    os_ = read_xl(pi_b, "orden_sectores")
    op  = read_xl(pi_b, "orden_programas")
    hom = read_xl(pi_b, "HomologacionSecretarias")

    # Columnas físicas
    avail  = [c for c in COLS_PI if c in pi.columns]
    fisicas = pi.select(avail)

    # Programación financiera (lowercase)
    pi_low = pi.select(pl.all().name.map(lambda x: x.strip().lower()))
    exprs  = [pl.col("codigo meta")]
    for suf,yr in [("24","2024"),("25","2025"),("26","2026"),("27","2027")]:
        exist = [c for c in PROG_COLS[suf] if c in pi_low.columns]
        if exist:
            e = pl.col(exist[0]).cast(pl.Float64)
            for c in exist[1:]: e = e + pl.col(c).cast(pl.Float64)
        else:
            e = pl.lit(0.0)
        exprs.append(e.alias(cPF(yr)))
    prog = pi_low.select(exprs)

    # Ejecuciones financieras
    ef24 = merge_ef(proc_reg(r24_b,"2024"), proc_hac(h24_b,"2024"), cEF("2024"))
    ef25 = merge_ef(proc_reg(r25_b,"2025"), proc_hac(h25_b,"2025"), cEF("2025"))
    ef26 = merge_ef(proc_reg(r26_b,"2026"), proc_hac(h26_b,"2026"), cEF("2026"))

    prog = (prog.join(ef24,left_on="codigo meta",right_on="CODIGO META",how="left")
               .join(ef25,left_on="codigo meta",right_on="CODIGO META",how="left")
               .join(ef26,left_on="codigo meta",right_on="CODIGO META",how="left")
               .with_columns(pl.col(cEF("2024"),cEF("2025"),cEF("2026")).fill_null(0)))

    pff = fisicas.join(prog, left_on="Codigo Meta", right_on="codigo meta", how="left")
    mc  = [cMeta(y) for y in ["2024","2025","2026","2027"] if cMeta(y) in pff.columns]
    if mc: pff = pff.with_columns([pl.col(c).fill_null(0) for c in mc])

    return {"pff":pff,"ol":ol,"os":os_,"op":op,"hom":hom}, False

# ──────────────────────────────────────────────────────────────────
# GAUGE
# ──────────────────────────────────────────────────────────────────
def gauge(val, title, color):
    dv = min(val*100, 120)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=dv,
        number={"suffix":"%","font":{"size":28,"color":color,"family":"Sora"},"valueformat":".1f"},
        title={"text":title,"font":{"size":12,"color":"#6b7280"}},
        gauge={"axis":{"range":[0,120],"tickvals":[0,29,59,99,120],
                       "ticktext":["0%","29%","59%","99%","≥100%"],"tickfont":{"size":9}},
               "bar":{"color":color,"thickness":.28},"bgcolor":"#f3f4f6","borderwidth":0,
               "steps":[{"range":[0,29],"color":"#fee2e2"},{"range":[29,59],"color":"#fef3c7"},
                        {"range":[59,99],"color":"#dbeafe"},{"range":[99,120],"color":"#d1fae5"}],
               "threshold":{"line":{"color":"#374151","width":2},"thickness":.75,"value":dv}}))
    fig.update_layout(height=210, margin=dict(t=40,b=5,l=15,r=15), paper_bgcolor="white")
    return fig

# ──────────────────────────────────────────────────────────────────
# CALCULOS DEL NOTEBOOK (fielmente replicados)
# ──────────────────────────────────────────────────────────────────
def calc_ponderados(pf, vig):
    """
    Replica ponderado_vigencia y ponderado_cuatrienio del notebook.
    Retorna (pond_vig_df, pond_cuat_df, n_prog, n_total)
    """
    CM = cMeta(vig); CP = cPct(vig)
    n_total = len(pf)
    n_prog  = int(pf.filter(pl.col(CM).fill_null(0)!=0).height) if CM in pf.columns else 0

    if n_prog == 0 or CP not in pf.columns:
        return None, None, n_prog, n_total

    # promedio por programa (solo metas programadas)
    prom_prog = (
        pf.filter(pl.col(CM).fill_null(0)!=0)
          .group_by("Programa PDD")
          .agg(pl.col(CP).fill_null(0).mean().alias("Promedio de avance de ejecucion de la vigencia"))
    )

    # ponderado_vigencia
    pond_vig = (
        pf.with_columns(
            pl.when(pl.col(CM)!=0).then(1).otherwise(0).alias("mp"))
          .group_by([CL,"Sector PDD","Programa PDD"])
          .agg(pl.col("mp").sum().alias("Total Indicadores de Producto Programados"))
          .with_columns((pl.col("Total Indicadores de Producto Programados")/n_prog)
                        .alias("Sobre Numero Total de Metas Programadas"))
          .join(prom_prog, on="Programa PDD", how="left")
          .with_columns(pl.col("Promedio de avance de ejecucion de la vigencia").fill_null(0))
    )

    # ponderado_cuatrienio
    n_metas_prog = (
        pf.group_by("Programa PDD")
          .agg(pl.col("Codigo Meta").len().alias("Total Indicadores de Producto"))
    )
    pond_cuat = (
        pf.group_by([CL,"Sector PDD","Programa PDD"])
          .agg(pl.col(CPAC).fill_null(0).mean().alias("Promedio de avance de ejecucion acumulada"))
          .join(n_metas_prog, on="Programa PDD")
          .with_columns((pl.col("Total Indicadores de Producto")/n_total)
                        .alias("Sobre Numero Total de Metas"))
    )
    return pond_vig, pond_cuat, n_prog, n_total

def eficacia_grupo(pond_vig, pond_cuat, n_prog, n_total, group_col, es_vigencia=True):
    """
    Replica avance_vigencia_lineas / avance_cuatrienio_lineas del notebook.
    Retorna DataFrame pandas con: group_col, % Avance de la Ejecucion Fisica
    """
    if es_vigencia and pond_vig is not None:
        # cuenta metas programadas por grupo
        n_grupo = (
            pond_vig.group_by(group_col)
                    .agg(pl.col("Total Indicadores de Producto Programados").sum()
                           .alias("Total Indicadores de Producto con Programacion"))
        )
        df = (
            pond_vig.group_by(group_col)
                    .agg((pl.col("Promedio de avance de ejecucion de la vigencia")
                          *pl.col("Sobre Numero Total de Metas Programadas")).sum()
                          .alias("Aporte"))
                    .join(n_grupo, on=group_col)
                    .with_columns(
                        (pl.col("Total Indicadores de Producto con Programacion")/n_prog)
                          .alias("Peso"),
                        pl.when(
                            (pl.col("Total Indicadores de Producto con Programacion")/n_prog)==0)
                          .then(0.0)
                          .otherwise(pl.col("Aporte")/
                                     (pl.col("Total Indicadores de Producto con Programacion")/n_prog))
                          .alias("% Avance de la Ejecucion Fisica")
                    )
                    .sort("% Avance de la Ejecucion Fisica", descending=False)
                    .to_pandas()[[group_col,"% Avance de la Ejecucion Fisica"]]
        )
    else:
        # cuatrienio
        if group_col == CL:
            n_grupo = (
                pond_cuat.group_by(group_col)
                         .agg(pl.col("Total Indicadores de Producto").sum())
            )
        else:
            n_grupo = (
                pond_cuat.group_by(group_col)
                         .agg(pl.col("Total Indicadores de Producto").sum())
            )
        df = (
            pond_cuat.group_by(group_col)
                     .agg((pl.col("Promedio de avance de ejecucion acumulada")
                           *pl.col("Sobre Numero Total de Metas")).sum()
                           .alias("Aporte"))
                     .join(n_grupo, on=group_col)
                     .with_columns(
                         (pl.col("Total Indicadores de Producto")/n_total).alias("Peso"),
                         pl.when((pl.col("Total Indicadores de Producto")/n_total)==0)
                           .then(0.0)
                           .otherwise(pl.col("Aporte")/
                                      (pl.col("Total Indicadores de Producto")/n_total))
                           .alias("% Avance de la Ejecucion Fisica")
                     )
                     .sort("% Avance de la Ejecucion Fisica", descending=False)
                     .to_pandas()[[group_col,"% Avance de la Ejecucion Fisica"]]
        )
    return df

def barra_horizontal(df, x_col, y_col, titulo, key):
    vals = df[x_col].tolist()
    fig = go.Figure(go.Bar(
        x=[v*100 for v in vals], y=df[y_col].tolist(), orientation="h",
        marker_color=[sem_color(v) for v in vals],
        text=[fmt_pct(v) for v in vals], textposition="outside",
        hovertemplate=f"<b>%{{y}}</b><br>{x_col}: %{{text}}<extra></extra>",
    ))
    fig.update_layout(
        title=titulo, xaxis_title="% Avance", xaxis_range=[0,130],
        height=max(300, len(df)*52), paper_bgcolor="white", plot_bgcolor="#fafafa",
        font={"family":"DM Sans"}, margin=dict(l=20,r=110,t=40,b=20),
    )
    st.plotly_chart(fig, width="stretch", key=key)

def barra_financiera(df, ejec_col, prog_col, pct_col, y_col, titulo, key):
    vals = df[pct_col].tolist()
    fig = go.Figure(go.Bar(
        x=df[ejec_col].tolist(), y=df[y_col].tolist(), orientation="h",
        marker_color=[sem_color(v) for v in vals],
        text=[fmt_pct(v) for v in vals], textposition="outside",
        customdata=df[[prog_col,ejec_col]].values,
        hovertemplate=("<b>%{y}</b><br>Programacion: $%{customdata[0]:,.0f}<br>"
                       "Ejecucion: $%{customdata[1]:,.0f}<br>Avance: %{text}<extra></extra>"),
    ))
    fig.update_layout(
        title=titulo, xaxis_title="Ejecucion ($)",
        height=max(300, len(df)*52), paper_bgcolor="white", plot_bgcolor="#fafafa",
        font={"family":"DM Sans"}, margin=dict(l=20,r=110,t=40,b=20),
    )
    st.plotly_chart(fig, width="stretch", key=key)

# ──────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Dashboard PDD")
    st.markdown("#### Reporte de Avance 2024-2027")
    st.markdown("---")
    st.markdown("### Fuente de datos")
    modo = st.radio("Origen de archivos:", ["GitHub (todos)", "Subir manualmente"], index=0)
    st.markdown("---")
    st.markdown("### Filtros")
    vig = st.selectbox("Vigencia:", VIGENCIAS, index=2)
    modo_periodo = st.radio("Ver avance de:", ["Vigencia seleccionada", "Cuatrienio acumulado"], index=0)
    es_vig = modo_periodo == "Vigencia seleccionada"
    ph_lin = st.empty()
    ph_sec = st.empty()
    ph_res = st.empty()
    st.markdown("---")
    st.markdown('<div style="font-size:.73rem;color:#94a3b8;line-height:1.6">'
                'Semaforización: Superior ≥100% | Alto 60-99%<br>'
                'Medio 30-59% | Minimo 0-29%</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────
periodo_label = f"Vigencia {vig}" if es_vig else "Cuatrienio 2024-2027"
st.markdown(f"""
<div class="main-header">
  <h1>Reporte de Avance del Plan de Desarrollo</h1>
  <p>Ejecucion Fisica y Financiera &middot; <strong>{periodo_label}</strong> &middot; Cuatrienio 2024&ndash;2027</p>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# CARGA DE ARCHIVOS
# ──────────────────────────────────────────────────────────────────
pi_b=h24_b=r24_b=h25_b=r25_b=h26_b=r26_b=None

if modo == "GitHub (todos)":
    st.info("Todos los archivos se cargan automaticamente desde GitHub. No necesitas subir nada.")
    with st.spinner("Descargando archivos desde GitHub..."):
        pi_b  = fetch(GH["pi"])
        h24_b = fetch(GH["h24"]); r24_b = fetch(GH["r24"])
        h25_b = fetch(GH["h25"]); r25_b = fetch(GH["r25"])
        h26_b = fetch(GH["h26"]); r26_b = fetch(GH["r26"])
    failed = [k for k,b in {"Plan Indicativo":pi_b,"Hacienda 2024":h24_b,"Regalias 2024":r24_b,
                              "Hacienda 2025":h25_b,"Regalias 2025":r25_b,
                              "Hacienda 2026":h26_b,"Regalias 2026":r26_b}.items() if b is None]
    if failed:
        st.warning(f"No se pudieron descargar: {', '.join(failed)}")
    if pi_b is None:
        st.error("No se pudo cargar el Plan Indicativo desde GitHub. Cambia a modo manual.")
        st.stop()

else:
    st.markdown("### Carga de Archivos")
    with st.expander("Vigencias cerradas 2024-2025 (opcionales si usas GitHub)", expanded=False):
        c1,c2 = st.columns(2)
        with c1:
            pi_f  = st.file_uploader("Plan Indicativo",  type=["xlsx"], key="pi")
            h24_f = st.file_uploader("Hacienda 2024",    type=["xlsx"], key="h24")
            r24_f = st.file_uploader("Regalias 2024",    type=["xlsx"], key="r24")
        with c2:
            h25_f = st.file_uploader("Hacienda 2025",    type=["xlsx"], key="h25")
            r25_f = st.file_uploader("Regalias 2025",    type=["xlsx"], key="r25")
        pi_b  = pi_f.read()  if pi_f  else None
        h24_b = h24_f.read() if h24_f else None
        r24_b = r24_f.read() if r24_f else None
        h25_b = h25_f.read() if h25_f else None
        r25_b = r25_f.read() if r25_f else None

    with st.expander("Vigencia actual 2026", expanded=True):
        c1,c2 = st.columns(2)
        with c1:
            h26_f = st.file_uploader("Hacienda 2026",    type=["xlsx"], key="h26")
        with c2:
            r26_f = st.file_uploader("Regalias 2026",    type=["xlsx"], key="r26")
        h26_b = h26_f.read() if h26_f else None
        r26_b = r26_f.read() if r26_f else None

    # Si no subió PI, descargar de GitHub como fallback
    if not pi_b:
        with st.spinner("Descargando Plan Indicativo desde GitHub..."):
            pi_b = fetch(GH["pi"])
        if not pi_b:
            st.markdown('<div class="upload-zone">Carga el <b>Plan Indicativo</b> para comenzar.</div>',
                        unsafe_allow_html=True)
            st.stop()
    # Misma lógica para 2024-2025 si no los subió
    if not h24_b: h24_b = fetch(GH["h24"])
    if not r24_b: r24_b = fetch(GH["r24"])
    if not h25_b: h25_b = fetch(GH["h25"])
    if not r25_b: r25_b = fetch(GH["r25"])

# ──────────────────────────────────────────────────────────────────
# PROCESAMIENTO
# ──────────────────────────────────────────────────────────────────
with st.spinner("Procesando datos..."):
    res, err = load_all(pi_b, h24_b, r24_b, h25_b, r25_b, h26_b, r26_b)

if err:
    show_err("Plan Indicativo", SCHEMAS["Plan Indicativo"][1], SCHEMAS["Plan Indicativo"][0])
    st.stop()

pff=res["pff"]; ol=res["ol"]; os_=res["os"]; op=res["op"]; hom=res["hom"]

# Columnas activas
CM=cMeta(vig); CP=cPct(vig); CCA=cCat(vig); CEF=cEF(vig); CPF=cPF(vig)
cL = CL if CL in pff.columns else "Linea Estrategica"

# Calculos ponderados (usados en Tab 3)
pond_vig, pond_cuat, n_prog, n_total = calc_ponderados(pff, vig)

# Filtros
lo = sorted(pff[cL].drop_nulls().unique().to_list()) if cL in pff.columns else []
so = sorted(pff["Sector PDD"].drop_nulls().unique().to_list()) if "Sector PDD" in pff.columns else []
ro = sorted(pff["Responsable"].drop_nulls().unique().to_list()) if "Responsable" in pff.columns else []
with ph_lin: fl = st.multiselect("Linea:", lo, placeholder="Todas las lineas")
with ph_sec: fs = st.multiselect("Sector:", so, placeholder="Todos los sectores")
with ph_res: fr = st.multiselect("Dependencia:", ro, placeholder="Todas")

pf = pff.clone()
if fl and cL in pf.columns:          pf = pf.filter(pl.col(cL).is_in(fl))
if fs and "Sector PDD" in pf.columns: pf = pf.filter(pl.col("Sector PDD").is_in(fs))
if fr and "Responsable" in pf.columns: pf = pf.filter(pl.col("Responsable").is_in(fr))

# Recalcular con filtro aplicado
pond_vig_f, pond_cuat_f, n_prog_f, n_total_f = calc_ponderados(pf, vig)

# KPIs globales
n_sup = 0
if CCA in pf.columns and CM in pf.columns:
    n_sup = int(pf.filter(pl.col(CM).fill_null(0)!=0).filter(pl.col(CCA)=="Superior").height)

ejec_fin=0.0; prog_fin=0.0; pct_fin=0.0
if CEF in pf.columns: ejec_fin = float(pf.select(pl.col(CEF).sum()).item() or 0)
if CPF in pf.columns: prog_fin = float(pf.select(pl.col(CPF).sum()).item() or 0)
if prog_fin > 0: pct_fin = ejec_fin/prog_fin

avance_ponderado = 0.0
if pond_vig_f is not None and n_prog_f > 0:
    avance_ponderado = float(
        pond_vig_f.select(
            (pl.col("Promedio de avance de ejecucion de la vigencia")
             *pl.col("Sobre Numero Total de Metas Programadas")).sum()
        ).item() or 0)

avance_ponderado_acum = 0.0
if pond_cuat_f is not None:
    avance_ponderado_acum = float(
        pond_cuat_f.select(
            (pl.col("Promedio de avance de ejecucion acumulada")
             *pl.col("Sobre Numero Total de Metas")).sum()
        ).item() or 0)

avance_display = avance_ponderado if es_vig else avance_ponderado_acum

# Distribucion de metas (notebook: distribucion_metas_pdd)
meta_cuat = float(pf.select(pl.col("Meta de cuatrenio").fill_null(0).sum()).item() or 0) \
    if "Meta de cuatrenio" in pf.columns else 0
dist = {}
for y in ["2024","2025","2026","2027"]:
    mc = cMeta(y)
    dist[y] = float(pf.select(pl.col(mc).fill_null(0).sum()).item() or 0)/meta_cuat \
        if mc in pf.columns and meta_cuat>0 else 0.0

# ──────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4 = st.tabs(["Resumen General","Ejecucion Financiera","Ejecucion Fisica","Por Dependencia"])

# ================================================================
# TAB 1: RESUMEN GENERAL
# ================================================================
with tab1:
    sec(f"Indicadores Clave - {periodo_label}")
    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: kpi_card("Metas Totales", str(n_total_f), "",
        "Total de indicadores de producto del PDD con los filtros aplicados.")
    with k2: kpi_card(f"Metas Programadas {vig}", str(n_prog_f), "c",
        f"Indicadores con Meta Fisica Esperada {vig} mayor a cero.")
    with k3: kpi_card(f"Avance Ponderado {vig}", fmt_pct(avance_ponderado), "v",
        f"Suma de (peso_programa) x (promedio_avance_programa) donde peso = metas_prog_programa / total_metas_prog_vigencia.")
    with k4: kpi_card("Avance Ponderado Cuatrienio", fmt_pct(avance_ponderado_acum), "n",
        "Suma de (peso_programa) x (promedio_avance_acumulado_programa) donde peso = metas_programa / total_metas.")
    with k5: kpi_card(f"Metas Superiores {vig}", str(n_sup), "ca",
        f"Metas cuya CATEGORIA DE EJECUCION FISICA {vig} es 'Superior' (ejecucion >= 100%).")

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    cg1,cg2,cg3 = st.columns(3)
    with cg1: st.plotly_chart(gauge(avance_ponderado,f"Avance Ponderado {vig}",sem_color(avance_ponderado)), width="stretch", key="g1")
    with cg2: st.plotly_chart(gauge(avance_ponderado_acum,"Avance Ponderado Cuatrienio",sem_color(avance_ponderado_acum)), width="stretch", key="g2")
    with cg3: st.plotly_chart(gauge(pct_fin,f"Ejecucion Financiera {vig}",sem_color(pct_fin)), width="stretch", key="g3")

    # Distribución de metas (notebook: distribucion_metas_pdd)
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    sec("Distribucion de la Meta Fisica del Cuatrienio por Vigencia")
    dc1,dc2 = st.columns([1.4,1])
    with dc1:
        fig_d = go.Figure(go.Bar(
            x=list(dist.keys()), y=[v*100 for v in dist.values()],
            marker_color=[sem_color(v) for v in dist.values()],
            text=[fmt_pct(v) for v in dist.values()], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Distribucion: %{y:.1f}%<extra></extra>",
        ))
        fig_d.update_layout(
            yaxis_title="% sobre Meta Cuatrienal",
            yaxis_range=[0, max(v*100 for v in dist.values())*1.25+5] if any(dist.values()) else [0,30],
            height=300, paper_bgcolor="white", plot_bgcolor="#fafafa",
            font={"family":"DM Sans"}, margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_d, width="stretch", key="dist_bar")
    with dc2:
        st.markdown("**Como se calcula:**")
        st.markdown("Suma(Meta Fisica Esperada año) / Suma(Meta de cuatrenio). "
                    "Muestra que fraccion de la meta total del cuatrienio se programo para cada vigencia.")
        st.markdown("")
        st.markdown("**Semaforización institucional:**")
        for lbl,rango in [("Superior","≥ 100%"),("Alto","60–99%"),("Medio","30–59%"),("Minimo","< 30%")]:
            clr = {"Superior":C["verde"],"Alto":C["cyan"],"Medio":C["naranja"],"Minimo":C["salmon"]}[lbl]
            st.markdown(f'{pill(lbl,clr)} &nbsp; {rango}', unsafe_allow_html=True)
            st.write("")

    # Distribución por categoría de ejecución
    if CCA in pf.columns and CM in pf.columns:
        sec(f"Semaforización de Metas - {vig}")
        cat_df = (pf.filter(pl.col(CM).fill_null(0)!=0)
                    .group_by(CCA).agg(pl.col("Codigo Meta").len().alias("n"))
                    .drop_nulls().to_pandas())
        if not cat_df.empty:
            total_prog = cat_df["n"].sum()
            p1,p2 = st.columns([1.2,1])
            with p1:
                fig_pie = go.Figure(go.Pie(
                    labels=cat_df[CCA], values=cat_df["n"],
                    marker_colors=[sem_color({"Superior":1.0,"Alto":0.7,"Medio":0.4,"Minimo":0.1}.get(l,0))
                                   for l in cat_df[CCA]],
                    hole=.44, textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>%{value} metas<br>%{percent}<extra></extra>",
                ))
                fig_pie.update_layout(title=f"Categorias de ejecucion {vig}", height=330,
                    paper_bgcolor="white", font={"family":"DM Sans"}, margin=dict(t=50,b=5,l=5,r=5))
                st.plotly_chart(fig_pie, width="stretch", key="pie_cat")
            with p2:
                sem_map = {"Superior":1.0,"Alto":0.7,"Medio":0.4,"Minimo":0.1}
                cat_show = cat_df.copy()
                cat_show["Semaforo_val"] = cat_show[CCA].map(sem_map).fillna(0)
                cat_show["% del total"] = (cat_show["n"]/total_prog*100).round(1).astype(str)+"%"
                cat_show = cat_show[["Semaforo_val","n","% del total"]].copy()
                cat_show.columns = ["Categoria","Metas","% del total"]
                st.markdown(htable(cat_show, col_pct=["Categoria"],
                    tooltips={"Categoria":"Semaforización: Superior ≥100% | Alto 60-99% | Medio 30-59% | Minimo <30%",
                              "% del total":"Sobre metas con programacion en la vigencia."}),
                    unsafe_allow_html=True)

# ================================================================
# TAB 2: EJECUCION FINANCIERA
# ================================================================
with tab2:
    # Sub-tabs: vigencia vs cuatrienio
    ft1,ft2 = st.tabs([f"Vigencia {vig}", "Cuatrienio Acumulado"])

    # ── VIGENCIA ──────────────────────────────────────────────
    with ft1:
        if CEF not in pf.columns or CPF not in pf.columns:
            st.info(f"No hay datos financieros para {vig}. Verifica que los archivos de hacienda y regalias esten cargados.")
        else:
            def fin_lineas_vig(pf_src, vig_sel):
                CPF_ = cPF(vig_sel); CEF_ = cEF(vig_sel)
                if CPF_ not in pf_src.columns or CEF_ not in pf_src.columns: return pd.DataFrame()
                ord_c = "Orden Linea" if ol is not None and "Orden Linea" in ol.columns else None
                jc    = cL if ol is not None and cL in ol.columns else (ol.columns[0] if ol is not None else None)
                q = (pf_src.group_by(cL).agg(pl.col(CPF_).sum(), pl.col(CEF_).sum())
                           .with_columns(pl.when(pl.col(CPF_)==0).then(0.0)
                                           .otherwise(pl.col(CEF_)/pl.col(CPF_)).alias("Pct")))
                if ol is not None and jc:
                    q = q.join(ol, left_on=cL, right_on=jc, how="left")
                    if ord_c: q = q.sort(ord_c)
                return q.to_pandas()

            def fin_sectores_vig(pf_src, vig_sel):
                CPF_ = cPF(vig_sel); CEF_ = cEF(vig_sel)
                if CPF_ not in pf_src.columns or CEF_ not in pf_src.columns: return pd.DataFrame()
                ord_c = "Orden Sector" if os_ is not None and "Orden Sector" in os_.columns else None
                q = (pf_src.group_by("Sector PDD").agg(pl.col(CPF_).sum(), pl.col(CEF_).sum())
                           .with_columns(pl.when(pl.col(CPF_)==0).then(0.0)
                                           .otherwise(pl.col(CEF_)/pl.col(CPF_)).alias("Pct")))
                if os_ is not None:
                    q = q.join(os_, on="Sector PDD", how="left")
                    if ord_c: q = q.sort(ord_c)
                return q.to_pandas()

            def fin_programas_vig(pf_src, vig_sel):
                CPF_ = cPF(vig_sel); CEF_ = cEF(vig_sel)
                if CPF_ not in pf_src.columns or CEF_ not in pf_src.columns: return pd.DataFrame()
                ord_c = "Orden Programa PDD" if op is not None and "Orden Programa PDD" in op.columns else None
                q = (pf_src.group_by("Programa PDD").agg(pl.col(CPF_).sum(), pl.col(CEF_).sum())
                           .with_columns(pl.when(pl.col(CPF_)==0).then(0.0)
                                           .otherwise(pl.col(CEF_)/pl.col(CPF_)).alias("Pct")))
                if op is not None:
                    q = q.join(op, on="Programa PDD", how="left")
                    if ord_c: q = q.sort(ord_c)
                return q.to_pandas()

            # Lineas
            sec(f"Ejecucion Financiera por Linea Estrategica - {vig}")
            lf = fin_lineas_vig(pf, vig)
            if not lf.empty:
                gt1,gt2 = st.tabs(["Grafico","Tabla"])
                with gt1:
                    barra_financiera(lf, CEF, CPF, "Pct", cL, f"Lineas - {vig}", "bfl_v")
                    st.caption("Ejecucion / Programacion de la vigencia. Semaforización institucional aplicada.")
                with gt2:
                    s = lf[[cL,CPF,CEF,"Pct"]].copy(); s.columns=["Linea",f"Prog. {vig}",f"Ejec. {vig}","% Avance"]
                    st.markdown(htable(s,col_pct=["% Avance"],col_money=[f"Prog. {vig}",f"Ejec. {vig}"],
                        tooltips={"% Avance":f"Ejecucion Financiera {vig} / Programacion Financiera {vig}",
                                  f"Prog. {vig}":"Suma ICLD+ICDE+SGP+Regalias+Credito+Cofinanciacion+Otras Fuentes",
                                  f"Ejec. {vig}":"RP Hacienda + Pagos Regalias"}),unsafe_allow_html=True)

            # Sectores
            sec(f"Ejecucion Financiera por Sector PDD - {vig}")
            sf = fin_sectores_vig(pf, vig)
            if not sf.empty:
                gt1,gt2 = st.tabs(["Grafico","Tabla"])
                with gt1:
                    barra_financiera(sf, CEF, CPF, "Pct", "Sector PDD", f"Sectores - {vig}", "bfs_v")
                with gt2:
                    s = sf[["Sector PDD",CPF,CEF,"Pct"]].copy(); s.columns=["Sector",f"Prog. {vig}",f"Ejec. {vig}","% Avance"]
                    st.markdown(htable(s,col_pct=["% Avance"],col_money=[f"Prog. {vig}",f"Ejec. {vig}"]),unsafe_allow_html=True)

            # Programas
            sec(f"Ejecucion Financiera por Programa PDD - {vig}")
            prgf = fin_programas_vig(pf, vig)
            if not prgf.empty:
                gt1,gt2 = st.tabs(["Grafico","Tabla"])
                with gt1:
                    barra_financiera(prgf, CEF, CPF, "Pct", "Programa PDD", f"Programas - {vig}", "bfp_v")
                with gt2:
                    s = prgf[["Programa PDD",CPF,CEF,"Pct"]].copy(); s.columns=["Programa",f"Prog. {vig}",f"Ejec. {vig}","% Avance"]
                    st.markdown(htable(s,col_pct=["% Avance"],col_money=[f"Prog. {vig}",f"Ejec. {vig}"]),unsafe_allow_html=True)

    # ── CUATRIENIO ────────────────────────────────────────────
    with ft2:
        # Ejecucion acumulada por linea (2024+2025+2026)
        yrs_disp = [y for y in ["2024","2025","2026"] if cEF(y) in pf.columns]
        if not yrs_disp:
            st.info("No hay datos financieros acumulados disponibles.")
        else:
            # KPIs acumulados
            ejec_acum = sum(float(pf.select(pl.col(cEF(y)).sum()).item() or 0) for y in yrs_disp)
            prog_cuat = sum(float(pf.select(pl.col(cPF(y)).sum()).item() or 0)
                           for y in ["2024","2025","2026","2027"] if cPF(y) in pf.columns)
            pct_acum  = ejec_acum/prog_cuat if prog_cuat>0 else 0
            ka1,ka2,ka3 = st.columns(3)
            with ka1: kpi_card("Programacion Cuatrienio", fmt_cop(prog_cuat),"","Suma de programacion 2024-2027 de todas las fuentes.")
            with ka2: kpi_card("Ejecucion Acumulada", fmt_cop(ejec_acum),"v","Suma de RP Hacienda + Pagos Regalias 2024-2026.")
            with ka3: kpi_card("% Avance Acumulado", fmt_pct(pct_acum),"c","Ejecucion Acumulada / Programacion Cuatrienio.")

            st.markdown('<hr class="sep">', unsafe_allow_html=True)

            # Comparativo anual programacion vs ejecucion
            sec("Programacion vs Ejecucion por Año")
            ev = [float(pf.select(pl.col(cEF(y)).sum()).item() or 0) for y in yrs_disp]
            pv = [float(pf.select(pl.col(cPF(y)).sum()).item() or 0) if cPF(y) in pf.columns else 0 for y in yrs_disp]
            fig_a = go.Figure()
            fig_a.add_trace(go.Bar(name="Programacion",x=yrs_disp,y=pv,marker_color=C["cyan"],opacity=.75))
            fig_a.add_trace(go.Bar(name="Ejecucion",x=yrs_disp,y=ev,marker_color=C["azul"]))
            fig_a.update_layout(barmode="group",height=350,paper_bgcolor="white",plot_bgcolor="#fafafa",
                font={"family":"DM Sans"},legend=dict(orientation="h",y=1.1),margin=dict(t=20,b=20))
            st.plotly_chart(fig_a, width="stretch", key="bar_acum_a")

            # Por linea acumulado
            sec("Ejecucion Financiera Acumulada por Linea")
            if cL in pf.columns:
                ef_acum_df = (
                    pf.group_by(cL)
                      .agg(*[pl.col(cEF(y)).sum() for y in yrs_disp],
                           *[pl.col(cPF(y)).sum() for y in ["2024","2025","2026","2027"] if cPF(y) in pf.columns])
                      .to_pandas()
                )
                ef_acum_df["Ejec_Acum"] = sum(ef_acum_df.get(cEF(y),0) for y in yrs_disp)
                ef_acum_df["Prog_Cuat"] = sum(ef_acum_df.get(cPF(y),0) for y in ["2024","2025","2026","2027"] if cPF(y) in ef_acum_df.columns)
                ef_acum_df["Pct_Acum"]  = ef_acum_df.apply(
                    lambda r: r["Ejec_Acum"]/r["Prog_Cuat"] if r["Prog_Cuat"]>0 else 0, axis=1)
                ef_acum_df = ef_acum_df.sort_values("Pct_Acum")
                gt1,gt2 = st.tabs(["Grafico","Tabla"])
                with gt1:
                    barra_financiera(ef_acum_df,"Ejec_Acum","Prog_Cuat","Pct_Acum",cL,"Lineas - Acumulado","bfl_a")
                with gt2:
                    s = ef_acum_df[[cL,"Prog_Cuat","Ejec_Acum","Pct_Acum"]].copy()
                    s.columns=["Linea","Prog. Cuatrienio","Ejec. Acumulada","% Avance Acumulado"]
                    st.markdown(htable(s,col_pct=["% Avance Acumulado"],
                                       col_money=["Prog. Cuatrienio","Ejec. Acumulada"]),unsafe_allow_html=True)

# ================================================================
# TAB 3: EJECUCION FISICA
# ================================================================
with tab3:
    if pond_vig_f is None and pond_cuat_f is None:
        st.info("No hay datos de ejecucion fisica disponibles.")
    else:
        ft1,ft2 = st.tabs([f"Vigencia {vig}", "Cuatrienio Acumulado"])

        def mostrar_grupo_fisico(group_col, label, pond_v, pond_c, n_p, n_t, tab_key_suf, es_vig_sel):
            df = eficacia_grupo(pond_v, pond_c, n_p, n_t, group_col, es_vig_sel)
            if df is None or df.empty:
                st.info(f"No hay datos para {label}.")
                return
            gt1,gt2 = st.tabs(["Grafico","Tabla"])
            with gt1:
                barra_horizontal(df,"% Avance de la Ejecucion Fisica",group_col,
                    f"{label} - {'Vigencia '+vig if es_vig_sel else 'Cuatrienio'}",
                    f"bar_{tab_key_suf}")
                tip = (f"Replica avance_vigencia del notebook: Aporte / Peso donde "
                       f"Aporte = suma(promedio_avance_programa * peso_programa) y "
                       f"Peso = metas_prog_grupo / total_metas_prog_{vig}.")
                st.caption(tip)
            with gt2:
                df_s = df.copy().sort_values("% Avance de la Ejecucion Fisica",ascending=False)
                st.markdown(htable(df_s, col_pct=["% Avance de la Ejecucion Fisica"],
                    tooltips={"% Avance de la Ejecucion Fisica":
                        "Eficacia Operativa del notebook: "
                        "sum(promedio_programa * peso_programa) / peso_grupo. "
                        "Superior >= 100% | Alto 60-99% | Medio 30-59% | Minimo < 30%"}),
                    unsafe_allow_html=True)

        with ft1:
            sec(f"Avance Fisico por Linea Estrategica - Vigencia {vig}")
            mostrar_grupo_fisico(cL,"Lineas",pond_vig_f,pond_cuat_f,n_prog_f,n_total_f,"lin_v",True)
            sec(f"Avance Fisico por Sector PDD - Vigencia {vig}")
            mostrar_grupo_fisico("Sector PDD","Sectores",pond_vig_f,pond_cuat_f,n_prog_f,n_total_f,"sec_v",True)
            sec(f"Avance Fisico por Programa PDD - Vigencia {vig}")
            mostrar_grupo_fisico("Programa PDD","Programas",pond_vig_f,pond_cuat_f,n_prog_f,n_total_f,"prg_v",True)

            # Tabla detalle de metas
            sec("Detalle de Metas PDD")
            dcols = [c for c in ["Codigo Meta",cL,"Sector PDD","Programa PDD","Responsable",CM,CP,CPAC] if c in pf.columns]
            tbl = pf.select(dcols).to_pandas()
            for pc in [CP,CPAC]:
                if pc in tbl.columns: tbl[pc] = tbl[pc].fillna(0)
            st.markdown(htable(tbl, col_pct=[c for c in [CP,CPAC] if c in tbl.columns],
                tooltips={CP:f"PORCENTAJE DE EJECUCION {vig} (0.92 = 92%). Pill = semaforización.",
                          CPAC:"Avance acumulado frente a meta cuatrienal."}),
                unsafe_allow_html=True)

        with ft2:
            sec("Avance Fisico por Linea Estrategica - Cuatrienio")
            mostrar_grupo_fisico(cL,"Lineas",pond_vig_f,pond_cuat_f,n_prog_f,n_total_f,"lin_c",False)
            sec("Avance Fisico por Sector PDD - Cuatrienio")
            mostrar_grupo_fisico("Sector PDD","Sectores",pond_vig_f,pond_cuat_f,n_prog_f,n_total_f,"sec_c",False)
            sec("Avance Fisico por Programa PDD - Cuatrienio")
            mostrar_grupo_fisico("Programa PDD","Programas",pond_vig_f,pond_cuat_f,n_prog_f,n_total_f,"prg_c",False)

# ================================================================
# TAB 4: POR DEPENDENCIA
# ================================================================
with tab4:
    sec(f"Avance por Dependencia Responsable - {periodo_label}")
    if CP not in pf.columns or CM not in pf.columns:
        st.info("No hay datos de dependencias disponibles.")
    else:
        # ejecucion_por_dependencia del notebook
        ejec_dep_acum = (
            pff.select(pl.col("Responsable").str.strip_chars(), CPAC)
               .group_by("Responsable")
               .agg(pl.col(CPAC).fill_null(0).mean().alias("Pct_Acum"))
            if CPAC in pff.columns else None
        )

        cat_e = (pl.when(pl.col(CCA)=="Superior").then(1).otherwise(0).alias("Sup")
                 if CCA in pf.columns else pl.lit(0).alias("Sup"))

        dep = (
            pf.filter(pl.col(CM).fill_null(0)!=0)
              .with_columns(cat_e, pl.lit(1).alias("mp"))
              .group_by(pl.col("Responsable").str.strip_chars())
              .agg(pl.col(CP).fill_null(0).mean().alias("Avance"),
                   pl.col("mp").sum().alias("N Metas"),
                   pl.col("Sup").sum().alias("N Superiores"))
        )
        if ejec_dep_acum is not None:
            dep = dep.join(ejec_dep_acum, on="Responsable", how="left")
            dep = dep.with_columns(pl.col("Pct_Acum").fill_null(0))
        else:
            dep = dep.with_columns(pl.lit(0.0).alias("Pct_Acum"))

        # Homologacion
        if hom is not None:
            rc = next((c for c in hom.columns if "Responsable" in c and "PI" in c), None)
            if rc:
                dep = dep.join(hom.rename({rc:"Responsable"}), on="Responsable", how="left")

        dep_pd = dep.to_pandas()
        dep_pd["Avance"]   = dep_pd["Avance"].fillna(0)
        dep_pd["Pct_Acum"] = dep_pd["Pct_Acum"].fillna(0)
        name_c = "Dependencia Responsable" if "Dependencia Responsable" in dep_pd.columns else "Responsable"
        dep_s  = dep_pd.sort_values("Avance", ascending=True)

        ft1,ft2 = st.tabs([f"Vigencia {vig}","Cuatrienio Acumulado"])
        with ft1:
            fig_dep = go.Figure(go.Bar(
                x=dep_s["Avance"]*100, y=dep_s[name_c], orientation="h",
                marker_color=[sem_color(v) for v in dep_s["Avance"]],
                text=[fmt_pct(v) for v in dep_s["Avance"]], textposition="outside",
                customdata=dep_s[["N Metas","N Superiores","Pct_Acum"]].values,
                hovertemplate=(f"<b>%{{y}}</b><br>Avance {vig}: %{{text}}<br>"
                               "Metas programadas: %{customdata[0]}<br>"
                               "Metas superiores: %{customdata[1]}<br>"
                               "Avance acumulado: %{customdata[2]:.1%}<extra></extra>"),
            ))
            fig_dep.update_layout(xaxis_title=f"% Avance {vig}",xaxis_range=[0,130],
                height=max(360,len(dep_s)*52),paper_bgcolor="white",plot_bgcolor="#fafafa",
                font={"family":"DM Sans"},margin=dict(l=20,r=110,t=30,b=20))
            st.plotly_chart(fig_dep, width="stretch", key="bar_dep_v")
            st.caption(f"Promedio del PORCENTAJE DE EJECUCION {vig} de las metas programadas a cargo de cada dependencia.")

            tbl_d = dep_pd[[name_c,"N Metas","N Superiores","Avance","Pct_Acum"]].copy()
            tbl_d.columns=["Dependencia","Metas Prog.",f"Superiores {vig}",f"% Avance {vig}","% Avance Acumulado"]
            tbl_d = tbl_d.sort_values(f"% Avance {vig}", ascending=False).reset_index(drop=True)
            st.markdown(htable(tbl_d,col_pct=[f"% Avance {vig}","% Avance Acumulado"],
                tooltips={f"% Avance {vig}":f"Promedio PORCENTAJE DE EJECUCION {vig} de metas programadas.",
                          "% Avance Acumulado":"Promedio PORCENTAJE DE EJECUCION ACUMULADA (cuatrienio).",
                          f"Superiores {vig}":f"Metas con CATEGORIA DE EJECUCION FISICA = 'Superior' en {vig}."}),
                unsafe_allow_html=True)

        with ft2:
            dep_cuat = dep_pd.sort_values("Pct_Acum", ascending=True)
            fig_dc = go.Figure(go.Bar(
                x=dep_cuat["Pct_Acum"]*100, y=dep_cuat[name_c], orientation="h",
                marker_color=[sem_color(v) for v in dep_cuat["Pct_Acum"]],
                text=[fmt_pct(v) for v in dep_cuat["Pct_Acum"]], textposition="outside",
                hovertemplate="<b>%{y}</b><br>Avance acumulado: %{text}<extra></extra>",
            ))
            fig_dc.update_layout(xaxis_title="% Avance Acumulado Cuatrienio",xaxis_range=[0,130],
                height=max(360,len(dep_cuat)*52),paper_bgcolor="white",plot_bgcolor="#fafafa",
                font={"family":"DM Sans"},margin=dict(l=20,r=110,t=30,b=20))
            st.plotly_chart(fig_dc, width="stretch", key="bar_dep_c")
            st.caption("Promedio del PORCENTAJE DE EJECUCION ACUMULADA por dependencia (sin filtro de meta programada en la vigencia, replicando el notebook).")

# ──────────────────────────────────────────────────────────────────
# ERRORES OPCIONALES
# ──────────────────────────────────────────────────────────────────
miss = []
if h26_b is None: miss.append(("Hacienda 2026","Hacienda 2026"))
if r26_b is None: miss.append(("Regalias 2026","Regalias 2026"))
if miss:
    with st.expander("Archivos 2026 no cargados", expanded=False):
        for nm,k in miss:
            show_err(nm, SCHEMAS[k][1], SCHEMAS[k][0])

st.markdown('<div class="footer">Dashboard de Avance PDD &middot; Streamlit &middot; Polars &middot; Plotly</div>',
            unsafe_allow_html=True)
