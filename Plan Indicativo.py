import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plan Indicativo Municipal",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background-color: #f1f5fb;
}

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #0d1b2e 0%, #1e3352 60%, #1e40af 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 20px;
    color: white;
}
.header-banner h1 {
    margin: 0 0 4px 0;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #f8fafc;
}
.header-banner .subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
}
.header-banner .label {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 6px;
}
.stats-row {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}
.stat-box {
    background: rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 18px;
    text-align: center;
    min-width: 100px;
}
.stat-box .val {
    font-size: 24px;
    font-weight: 800;
    color: #f8fafc;
}
.stat-box .lbl {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
}

/* Indicador card */
.ind-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 2px;
    cursor: pointer;
    border: 1px solid #334155;
}
.ind-header.expanded {
    background: linear-gradient(135deg, #0d1b2e 0%, #1e3352 100%);
    border-radius: 8px 8px 0 0;
    border-color: #1e3352;
}
.ind-codigo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #93c5fd;
}
.ind-linea {
    font-size: 13px;
    font-weight: 600;
    color: #f1f5f9;
    margin-top: 2px;
}
.ind-indicador {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 2px;
}

/* Pills */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.pill-blue  { background: #dbeafe; color: #2563eb; }
.pill-green { background: #d1fae5; color: #10b981; }
.pill-amber { background: #fef3c7; color: #f59e0b; }
.pill-gray  { background: #f1f5f9; color: #64748b; }

/* Meta boxes */
.meta-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 12px 0;
}
.meta-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
}
.meta-box .year {
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.meta-box .value {
    font-size: 22px;
    font-weight: 800;
    color: #2563eb;
}

/* Proyecto row */
.proy-row {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    transition: border-color 0.15s;
}
.proy-row:hover {
    border-color: #2563eb;
    box-shadow: 0 2px 10px rgba(37,99,235,0.1);
}
.proy-nombre {
    font-size: 13px;
    font-weight: 700;
    color: #1e293b;
    margin: 3px 0;
}
.proy-meta {
    font-size: 11px;
    color: #64748b;
}

/* Detail section */
.detail-panel {
    background: #f8faff;
    border: 1.5px solid #1e3352;
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 16px;
    margin-bottom: 8px;
}
.detail-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    background: white;
    border-radius: 8px;
    padding: 14px;
    border: 1px solid #e2e8f0;
    margin-bottom: 12px;
}
.detail-item .dlabel {
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 3px;
}
.detail-item .dvalue {
    font-size: 12px;
    font-weight: 500;
    color: #1e293b;
}

/* Form styling */
.form-section {
    background: #f0f7ff;
    border: 1.5px solid #2563eb;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 10px;
}
.form-section .form-title {
    font-size: 11px;
    font-weight: 800;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}

/* Ejecucion boxes */
.ejec-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}
.ejec-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    padding: 8px;
    text-align: center;
}
.ejec-box .eyear {
    font-size: 10px;
    color: #94a3b8;
    font-weight: 700;
    margin-bottom: 2px;
}
.ejec-box .evalue {
    font-size: 14px;
    font-weight: 800;
    color: #2563eb;
}

/* Section title */
.section-title {
    font-size: 11px;
    font-weight: 800;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}

/* Filter chip */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #dbeafe;
    color: #2563eb;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin: 2px;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 32px;
    color: #94a3b8;
    font-size: 13px;
}

/* Column header */
.col-header {
    font-size: 10px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Error box */
.error-box {
    background: #fee2e2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    padding: 14px;
    color: #dc2626;
    font-size: 13px;
}

/* Divider */
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 12px 0; }

/* Remove streamlit default padding */
.block-container { padding-top: 1rem !important; }

/* Streamlit button overrides */
.stButton > button {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    border-radius: 7px !important;
    border: none !important;
    padding: 6px 14px !important;
    transition: opacity 0.15s !important;
}

/* Input overrides */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 7px !important;
}

