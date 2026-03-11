import { useState, useEffect, useCallback, useRef } from "react";

const SUPABASE_URL = "https://inkaifstkrizlaowkerb.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlua2FpZnN0a3Jpemxhb3drZXJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxODI3MDAsImV4cCI6MjA4ODc1ODcwMH0.fXvVBRQ2s1WBI5Gs_JFiJQb-GF00pF5PFgSa1GO-A0k";

const headers = {
  "apikey": SUPABASE_KEY,
  "Authorization": `Bearer ${SUPABASE_KEY}`,
  "Content-Type": "application/json",
  "Prefer": "return=representation",
};

async function sbFetch(path, options = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, { headers, ...options });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// ─── tiny design tokens ───────────────────────────────────────────────────────
const C = {
  navy: "#0d1b2e",
  ink: "#162032",
  steel: "#1e3352",
  sky: "#2563eb",
  skyLight: "#dbeafe",
  mint: "#10b981",
  mintLight: "#d1fae5",
  amber: "#f59e0b",
  red: "#ef4444",
  surface: "#f4f7fb",
  card: "#ffffff",
  border: "#e2e8f0",
  text: "#1e293b",
  muted: "#64748b",
  faint: "#94a3b8",
};

const font = `'IBM Plex Sans', 'Segoe UI', sans-serif`;

// ─── helpers ──────────────────────────────────────────────────────────────────
function pill(label, scheme = "blue") {
  const s = {
    blue: { bg: C.skyLight, color: C.sky },
    green: { bg: C.mintLight, color: C.mint },
    amber: { bg: "#fef3c7", color: C.amber },
    red: { bg: "#fee2e2", color: C.red },
    gray: { bg: "#f1f5f9", color: C.muted },
  }[scheme] || { bg: C.skyLight, color: C.sky };
  return (
    <span style={{
      background: s.bg, color: s.color,
      fontSize: 11, fontWeight: 700, padding: "2px 8px",
      borderRadius: 20, letterSpacing: "0.04em",
      whiteSpace: "nowrap",
    }}>{label}</span>
  );
}

function Label({ children }) {
  return <div style={{ fontSize: 10, fontWeight: 700, color: C.faint, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 3 }}>{children}</div>;
}

function Field({ label, value, onChange, type = "text", multiline = false, readOnly = false }) {
  const base = {
    width: "100%", boxSizing: "border-box",
    border: `1px solid ${C.border}`, borderRadius: 7,
    padding: "6px 10px", fontSize: 13, color: C.text,
    background: readOnly ? C.surface : C.card,
    fontFamily: font, outline: "none",
    transition: "border-color .15s",
  };
  return (
    <div style={{ marginBottom: 10 }}>
      <Label>{label}</Label>
      {multiline
        ? <textarea rows={2} value={value ?? ""} onChange={e => onChange(e.target.value)} style={{ ...base, resize: "vertical" }} readOnly={readOnly} />
        : <input type={type} value={value ?? ""} onChange={e => onChange(e.target.value)} style={base} readOnly={readOnly} />
      }
    </div>
  );
}

function Btn({ children, onClick, variant = "primary", small = false, disabled = false }) {
  const variants = {
    primary: { background: C.sky, color: "#fff" },
    success: { background: C.mint, color: "#fff" },
    danger: { background: C.red, color: "#fff" },
    ghost: { background: "transparent", color: C.muted, border: `1px solid ${C.border}` },
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        ...variants[variant],
        padding: small ? "4px 12px" : "7px 16px",
        fontSize: small ? 11 : 12,
        fontWeight: 700, borderRadius: 7,
        border: "none", cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? .5 : 1,
        fontFamily: font, letterSpacing: "0.03em",
        transition: "opacity .15s, box-shadow .15s",
        whiteSpace: "nowrap",
      }}
    >{children}</button>
  );
}

