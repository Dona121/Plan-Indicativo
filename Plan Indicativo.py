import streamlit as st
import requests as _req
import pandas as pd

st.set_page_config(
    page_title="Plan Indicativo Municipal",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #f1f5fb; }
.block-container { padding-top: 1rem !important; }

.header-banner {
    background: linear-gradient(135deg, #0d1b2e 0%, #1e3352 60%, #1e40af 100%);
    border-radius: 12px; padding: 28px 32px; margin-bottom: 20px; color: white;
}
.header-banner h1 { margin: 0 0 4px 0; font-size: 24px; font-weight: 800; letter-spacing: -0.02em; color: #f8fafc; }
.header-banner .subtitle { font-size: 13px; color: #94a3b8; margin: 0; }
.header-banner .toplabel { font-size: 10px; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase; color: #475569; margin-bottom: 6px; }
.stats-row { display: flex; gap: 12px; margin-top: 16px; }
.stat-box { background: rgba(255,255,255,0.07); border-radius: 10px; padding: 10px 18px; text-align: center; min-width: 100px; }
.stat-box .val { font-size: 24px; font-weight: 800; color: #f8fafc; }
.stat-box .lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; }

.pill { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 0.03em; }
.pill-blue  { background: #dbeafe; color: #2563eb; }
.pill-green { background: #d1fae5; color: #10b981; }
.pill-amber { background: #fef3c7; color: #f59e0b; }
.pill-gray  { background: #f1f5f9; color: #64748b; }

.meta-box { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; text-align: center; margin-bottom: 8px; }
.meta-box .year { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.meta-box .value { font-size: 22px; font-weight: 800; color: #2563eb; }

.detail-item .dlabel { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 3px; }
.detail-item .dvalue { font-size: 12px; font-weight: 500; color: #1e293b; }

.proy-row { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 6px; }
.proy-row:hover { border-color: #2563eb; box-shadow: 0 2px 10px rgba(37,99,235,0.1); }
.proy-nombre { font-size: 13px; font-weight: 700; color: #1e293b; margin: 3px 0; }
.proy-meta { font-size: 11px; color: #64748b; }
.ejec-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 8px; }
.ejec-box { background: #f8faff; border: 1px solid #e2e8f0; border-radius: 7px; padding: 6px 8px; text-align: center; }
.ejec-box .eyear { font-size: 9px; color: #94a3b8; font-weight: 700; margin-bottom: 2px; }
.ejec-box .evalue { font-size: 13px; font-weight: 800; color: #2563eb; }

.form-section { background: #f0f7ff; border: 1.5px solid #2563eb; border-radius: 10px; padding: 16px; margin-bottom: 10px; }
.form-title { font-size: 11px; font-weight: 800; color: #2563eb; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; }

.section-title { font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.col-header { font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 12px 0; }
.empty-state { text-align: center; padding: 32px; color: #94a3b8; font-size: 13px; }
.error-box { background: #fee2e2; border: 1px solid #fca5a5; border-radius: 8px; padding: 14px; color: #dc2626; font-size: 13px; }
.chip { display: inline-flex; align-items: center; gap: 4px; background: #dbeafe; color: #2563eb; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; margin: 2px; }

.stButton > button { font-family: 'IBM Plex Sans', sans-serif !important; font-weight: 700 !important; font-size: 12px !important; border-radius: 7px !important; }
.stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea {
    font-family: 'IBM Plex Sans', sans-serif !important; font-size: 13px !important; border-radius: 7px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Supabase REST ──────────────────────────────────────────────────────────────
SUPABASE_URL = "https://inkaifstkrizlaowkerb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlua2FpZnN0a3Jpemxhb3drZXJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxODI3MDAsImV4cCI6MjA4ODc1ODcwMH0.fXvVBRQ2s1WBI5Gs_JFiJQb-GF00pF5PFgSa1GO-A0k"

_H = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def _rest(path, method="GET", params=None, body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    r = _req.request(method, url, headers=_H, params=params, json=body, timeout=15)
    if not r.ok:
        raise Exception(r.json())
    return r.json() if r.text.strip() else None

# ── Columnas exactas ───────────────────────────────────────────────────────────
# Plan Indicativo
PI_COLS = [
    "Codigo Meta",
    "Serie Numero",
    "Línea Estratégica",
    "Indicador de resultado",
    "Línea base",
    "Unidad de Medida del Indicador de Resultado",
    "Año base",
    "Fuente",
    "Meta cuatrienio",
    "ODS",
    "Sector PDD",
    "Numero Programa PDD",
    "Programa PDD",
    "Sector de inversión",
    "Código del sector",
    "Programa Presupuestal",
    "Código del programa",
    "Producto",
    "Código del producto",
    "Indicador de producto principal",
    "Código de indicador principal",
    "Descripción",
    "Medido a través de",
    "Tiene EDT",
    "Unidad de Medida del Indicador de Producto",
    "Meta de Cuatrienio del Indicador de Producto",
    "Tipo de Acumulación",
    "Responsable",
    "Meta Física Esperada 2024",
    "Meta Física Esperada 2025",
    "Meta Física Esperada 2026",
    "Meta Física Esperada 2027",
    "OBSERVACIONES SEGUIMIENTO",
    "OBSERVACIONES",
]

# Proyectos
PROY_COLS = [
    "IdProyecto",
    "Codigo Meta",
    "Ejecución 2024",
    "Ejecución 2025",
    "Ejecución 2026",
    "Ejecución 2027",
    "BPIN",
    "NOMBRE DEL PROYECTO",
    "META DEL PROYECTO",
    "MUNICIPIO",
    "VIGENCIA PI",
    "OBSERVACIONES DE SEGUIMIENTO",
]

# ── Data loaders ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_indicadores():
    cols = ",".join(PI_COLS)
    return _rest("Plan%20Indicativo", params={"select": cols, "order": "Serie Numero.asc"}) or []

def load_proyectos(codigo_meta: str):
    return _rest("Proyectos", params={"select": "*", "Codigo Meta": f"eq.{codigo_meta}"}) or []

def save_proyecto(body: dict, is_new: bool, proyecto_id=None):
    if is_new:
        return _rest("Proyectos", method="POST", body=body)
    else:
        return _rest(f"Proyectos?IdProyecto=eq.{proyecto_id}", method="PATCH", body=body)

def delete_proyecto(proyecto_id):
    _rest(f"Proyectos?IdProyecto=eq.{proyecto_id}", method="DELETE")

# ── Session state helper ───────────────────────────────────────────────────────
def ss(key, default=None):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

# ── Proyecto form ──────────────────────────────────────────────────────────────
def render_proyecto_form(codigo_meta: str, proyecto: dict = None, form_key: str = "new"):
    is_new = proyecto is None
    p = proyecto or {}
    form_title = "Nuevo Proyecto" if is_new else f"Editando Proyecto #{p.get('IdProyecto', '')}"

    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="form-title">{form_title}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        bpin      = st.text_input("BPIN",      value=p.get("BPIN", "") or "",                key=f"bpin_{form_key}")
    with c2:
        municipio = st.text_input("Municipio", value=p.get("MUNICIPIO", "") or "",           key=f"mun_{form_key}")

    nombre   = st.text_input("Nombre del Proyecto",          value=p.get("NOMBRE DEL PROYECTO", "") or "",    key=f"nom_{form_key}")
    meta_p   = st.text_area("Meta del Proyecto",             value=p.get("META DEL PROYECTO", "") or "",      key=f"metap_{form_key}", height=80)
    obs      = st.text_area("Observaciones de Seguimiento",  value=p.get("OBSERVACIONES DE SEGUIMIENTO", "") or "", key=f"obs_{form_key}", height=60)
    vigencia = st.number_input("Vigencia PI", value=int(p.get("VIGENCIA PI", 2024) or 2024), min_value=2020, max_value=2030, key=f"vig_{form_key}")

    st.markdown('<div class="section-title" style="margin-top:8px">Ejecución por Año</div>', unsafe_allow_html=True)
    ec = st.columns(4)
    ejecuciones = {}
    for i, year in enumerate([2024, 2025, 2026, 2027]):
        with ec[i]:
            st.markdown(f'<div style="text-align:center;font-size:11px;color:#94a3b8;font-weight:700;margin-bottom:2px">{year}</div>', unsafe_allow_html=True)
            ejecuciones[year] = st.number_input(
                str(year),
                value=float(p.get(f"Ejecución {year}", 0) or 0),
                key=f"ejec_{year}_{form_key}",
                label_visibility="collapsed",
            )

    b1, b2, b3, _ = st.columns([1, 1, 1, 3])
    saved = deleted = False

    with b1:
        if st.button("Guardar", key=f"save_{form_key}", type="primary"):
            payload = {
                "Codigo Meta":                    codigo_meta,
                "BPIN":                           bpin,
                "MUNICIPIO":                      municipio,
                "NOMBRE DEL PROYECTO":            nombre,
                "META DEL PROYECTO":              meta_p,
                "OBSERVACIONES DE SEGUIMIENTO":   obs,
                "VIGENCIA PI":                    vigencia,
                "Ejecución 2024":                 ejecuciones[2024],
                "Ejecución 2025":                 ejecuciones[2025],
                "Ejecución 2026":                 ejecuciones[2026],
                "Ejecución 2027":                 ejecuciones[2027],
            }
            try:
                save_proyecto(payload, is_new=is_new, proyecto_id=p.get("IdProyecto"))
                st.success("Guardado correctamente.")
                saved = True
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    if not is_new:
        with b2:
            if st.button("Eliminar", key=f"del_{form_key}"):
                try:
                    delete_proyecto(p["IdProyecto"])
                    st.success("Eliminado.")
                    deleted = True
                except Exception as e:
                    st.error(f"Error: {e}")

    with b3:
        if st.button("Cancelar", key=f"cancel_{form_key}"):
            saved = True

    st.markdown('</div>', unsafe_allow_html=True)
    return saved, deleted

# ── Indicador row ──────────────────────────────────────────────────────────────
def render_indicador(ind: dict, idx: int):
    codigo   = ind.get("Codigo Meta", "")
    exp_key  = f"exp_{codigo}"
    edit_key = f"edit_{codigo}"
    add_key  = f"add_{codigo}"
    proy_key = f"proy_{codigo}"

    ss(exp_key,  False)
    ss(edit_key, None)
    ss(add_key,  False)

    # Toggle
    expanded = st.toggle("expand", value=st.session_state[exp_key], key=f"tog_{codigo}", label_visibility="collapsed")
    st.session_state[exp_key] = expanded

    sector    = ind.get("Sector PDD", "") or ""
    tipo_acum = ind.get("Tipo de Acumulación", "") or ""
    linea     = ind.get("Línea Estratégica", "") or ""
    indicador = ind.get("Indicador de producto principal") or ind.get("Indicador de resultado", "") or ""

    bg         = "#162032" if expanded else ("#f8fafd" if idx % 2 == 0 else "#ffffff")
    text_color = "#f1f5f9" if expanded else "#1e293b"
    sub_color  = "#94a3b8" if expanded else "#64748b"
    code_color = "#93c5fd" if expanded else "#2563eb"
    border_cl  = "#1e3352" if expanded else "#e2e8f0"
    br         = "8px 8px 0 0" if expanded else "8px"

    st.markdown(f"""
    <div style="background:{bg};border:1.5px solid {border_cl};border-radius:{br};padding:12px 16px;margin-top:-8px;">
      <div style="display:grid;grid-template-columns:160px 1fr 1fr 130px 130px;gap:12px;align-items:center;">
        <div>
          <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:2px">Código Meta</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:700;color:{code_color}">{codigo}</div>
        </div>
        <div>
          <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:2px">Línea Estratégica</div>
          <div style="font-size:12px;font-weight:600;color:{text_color}">{linea}</div>
        </div>
        <div>
          <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:2px">Indicador Principal</div>
          <div style="font-size:11px;color:{sub_color};overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{indicador}</div>
        </div>
        <div>
          <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:4px">Sector PDD</div>
          <span class="pill pill-blue">{sector}</span>
        </div>
        <div>
          <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:4px">Tipo Acumulación</div>
          <span class="pill pill-amber">{tipo_acum}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not expanded:
        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
        return

    # ── Panel expandido ────────────────────────────────────────────────────────
    st.markdown("""<div style="border:1.5px solid #1e3352;border-top:none;border-radius:0 0 8px 8px;
        background:#f8faff;padding:16px;margin-bottom:10px;">""", unsafe_allow_html=True)

    # Metadata
    meta_fields = [
        ("Programa PDD",           ind.get("Programa PDD") or "—"),
        ("Sector de Inversión",    ind.get("Sector de inversión") or "—"),
        ("Programa Presupuestal",  ind.get("Programa Presupuestal") or "—"),
        ("Producto",               ind.get("Producto") or "—"),
        ("Cód. Indicador",         ind.get("Código de indicador principal") or "—"),
        ("Responsable",            ind.get("Responsable") or "—"),
        ("Meta Cuatrienio",        ind.get("Meta cuatrienio") or "—"),
        ("Unidad de Medida",       ind.get("Unidad de Medida del Indicador de Producto") or "—"),
    ]
    cols = st.columns(4)
    for i, (label, value) in enumerate(meta_fields):
        with cols[i % 4]:
            st.markdown(f"""<div class="detail-item" style="margin-bottom:10px">
                <div class="dlabel">{label}</div>
                <div class="dvalue">{value}</div>
            </div>""", unsafe_allow_html=True)

    # Metas físicas
    mcols = st.columns(4)
    for i, year in enumerate([2024, 2025, 2026, 2027]):
        val = ind.get(f"Meta Física Esperada {year}")
        with mcols[i]:
            st.markdown(f"""<div class="meta-box">
                <div class="year">Meta {year}</div>
                <div class="value">{val if val is not None else '—'}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Proyectos header
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        st.markdown('<div class="section-title">Proyectos Asociados</div>', unsafe_allow_html=True)
    with hc2:
        if st.button("+ Agregar", key=f"addbtn_{codigo}"):
            st.session_state[add_key]  = True
            st.session_state[edit_key] = None

    # Cargar proyectos
    if proy_key not in st.session_state:
        st.session_state[proy_key] = load_proyectos(codigo)
    proyectos = st.session_state[proy_key]

    # Formulario nuevo
    if st.session_state[add_key]:
        saved, _ = render_proyecto_form(codigo, form_key=f"new_{codigo}")
        if saved:
            st.session_state[add_key]  = False
            st.session_state[proy_key] = load_proyectos(codigo)
            st.rerun()

    if not proyectos and not st.session_state[add_key]:
        st.markdown('<div class="empty-state">No hay proyectos asociados. Haz clic en "+ Agregar" para comenzar.</div>', unsafe_allow_html=True)

    for p in proyectos:
        pid = p.get("IdProyecto")
        if st.session_state[edit_key] == pid:
            saved, deleted = render_proyecto_form(codigo, proyecto=p, form_key=f"edit_{pid}")
            if saved or deleted:
                st.session_state[edit_key] = None
                st.session_state[proy_key] = load_proyectos(codigo)
                st.rerun()
        else:
            pc1, pc2 = st.columns([4, 1])
            with pc1:
                bpin_v  = p.get("BPIN") or "Sin BPIN"
                mun_v   = p.get("MUNICIPIO") or ""
                vig_v   = p.get("VIGENCIA PI") or ""
                nom_v   = p.get("NOMBRE DEL PROYECTO") or "Sin nombre"
                meta_v  = p.get("META DEL PROYECTO") or ""
                ejec_html = "".join(
                    f'<div class="ejec-box"><div class="eyear">{y}</div><div class="evalue">{p.get(f"Ejecución {y}", "—")}</div></div>'
                    for y in [2024, 2025, 2026, 2027]
                )
                municipio_pill = f'<span class="pill pill-blue">{mun_v}</span>' if mun_v else ""
                vigencia_pill  = f'<span class="pill pill-gray">Vigencia {vig_v}</span>' if vig_v else ""
                meta_div       = f'<div class="proy-meta">{meta_v}</div>' if meta_v else ""
                st.markdown(f"""<div class="proy-row">
                    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px">
                        <span class="pill pill-gray">{bpin_v}</span>
                        {municipio_pill}{vigencia_pill}
                    </div>
                    <div class="proy-nombre">{nom_v}</div>
                    {meta_div}
                    <div class="ejec-grid">{ejec_html}</div>
                </div>""", unsafe_allow_html=True)
            with pc2:
                if st.button("Editar", key=f"editbtn_{pid}", use_container_width=True):
                    st.session_state[edit_key] = pid
                    st.session_state[add_key]  = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    try:
        data = load_indicadores()
    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Error al conectar con Supabase:</strong><br>{e}</div>', unsafe_allow_html=True)
        return

    responsables = sorted({d.get("Responsable", "") for d in data if d.get("Responsable")})

    # Header
    st.markdown(f"""<div class="header-banner">
        <div class="toplabel">Sistema de Seguimiento</div>
        <h1>Plan Indicativo Municipal</h1>
        <p class="subtitle">Cuatrienio 2024 – 2027</p>
        <div class="stats-row">
            <div class="stat-box"><div class="val">{len(data)}</div><div class="lbl">Indicadores</div></div>
            <div class="stat-box"><div class="val">{len(responsables)}</div><div class="lbl">Responsables</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Filtros
    fc1, fc2 = st.columns([2, 2])
    with fc1:
        search = st.text_input("", placeholder="Buscar por código, línea o indicador...", label_visibility="collapsed")
    with fc2:
        selected_resp = st.multiselect("", options=responsables, placeholder="Filtrar por responsable...", label_visibility="collapsed", key="filter_resp")

    # Aplicar filtros
    filtered = data
    if search:
        q = search.lower()
        filtered = [d for d in filtered if
            q in (d.get("Codigo Meta") or "").lower() or
            q in (d.get("Línea Estratégica") or "").lower() or
            q in (d.get("Indicador de producto principal") or "").lower() or
            q in (d.get("Sector PDD") or "").lower()]
    if selected_resp:
        filtered = [d for d in filtered if d.get("Responsable") in selected_resp]

    # Chips de filtro activos
    if selected_resp:
        chips = " ".join(f'<span class="chip">{r}</span>' for r in selected_resp)
        st.markdown(f'<div style="margin-bottom:8px">{chips}</div>', unsafe_allow_html=True)

    if len(filtered) != len(data):
        st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px">Mostrando {len(filtered)} de {len(data)} indicadores</div>', unsafe_allow_html=True)

    # Encabezados columnas
    if not filtered:
        st.markdown('<div class="empty-state">No se encontraron indicadores con los filtros aplicados.</div>', unsafe_allow_html=True)
        return

    h1, h2, h3, h4, h5 = st.columns([1.6, 1, 1, 1.3, 1.3])
    for col, label in zip([h1,h2,h3,h4,h5], ["Código Meta","Línea Estratégica","Indicador","Sector PDD","Tipo Acumulación"]):
        with col:
            st.markdown(f'<div class="col-header">{label}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider" style="margin:6px 0 10px 0">', unsafe_allow_html=True)

    for idx, ind in enumerate(filtered):
        render_indicador(ind, idx)

if __name__ == "__main__":
    main()