/* Selectbox override */
.stMultiSelect > div {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Supabase client ────────────────────────────────────────────────────────────
SUPABASE_URL = "https://inkaifstkrizlaowkerb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlua2FpZnN0a3Jpemxhb3drZXJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxODI3MDAsImV4cCI6MjA4ODc1ODcwMH0.fXvVBRQ2s1WBI5Gs_JFiJQb-GF00pF5PFgSa1GO-A0k"

import requests as _req

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

# ── Data loaders ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_indicadores():
    cols = ",".join([
        "Codigo Meta", "Serie Numero", "Linea Estrategica",
        "Sector PDD", "Programa PDD", "Sector de inversion",
        "Programa Presupuestal", "Producto",
        "Indicador de producto principal", "Codigo de indicador principal",
        "Tipo de Acumulacion", "Responsable",
        "Meta cuatrienio", "Unidad de Medida del Indicador de Producto",
        "Meta Fisica Esperada 2024", "Meta Fisica Esperada 2025",
        "Meta Fisica Esperada 2026", "Meta Fisica Esperada 2027",
        "Indicador de resultado",
    ])
    return _rest("Plan%20Indicativo", params={"select": cols, "order": "Serie Numero.asc"}) or []

def load_proyectos(codigo_meta: str):
    return _rest("Proyectos", params={"select": "*", "Codigo Meta": f"eq.{codigo_meta}"}) or []

def save_proyecto(data: dict, is_new: bool, proyecto_id=None):
    if is_new:
        return _rest("Proyectos", method="POST", body=data)
    else:
        return _rest(f"Proyectos?IdProyecto=eq.{proyecto_id}", method="PATCH", body=data)

def delete_proyecto(proyecto_id: int):
    _rest(f"Proyectos?IdProyecto=eq.{proyecto_id}", method="DELETE")

# ── Session state helpers ──────────────────────────────────────────────────────
def ss(key, default=None):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

# ── Render proyecto form ───────────────────────────────────────────────────────
def render_proyecto_form(codigo_meta: str, proyecto: dict = None, form_key: str = "new"):
    is_new = proyecto is None
    p = proyecto or {}

    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    form_title = "Nuevo Proyecto" if is_new else f"Editando Proyecto #{p.get('IdProyecto', '')}"
    st.markdown(f'<div class="form-title">{form_title}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        bpin = st.text_input("BPIN", value=p.get("BPIN", ""), key=f"bpin_{form_key}")
    with c2:
        municipio = st.text_input("Municipio", value=p.get("MUNICIPIO", ""), key=f"mun_{form_key}")

    nombre = st.text_input("Nombre del Proyecto", value=p.get("NOMBRE DEL PROYECTO", ""), key=f"nom_{form_key}")
    meta_proy = st.text_area("Meta del Proyecto", value=p.get("META DEL PROYECTO", ""), key=f"meta_{form_key}", height=80)
    obs = st.text_area("Observaciones de Seguimiento", value=p.get("OBSERVACIONES DE SEGUIMIENTO", ""), key=f"obs_{form_key}", height=60)

    c3, c4 = st.columns(2)
    with c3:
        vigencia = st.number_input("Vigencia PI", value=int(p.get("VIGENCIA PI", 2024)), min_value=2020, max_value=2030, key=f"vig_{form_key}")

    st.markdown('<div class="section-title" style="margin-top:8px">Ejecucion por Ano</div>', unsafe_allow_html=True)
    ec1, ec2, ec3, ec4 = st.columns(4)
    cols_ejec = [ec1, ec2, ec3, ec4]
    ejecuciones = {}
    for i, year in enumerate([2024, 2025, 2026, 2027]):
        with cols_ejec[i]:
            st.markdown(f'<div style="text-align:center;font-size:11px;color:#94a3b8;font-weight:700;margin-bottom:2px">{year}</div>', unsafe_allow_html=True)
            ejecuciones[year] = st.number_input(
                label=str(year),
                value=float(p.get(f"Ejecucion {year}", 0) or 0),
                key=f"ejec_{year}_{form_key}",
                label_visibility="collapsed",
            )

    b1, b2, b3, _ = st.columns([1, 1, 1, 3])
    saved = False
    deleted = False

    with b1:
        if st.button("Guardar", key=f"save_{form_key}", type="primary"):
            payload = {
                "Codigo Meta": codigo_meta,
                "BPIN": bpin,
                "MUNICIPIO": municipio,
                "NOMBRE DEL PROYECTO": nombre,
                "META DEL PROYECTO": meta_proy,
                "OBSERVACIONES DE SEGUIMIENTO": obs,
                "VIGENCIA PI": vigencia,
                "Ejecucion 2024": ejecuciones[2024],
                "Ejecucion 2025": ejecuciones[2025],
                "Ejecucion 2026": ejecuciones[2026],
                "Ejecucion 2027": ejecuciones[2027],
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
                    st.success("Proyecto eliminado.")
                    deleted = True
                except Exception as e:
                    st.error(f"Error: {e}")

    with b3:
        if st.button("Cancelar", key=f"cancel_{form_key}"):
            saved = True  # close form

    st.markdown('</div>', unsafe_allow_html=True)
    return saved, deleted

# ── Render single indicador ───────────────────────────────────────────────────
def render_indicador(ind: dict, idx: int):
    codigo = ind.get("Codigo Meta", "")
    state_key = f"expanded_{codigo}"
    edit_key = f"editing_{codigo}"
    adding_key = f"adding_{codigo}"
    proyectos_key = f"proyectos_{codigo}"

    ss(state_key, False)
    ss(edit_key, None)
    ss(adding_key, False)

    # Header toggle
    toggle_label = ("v " if st.session_state[state_key] else "> ") + codigo
    expanded = st.toggle(
        label=toggle_label,
        value=st.session_state[state_key],
        key=f"toggle_{codigo}",
        label_visibility="collapsed",
    )

    # Render header card
    sector = ind.get("Sector PDD", "")
    tipo_acum = ind.get("Tipo de Acumulacion", "")
    linea = ind.get("Linea Estrategica", "")
    indicador = ind.get("Indicador de producto principal") or ind.get("Indicador de resultado", "")

    bg = "#162032" if expanded else ("#f8fafd" if idx % 2 == 0 else "#ffffff")
    text_color = "#f1f5f9" if expanded else "#1e293b"
    sub_color = "#94a3b8" if expanded else "#64748b"
    code_color = "#93c5fd" if expanded else "#2563eb"
    border_color = "#1e3352" if expanded else "#e2e8f0"

    st.markdown(f"""
    <div style="background:{bg}; border:1.5px solid {border_color};
        border-radius:{'8px 8px 0 0' if expanded else '8px'};
        padding:12px 16px; margin-top:-8px;">
        <div style="display:grid; grid-template-columns:160px 1fr 1fr 130px 130px; gap:12px; align-items:center;">
            <div>
                <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:2px">Codigo Meta</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:700;color:{code_color}">{codigo}</div>
            </div>
            <div>
                <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:2px">Linea Estrategica</div>
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
                <div style="font-size:10px;color:{sub_color};font-weight:700;margin-bottom:4px">Tipo Acumulacion</div>
                <span class="pill pill-amber">{tipo_acum}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.session_state[state_key] = expanded

    if not expanded:
        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
        return

    # ── Expanded panel ────────────────────────────────────────────────────────
    with st.container():
        st.markdown("""
        <div style="border:1.5px solid #1e3352; border-top:none;
            border-radius:0 0 8px 8px; background:#f8faff; padding:16px; margin-bottom:10px;">
        """, unsafe_allow_html=True)

        # Metadata grid
        meta_fields = [
            ("Programa PDD", ind.get("Programa PDD", "—")),
            ("Sector de Inversion", ind.get("Sector de inversion", "—")),
            ("Programa Presupuestal", ind.get("Programa Presupuestal", "—")),
            ("Producto", ind.get("Producto", "—")),
            ("Cod. Indicador", ind.get("Codigo de indicador principal", "—")),
            ("Responsable", ind.get("Responsable", "—")),
            ("Meta Cuatrienio", ind.get("Meta cuatrienio", "—")),
            ("Unidad de Medida", ind.get("Unidad de Medida del Indicador de Producto", "—")),
        ]

        cols = st.columns(4)
        for i, (label, value) in enumerate(meta_fields):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:2px">{label}</div>
                    <div style="font-size:12px;font-weight:500;color:#1e293b">{value}</div>
                </div>""", unsafe_allow_html=True)

        # Metas fisicas
        st.markdown('<div class="meta-grid">', unsafe_allow_html=True)
        mcols = st.columns(4)
        for i, year in enumerate([2024, 2025, 2026, 2027]):
            val = ind.get(f"Meta Fisica Esperada {year}", "—")
            with mcols[i]:
                st.markdown(f"""
                <div class="meta-box">
                    <div class="year">Meta {year}</div>
                    <div class="value">{val if val is not None else '—'}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Proyectos section
        hcol1, hcol2 = st.columns([3, 1])
        with hcol1:
            st.markdown('<div class="section-title">Proyectos Asociados</div>', unsafe_allow_html=True)
        with hcol2:
            if st.button("+ Agregar Proyecto", key=f"add_{codigo}"):
                st.session_state[adding_key] = True
                st.session_state[edit_key] = None

        # Load proyectos
        if proyectos_key not in st.session_state:
            st.session_state[proyectos_key] = load_proyectos(codigo)

        proyectos = st.session_state[proyectos_key]

        # New proyecto form
        if st.session_state[adding_key]:
            saved, _ = render_proyecto_form(codigo, form_key=f"new_{codigo}")
            if saved:
                st.session_state[adding_key] = False
                st.session_state[proyectos_key] = load_proyectos(codigo)
                st.rerun()

        # Existing proyectos
        if not proyectos and not st.session_state[adding_key]:
            st.markdown('<div class="empty-state">No hay proyectos asociados. Haz clic en "+ Agregar Proyecto" para comenzar.</div>', unsafe_allow_html=True)

        for p in proyectos:
            pid = p.get("IdProyecto")

            if st.session_state[edit_key] == pid:
                saved, deleted = render_proyecto_form(codigo, proyecto=p, form_key=f"edit_{pid}")
                if saved or deleted:
                    st.session_state[edit_key] = None
                    st.session_state[proyectos_key] = load_proyectos(codigo)
                    st.rerun()
            else:
                # Proyecto row card
                pc1, pc2 = st.columns([3, 1])
                with pc1:
                    bpin_val = p.get("BPIN") or "Sin BPIN"
                    mun_val = p.get("MUNICIPIO") or ""
                    vig_val = p.get("VIGENCIA PI") or ""
                    nombre_val = p.get("NOMBRE DEL PROYECTO") or "Sin nombre"
                    meta_val = p.get("META DEL PROYECTO") or ""

                    st.markdown(f"""
                    <div class="proy-row">
                        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px">
                            <span class="pill pill-gray">{bpin_val}</span>
                            {f'<span class="pill pill-blue">{mun_val}</span>' if mun_val else ''}
                            {f'<span class="pill pill-gray">Vigencia {vig_val}</span>' if vig_val else ''}
                        </div>
                        <div class="proy-nombre">{nombre_val}</div>
                        {f'<div class="proy-meta">{meta_val}</div>' if meta_val else ''}
                        <div class="ejec-grid" style="margin-top:8px">
                            {''.join(f'<div class="ejec-box"><div class="eyear">{y}</div><div class="evalue">{p.get(f"Ejecucion {y}", "—")}</div></div>' for y in [2024,2025,2026,2027])}
                        </div>
                    </div>""", unsafe_allow_html=True)

                with pc2:
                    if st.button("Editar", key=f"edit_btn_{pid}", use_container_width=True):
                        st.session_state[edit_key] = pid
                        st.session_state[adding_key] = False
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    # Load data
    try:
        data = load_indicadores()
    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Error al conectar con Supabase:</strong><br>{e}</div>', unsafe_allow_html=True)
        return

    # Responsables for filter
    responsables = sorted(set(d.get("Responsable", "") for d in data if d.get("Responsable")))

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="header-banner">
        <div class="label">Sistema de Seguimiento</div>
        <h1>Plan Indicativo Municipal</h1>
        <p class="subtitle">Cuatrienio 2024 – 2027</p>
        <div class="stats-row">
            <div class="stat-box"><div class="val">{len(data)}</div><div class="lbl">Indicadores</div></div>
            <div class="stat-box"><div class="val">{len(responsables)}</div><div class="lbl">Responsables</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    fc1, fc2 = st.columns([2, 2])
    with fc1:
        search = st.text_input("", placeholder="Buscar por codigo, linea o indicador...", label_visibility="collapsed")
    with fc2:
        selected_resp = st.multiselect(
            label="",
            options=responsables,
            placeholder="Filtrar por responsable...",
            label_visibility="collapsed",
            key="filter_responsable",
        )

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = data
    if search:
        q = search.lower()
        filtered = [
            d for d in filtered if
            q in (d.get("Codigo Meta") or "").lower() or
            q in (d.get("Linea Estrategica") or "").lower() or
            q in (d.get("Indicador de producto principal") or "").lower() or
            q in (d.get("Sector PDD") or "").lower()
        ]
    if selected_resp:
        filtered = [d for d in filtered if d.get("Responsable") in selected_resp]

    # Active filter chips
    if selected_resp:
        chips = " ".join(f'<span class="chip">{r}</span>' for r in selected_resp)
        st.markdown(f'<div style="margin-bottom:8px">{chips}</div>', unsafe_allow_html=True)

    # Results count
    if len(filtered) != len(data):
        st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px">Mostrando {len(filtered)} de {len(data)} indicadores</div>', unsafe_allow_html=True)

    # ── Column headers ────────────────────────────────────────────────────────
    h1, h2, h3, h4, h5 = st.columns([1.6, 1, 1, 1.3, 1.3])
    with h1: st.markdown('<div class="col-header">Codigo Meta</div>', unsafe_allow_html=True)
    with h2: st.markdown('<div class="col-header">Linea Estrategica</div>', unsafe_allow_html=True)
    with h3: st.markdown('<div class="col-header">Indicador</div>', unsafe_allow_html=True)
    with h4: st.markdown('<div class="col-header">Sector PDD</div>', unsafe_allow_html=True)
    with h5: st.markdown('<div class="col-header">Tipo Acumulacion</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider" style="margin:6px 0 10px 0">', unsafe_allow_html=True)

    # ── Indicadores ───────────────────────────────────────────────────────────
    if not filtered:
        st.markdown('<div class="empty-state">No se encontraron indicadores con los filtros aplicados.</div>', unsafe_allow_html=True)
    else:
        for idx, ind in enumerate(filtered):
            render_indicador(ind, idx)

if __name__ == "__main__":
    main()