// ─── MultiSelect filter ───────────────────────────────────────────────────────
function MultiSelect({ options, selected, onChange, placeholder }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handler(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggle = (opt) => {
    onChange(selected.includes(opt) ? selected.filter(s => s !== opt) : [...selected, opt]);
  };

  return (
    <div ref={ref} style={{ position: "relative", minWidth: 220 }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: "100%", padding: "7px 12px", borderRadius: 8,
          border: `1.5px solid ${open ? C.sky : C.border}`,
          background: C.card, cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          fontFamily: font, fontSize: 12, color: selected.length ? C.text : C.faint,
          transition: "border-color .15s",
        }}
      >
        <span>
          {selected.length === 0
            ? placeholder
            : selected.length === 1
              ? selected[0]
              : `${selected.length} responsables`}
        </span>
        <span style={{ color: C.faint, fontSize: 10, marginLeft: 8 }}>{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div style={{
          position: "absolute", top: "calc(100% + 4px)", left: 0, right: 0, zIndex: 999,
          background: C.card, border: `1.5px solid ${C.border}`,
          borderRadius: 8, boxShadow: "0 8px 24px rgba(0,0,0,.1)",
          maxHeight: 260, overflowY: "auto",
        }}>
          {selected.length > 0 && (
            <div
              onClick={() => onChange([])}
              style={{ padding: "8px 12px", fontSize: 11, color: C.red, fontWeight: 700, cursor: "pointer", borderBottom: `1px solid ${C.border}` }}
            >Limpiar filtro</div>
          )}
          {options.map(opt => (
            <div
              key={opt}
              onClick={() => toggle(opt)}
              style={{
                padding: "8px 12px", fontSize: 12, cursor: "pointer",
                display: "flex", alignItems: "center", gap: 8,
                background: selected.includes(opt) ? C.skyLight : "transparent",
                color: selected.includes(opt) ? C.sky : C.text,
                fontWeight: selected.includes(opt) ? 700 : 400,
              }}
            >
              <span style={{
                width: 14, height: 14, borderRadius: 3,
                border: `2px solid ${selected.includes(opt) ? C.sky : C.border}`,
                background: selected.includes(opt) ? C.sky : "transparent",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0,
              }}>
                {selected.includes(opt) && <span style={{ color: "#fff", fontSize: 9, fontWeight: 900 }}>✓</span>}
              </span>
              {opt}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Proyecto form ─────────────────────────────────────────────────────────────
function ProyectoForm({ proyecto, codigoMeta, onSaved, onCancel, onDeleted, isNew }) {
  const [data, setData] = useState({ ...proyecto });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const set = (k) => (v) => setData(p => ({ ...p, [k]: v }));

  const save = async () => {
    setSaving(true); setError(null);
    try {
      if (isNew) {
        const body = { ...data };
        delete body.IdProyecto;
        body["Codigo Meta"] = codigoMeta;
        const result = await sbFetch(`Proyectos`, {
          method: "POST",
          body: JSON.stringify(body),
        });
        onSaved(Array.isArray(result) ? result[0] : result);
      } else {
        const body = { ...data };
        delete body.IdProyecto;
        const result = await sbFetch(`Proyectos?IdProyecto=eq.${data.IdProyecto}`, {
          method: "PATCH",
          body: JSON.stringify(body),
        });
        onSaved(Array.isArray(result) ? result[0] : { ...data });
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const del = async () => {
    if (!window.confirm("¿Eliminar este proyecto?")) return;
    setSaving(true);
    try {
      await sbFetch(`Proyectos?IdProyecto=eq.${data.IdProyecto}`, { method: "DELETE" });
      onDeleted(data.IdProyecto);
    } catch (e) {
      setError(e.message);
      setSaving(false);
    }
  };

  return (
    <div style={{
      background: "#f8faff",
      border: `1.5px solid ${C.sky}`,
      borderRadius: 10, padding: 16, marginBottom: 10,
      animation: "slideIn .2s ease",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ fontSize: 11, fontWeight: 800, color: C.sky, letterSpacing: "0.1em", textTransform: "uppercase" }}>
          {isNew ? "Nuevo Proyecto" : `Proyecto #${data.IdProyecto}`}
        </span>
        <div style={{ display: "flex", gap: 6 }}>
          <Btn small onClick={save} variant="success" disabled={saving}>{saving ? "Guardando..." : "Guardar"}</Btn>
          {!isNew && <Btn small onClick={del} variant="danger" disabled={saving}>Eliminar</Btn>}
          <Btn small onClick={onCancel} variant="ghost">Cancelar</Btn>
        </div>
      </div>

      {error && <div style={{ color: C.red, fontSize: 12, marginBottom: 8, padding: "6px 10px", background: "#fee2e2", borderRadius: 6 }}>{error}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" }}>
        <Field label="BPIN" value={data["BPIN"]} onChange={set("BPIN")} />
        <Field label="Municipio" value={data["MUNICIPIO"]} onChange={set("MUNICIPIO")} />
        <div style={{ gridColumn: "1 / -1" }}>
          <Field label="Nombre del Proyecto" value={data["NOMBRE DEL PROYECTO"]} onChange={set("NOMBRE DEL PROYECTO")} />
        </div>
        <div style={{ gridColumn: "1 / -1" }}>
          <Field label="Meta del Proyecto" value={data["META DEL PROYECTO"]} onChange={set("META DEL PROYECTO")} multiline />
        </div>
        <Field label="Vigencia PI" value={data["VIGENCIA PI"]} onChange={set("VIGENCIA PI")} type="number" />
        <div style={{ gridColumn: "1 / -1" }}>
          <Field label="Observaciones de Seguimiento" value={data["OBSERVACIONES DE SEGUIMIENTO"]} onChange={set("OBSERVACIONES DE SEGUIMIENTO")} multiline />
        </div>
      </div>

      <Label>Ejecución por año</Label>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8, marginTop: 4 }}>
        {[2024, 2025, 2026, 2027].map(y => (
          <div key={y} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 7, padding: "8px 10px", textAlign: "center" }}>
            <div style={{ fontSize: 10, color: C.faint, fontWeight: 700, marginBottom: 4 }}>{y}</div>
            <input
              type="number"
              value={data[`Ejecución ${y}`] ?? ""}
              onChange={e => set(`Ejecución ${y}`)(e.target.value === "" ? null : parseFloat(e.target.value))}
              style={{ width: "100%", border: "none", background: "transparent", textAlign: "center", fontSize: 14, fontWeight: 700, color: C.sky, fontFamily: font, outline: "none" }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Indicador row ─────────────────────────────────────────────────────────────
function IndicadorRow({ ind, idx }) {
  const [expanded, setExpanded] = useState(false);
  const [proyectos, setProyectos] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [addingNew, setAddingNew] = useState(false);

  const loadProyectos = useCallback(async () => {
    if (proyectos !== null) return;
    setLoading(true);
    try {
      const rows = await sbFetch(`Proyectos?Codigo%20Meta=eq.${encodeURIComponent(ind["Codigo Meta"])}&select=*`);
      setProyectos(rows || []);
    } catch { setProyectos([]); }
    finally { setLoading(false); }
  }, [ind, proyectos]);

  const toggle = () => {
    if (!expanded) loadProyectos();
    setExpanded(e => !e);
  };

  const onSaved = (saved) => {
    setProyectos(prev => {
      if (!prev) return [saved];
      const exists = prev.find(p => p.IdProyecto === saved?.IdProyecto);
      return exists ? prev.map(p => p.IdProyecto === saved.IdProyecto ? saved : p) : [...prev, saved];
    });
    setEditingId(null);
    setAddingNew(false);
  };

  const onDeleted = (id) => {
    setProyectos(prev => prev.filter(p => p.IdProyecto !== id));
    setEditingId(null);
  };

  const rowBg = idx % 2 === 0 ? C.card : "#f8fafd";

  return (
    <div style={{ marginBottom: 4 }}>
      {/* Main row */}
      <div
        onClick={toggle}
        style={{
          background: expanded ? C.ink : rowBg,
          borderRadius: expanded ? "8px 8px 0 0" : 8,
          padding: "11px 16px",
          display: "grid",
          gridTemplateColumns: "28px 160px 1fr 1fr 110px 110px 80px",
          alignItems: "center",
          gap: 12,
          cursor: "pointer",
          border: expanded ? `1.5px solid ${C.steel}` : `1px solid ${C.border}`,
          borderBottom: expanded ? "none" : undefined,
          transition: "background .2s",
        }}
      >
        <span style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: 22, height: 22, borderRadius: 5,
          background: expanded ? "rgba(255,255,255,.15)" : C.skyLight,
          color: expanded ? "#fff" : C.sky,
          fontSize: 9, fontWeight: 900,
          transition: "transform .2s",
          transform: expanded ? "rotate(90deg)" : "rotate(0deg)",
        }}>▶</span>

        <div>
          <div style={{ fontSize: 10, color: expanded ? "#94a3b8" : C.faint, fontWeight: 600, marginBottom: 2 }}>Código Meta</div>
          <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, fontWeight: 700, color: expanded ? "#93c5fd" : C.sky }}>{ind["Codigo Meta"]}</div>
        </div>

        <div>
          <div style={{ fontSize: 10, color: expanded ? "#94a3b8" : C.faint, fontWeight: 600, marginBottom: 2 }}>Línea Estratégica</div>
          <div style={{ fontSize: 12, fontWeight: 600, color: expanded ? "#f1f5f9" : C.text }}>{ind["Línea Estratégica"]}</div>
        </div>

        <div>
          <div style={{ fontSize: 10, color: expanded ? "#94a3b8" : C.faint, fontWeight: 600, marginBottom: 2 }}>Indicador de Producto</div>
          <div style={{ fontSize: 12, color: expanded ? "#cbd5e1" : C.muted, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {ind["Indicador de producto principal"] || ind["Indicador de resultado"] || "—"}
          </div>
        </div>

        <div>
          <div style={{ fontSize: 10, color: expanded ? "#94a3b8" : C.faint, fontWeight: 600, marginBottom: 2 }}>Sector</div>
          <div style={{ fontSize: 11 }}>{pill(ind["Sector PDD"] || "—", "blue")}</div>
        </div>

        <div>
          <div style={{ fontSize: 10, color: expanded ? "#94a3b8" : C.faint, fontWeight: 600, marginBottom: 2 }}>Tipo Acumulación</div>
          <div style={{ fontSize: 11 }}>{pill(ind["Tipo de Acumulación"] || "—", "amber")}</div>
        </div>

        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 10, color: expanded ? "#94a3b8" : C.faint, fontWeight: 600, marginBottom: 2 }}>Proyectos</div>
          <div style={{ fontSize: 12, fontWeight: 700, color: expanded ? C.mintLight : C.mint }}>
            {proyectos !== null ? proyectos.length : "—"}
          </div>
        </div>
      </div>

      {/* Expanded panel */}
      {expanded && (
        <div style={{
          border: `1.5px solid ${C.steel}`,
          borderTop: "none",
          borderRadius: "0 0 8px 8px",
          background: C.surface,
          padding: 16,
          animation: "slideIn .2s ease",
        }}>
          {/* Indicator metadata */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10,
            background: C.card, borderRadius: 8, padding: 14,
            border: `1px solid ${C.border}`, marginBottom: 16,
          }}>
            {[
              ["Programa PDD", ind["Programa PDD"]],
              ["Sector de Inversión", ind["Sector de inversión"]],
              ["Programa Presupuestal", ind["Programa Presupuestal"]],
              ["Producto", ind["Producto"]],
              ["Cód. Indicador", ind["Código de indicador principal"]],
              ["Responsable", ind["Responsable"]],
              ["Meta Cuatrienio", ind["Meta cuatrienio"]],
              ["Unidad de Medida", ind["Unidad de Medida del Indicador de Producto"]],
            ].map(([k, v]) => (
              <div key={k}>
                <Label>{k}</Label>
                <div style={{ fontSize: 12, color: C.text, fontWeight: 500 }}>{v || "—"}</div>
              </div>
            ))}
          </div>

          {/* Metas físicas */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8, marginBottom: 16 }}>
            {[2024, 2025, 2026, 2027].map(y => (
              <div key={y} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "10px 14px", textAlign: "center" }}>
                <div style={{ fontSize: 10, color: C.faint, fontWeight: 700, marginBottom: 4 }}>META {y}</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: C.sky }}>{ind[`Meta Física Esperada ${y}`] ?? "—"}</div>
              </div>
            ))}
          </div>

          {/* Proyectos section */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 11, fontWeight: 800, color: C.muted, letterSpacing: "0.1em", textTransform: "uppercase" }}>Proyectos asociados</span>
              {proyectos && pill(proyectos.length, "green")}
            </div>
            <Btn small onClick={() => { setAddingNew(true); setEditingId(null); }}>+ Agregar Proyecto</Btn>
          </div>

          {loading && <div style={{ textAlign: "center", color: C.faint, fontSize: 13, padding: 20 }}>Cargando proyectos...</div>}

          {addingNew && (
            <ProyectoForm
              proyecto={{}}
              codigoMeta={ind["Codigo Meta"]}
              onSaved={onSaved}
              onCancel={() => setAddingNew(false)}
              onDeleted={() => {}}
              isNew
            />
          )}

          {proyectos && proyectos.length === 0 && !addingNew && (
            <div style={{ textAlign: "center", padding: "24px 0", color: C.faint, fontSize: 13 }}>
              No hay proyectos asociados a este indicador.
            </div>
          )}

          {proyectos && proyectos.map(p => (
            editingId === p.IdProyecto
              ? <ProyectoForm key={p.IdProyecto} proyecto={p} codigoMeta={ind["Codigo Meta"]} onSaved={onSaved} onCancel={() => setEditingId(null)} onDeleted={onDeleted} isNew={false} />
              : (
                <div
                  key={p.IdProyecto}
                  onClick={() => { setEditingId(p.IdProyecto); setAddingNew(false); }}
                  style={{
                    background: C.card, border: `1px solid ${C.border}`,
                    borderRadius: 8, padding: "10px 14px", marginBottom: 6,
                    cursor: "pointer", display: "grid",
                    gridTemplateColumns: "1fr auto",
                    alignItems: "center", gap: 12,
                    transition: "border-color .15s, box-shadow .15s",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = C.sky; e.currentTarget.style.boxShadow = "0 2px 10px rgba(37,99,235,.1)"; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.boxShadow = "none"; }}
                >
                  <div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 3 }}>
                      {pill(p["BPIN"] || "Sin BPIN", "gray")}
                      {p["MUNICIPIO"] && pill(p["MUNICIPIO"], "blue")}
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: C.text }}>{p["NOMBRE DEL PROYECTO"] || "Sin nombre"}</div>
                    {p["META DEL PROYECTO"] && <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>{p["META DEL PROYECTO"]}</div>}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 6, textAlign: "center" }}>
                    {[2024, 2025, 2026, 2027].map(y => (
                      <div key={y}>
                        <div style={{ fontSize: 9, color: C.faint, fontWeight: 700 }}>{y}</div>
                        <div style={{ fontSize: 12, fontWeight: 800, color: C.sky }}>{(p[`Ejecución ${y}`] ?? "—")}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedResponsables, setSelectedResponsables] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const cols = [
          "Codigo Meta", "Serie Numero", "Línea Estratégica",
          "Sector PDD", "Programa PDD", "Sector de inversión",
          "Programa Presupuestal", "Producto",
          "Indicador de producto principal", "Código de indicador principal",
          "Tipo de Acumulación", "Responsable",
          "Meta cuatrienio", "Unidad de Medida del Indicador de Producto",
          "Meta Física Esperada 2024", "Meta Física Esperada 2025",
          "Meta Física Esperada 2026", "Meta Física Esperada 2027",
          "Indicador de resultado",
        ].map(c => encodeURIComponent(c)).join(",");

        const rows = await sbFetch(`Plan%20Indicativo?select=${cols}&order=Serie%20Numero.asc`);
        setData(rows || []);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const responsables = [...new Set(data.map(d => d["Responsable"]).filter(Boolean))].sort();

  const filtered = data.filter(d => {
    const q = search.toLowerCase();
    const matchSearch = !q ||
      (d["Codigo Meta"] || "").toLowerCase().includes(q) ||
      (d["Línea Estratégica"] || "").toLowerCase().includes(q) ||
      (d["Indicador de producto principal"] || "").toLowerCase().includes(q) ||
      (d["Sector PDD"] || "").toLowerCase().includes(q);
    const matchResponsable = selectedResponsables.length === 0 || selectedResponsables.includes(d["Responsable"]);
    return matchSearch && matchResponsable;
  });

  return (
    <div style={{ fontFamily: font, background: C.surface, minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@600;700&display=swap');
        @keyframes slideIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
        * { box-sizing: border-box; }
        input:focus, textarea:focus, select:focus { border-color: ${C.sky} !important; box-shadow: 0 0 0 3px rgba(37,99,235,.1); }
        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
      `}</style>

      {/* Header */}
      <div style={{ background: `linear-gradient(135deg, ${C.navy} 0%, ${C.steel} 100%)`, padding: "24px 32px 20px" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 800, color: "#64748b", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 4 }}>Sistema de Seguimiento</div>
              <h1 style={{ margin: 0, fontSize: 22, fontWeight: 800, color: "#f8fafc", letterSpacing: "-0.01em" }}>Plan Indicativo Municipal</h1>
              <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>Cuatrienio 2024 – 2027</div>
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              {[["Indicadores", filtered.length + (filtered.length !== data.length ? `/${data.length}` : "")], ["Responsables", responsables.length]].map(([label, val]) => (
                <div key={label} style={{ textAlign: "center", background: "rgba(255,255,255,.07)", borderRadius: 10, padding: "10px 18px" }}>
                  <div style={{ fontSize: 22, fontWeight: 800, color: "#f8fafc" }}>{val}</div>
                  <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 1400, margin: "0 auto", padding: "20px 32px 40px" }}>
        {/* Filters */}
        <div style={{ display: "flex", gap: 10, marginBottom: 16, alignItems: "center" }}>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por código, línea, indicador o sector..."
            style={{
              flex: 1, border: `1.5px solid ${C.border}`, borderRadius: 8,
              padding: "8px 14px", fontSize: 13, fontFamily: font,
              background: C.card, color: C.text, outline: "none",
              transition: "border-color .15s",
            }}
          />
          <MultiSelect
            options={responsables}
            selected={selectedResponsables}
            onChange={setSelectedResponsables}
            placeholder="Filtrar por responsable..."
          />
          {(search || selectedResponsables.length > 0) && (
            <Btn variant="ghost" small onClick={() => { setSearch(""); setSelectedResponsables([]); }}>
              Limpiar
            </Btn>
          )}
        </div>

        {/* Filter chips */}
        {selectedResponsables.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
            {selectedResponsables.map(r => (
              <span key={r} style={{
                background: C.skyLight, color: C.sky, fontSize: 11, fontWeight: 700,
                padding: "3px 10px", borderRadius: 20, display: "flex", alignItems: "center", gap: 6,
              }}>
                {r}
                <span
                  onClick={() => setSelectedResponsables(s => s.filter(x => x !== r))}
                  style={{ cursor: "pointer", fontWeight: 900, fontSize: 13, lineHeight: 1 }}>×</span>
              </span>
            ))}
          </div>
        )}

        {/* Column headers */}
        {!loading && !error && (
          <div style={{
            display: "grid",
            gridTemplateColumns: "28px 160px 1fr 1fr 110px 110px 80px",
            gap: 12, padding: "6px 16px", marginBottom: 4,
          }}>
            {["", "Código Meta", "Línea Estratégica", "Indicador Principal", "Sector PDD", "Tipo Acumulación", "Proyectos"].map(h => (
              <div key={h} style={{ fontSize: 10, fontWeight: 800, color: C.faint, textTransform: "uppercase", letterSpacing: "0.1em" }}>{h}</div>
            ))}
          </div>
        )}

        {/* States */}
        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0", color: C.muted, fontSize: 14 }}>
            Cargando datos desde Supabase...
          </div>
        )}

        {error && (
          <div style={{ background: "#fee2e2", border: `1px solid #fca5a5`, borderRadius: 10, padding: 20, color: C.red, fontSize: 13 }}>
            <strong>Error al conectar con Supabase:</strong><br />{error}
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div style={{ textAlign: "center", padding: "60px 0", color: C.faint, fontSize: 14 }}>
            No se encontraron indicadores con los filtros aplicados.
          </div>
        )}

        {filtered.map((ind, idx) => (
          <IndicadorRow key={ind["Codigo Meta"]} ind={ind} idx={idx} />
        ))}
      </div>
    </div>
  );
}
