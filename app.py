import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import date, datetime, timedelta
from supabase import create_client
import base64

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Inés (Repa 9)",
    page_icon="💗",
    layout="wide"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ESTADOS = [
    "Pendiente",
    "Pidiendo presupuestos",
    "Presupuestos recibidos",
    "Enviado al consejo",
    "Aprobado",
    "En ejecución",
    "Finalizado",
    "Cancelado",
]

PRIORIDADES = ["Baja", "Media", "Alta", "Urgente"]

CATEGORIAS = [
    "Plomería",
    "Electricidad",
    "Ascensor",
    "Pintura",
    "Humedad",
    "Limpieza",
    "Matafuegos",
    "Seguro",
    "Bombas",
    "Administración / reclamo",
    "Otro",
]

ESTADOS_CERRADOS = ["Finalizado", "Cancelado"]

ESTADOS_PROVEEDOR = [
    "Pendiente de contactar",
    "Contactado",
    "Visita coordinada",
    "Visitó el consorcio",
    "Presupuesto recibido",
    "Aprobado",
    "Trabajo en curso",
    "Finalizado",
    "Descartado",
]

# =========================================================
# ESTILOS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(255, 214, 225, 0.34), transparent 24%),
            radial-gradient(circle at top left, rgba(196, 236, 255, 0.28), transparent 28%),
            linear-gradient(180deg, #fff9fb 0%, #f9fcff 100%);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #b76b85;
        letter-spacing: -0.02em;
    }

    .hero-card {
        background:
            linear-gradient(135deg,
                rgba(255,247,250,0.98) 0%,
                rgba(255,252,246,0.96) 38%,
                rgba(245,251,255,0.96) 100%);
        border: 1px solid #f1d8e1;
        border-radius: 30px;
        padding: 26px 30px;
        box-shadow: 0 16px 34px rgba(183, 107, 133, 0.10);
        margin-bottom: 18px;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 150px 1fr;
        gap: 26px;
        align-items: center;
    }

    .hero-logo-box {
        background: rgba(255,255,255,0.78);
        border: 1px solid #f2dce5;
        border-radius: 24px;
        padding: 16px;
        min-height: 116px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.4);
    }

    .hero-logo-box img {
        max-width: 100%;
        max-height: 92px;
        object-fit: contain;
    }

    .hero-title {
        font-size: 2.55rem;
        line-height: 1.05;
        font-weight: 800;
        color: #b46884;
        margin-bottom: 0.2rem;
    }

    .hero-sub {
        color: #7f6e77;
        font-size: 1rem;
        margin-bottom: 0.65rem;
    }

    .hero-mini {
        color: #9a7081;
        font-size: 0.93rem;
    }

    .hero-line {
        height: 1px;
        background: linear-gradient(90deg, rgba(232,195,209,0.85), rgba(232,195,209,0.08));
        margin: 10px 0 12px 0;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(255,252,253,0.93) 100%);
        border: 1px solid #f0d7e1;
        border-radius: 22px;
        padding: 18px;
        box-shadow: 0 10px 26px rgba(183, 107, 133, 0.08);
        min-height: 118px;
    }

    .metric-label {
        font-size: 0.95rem;
        color: #7d6d75;
        margin-bottom: 12px;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #304055;
        line-height: 1;
    }

    .section-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(255,253,254,0.94) 100%);
        border: 1px solid #eef1f6;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(40, 55, 80, 0.05);
    }

    .section-title {
        font-size: 1.22rem;
        font-weight: 800;
        color: #b46884;
        margin-bottom: 0.95rem;
    }

    .small-muted {
        color: #7d6d75;
        font-size: 0.92rem;
    }

    .divider-soft {
        border-top: 1px solid #f1dfe6;
        margin: 12px 0 16px 0;
    }

    .soft-box {
        background: #fff;
        border: 1px solid #ece8ef;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    .alarm-card {
        background: #fff8fb;
        border: 1px solid #f2d3de;
        border-left: 7px solid #e39ab3;
        border-radius: 18px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 6px 16px rgba(180,104,132,0.05);
    }

    .alarm-card.vencida {
        background: #fff1f4;
        border-color: #efbfd0;
        border-left-color: #d94f70;
    }

    .alarm-card.hoy {
        background: #fff8f0;
        border-color: #f2d4a8;
        border-left-color: #e59b3d;
    }

    .alarm-card.proxima {
        background: #f4fbff;
        border-color: #d8e9fb;
        border-left-color: #78a9f6;
    }

    .alarm-title {
        font-weight: 800;
        color: #39485c;
    }

    .alarm-cons {
        color: #b46884;
        font-weight: 700;
    }

    .provider-pill {
        display:inline-block;
        background:#fff5f8;
        border:1px solid #efd4de;
        color:#b46884;
        padding:6px 10px;
        border-radius:999px;
        font-size:0.84rem;
        margin-right:6px;
        margin-bottom:6px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.95);
        border: 1px solid #efd5df;
        border-radius: 14px;
        padding: 9px 16px;
        height: auto;
        color: #8c6677;
        box-shadow: 0 4px 10px rgba(180,104,132,0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #fff6f9 0%, #fffdfd 100%) !important;
        border-color: #e7bfd0 !important;
        color: #b46884 !important;
        font-weight: 700;
    }

    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stNumberInput input {
        border-radius: 14px !important;
    }

    .stButton button,
    .stDownloadButton button {
        border-radius: 14px !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #eef1f6;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def parse_iso_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value)).date()
    except Exception:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except Exception:
            return None

def format_date(value):
    d = parse_iso_date(value)
    if not d:
        return ""
    return d.strftime("%d/%m/%Y")

def to_iso_or_none(value):
    if not value:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)

def money_to_float(value):
    if value is None:
        return None
    txt = str(value).strip().replace(".", "").replace(",", ".")
    if txt == "":
        return None
    try:
        return float(txt)
    except Exception:
        return None

def format_money(value):
    if value in (None, ""):
        return ""
    try:
        num = float(value)
        return f"${num:,.0f}".replace(",", ".")
    except Exception:
        return str(value)

def export_excel(df, sheet_name="Reporte"):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    bio.seek(0)
    return bio

def get_logo_html():
    try:
        with open("ajk_logo.jpg", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/jpeg;base64,{b64}" alt="logo">'
    except Exception:
        return '<div style="font-size:2rem;">💗</div>'

# =========================================================
# SUPABASE - LECTURA SEGURA
# =========================================================
def safe_table_select(table_name, order_by=None, desc=False):
    try:
        q = supabase.table(table_name).select("*")
        if order_by:
            q = q.order(order_by, desc=desc)
        return q.execute().data or []
    except Exception:
        return []

def get_consorcios():
    return safe_table_select("consorcios", "codigo")

def get_tareas(consorcio_id=None):
    try:
        q = supabase.table("tareas").select("*").order("created_at", desc=True)
        if consorcio_id:
            q = q.eq("consorcio_id", consorcio_id)
        return q.execute().data or []
    except Exception:
        return []

def get_historial(tarea_id):
    try:
        return (
            supabase.table("historial_tareas")
            .select("*")
            .eq("tarea_id", tarea_id)
            .order("created_at", desc=True)
            .execute()
            .data
            or []
        )
    except Exception:
        return []

def get_proveedores_tarea(tarea_id):
    try:
        return (
            supabase.table("proveedores_tarea")
            .select("*")
            .eq("tarea_id", tarea_id)
            .order("orden")
            .execute()
            .data
            or []
        )
    except Exception:
        return []

def get_proveedores_base():
    try:
        return (
            supabase.table("proveedores_base")
            .select("*")
            .order("nombre")
            .execute()
            .data
            or []
        )
    except Exception:
        return []

# =========================================================
# SUPABASE - ESCRITURA
# =========================================================
def add_tarea(payload):
    try:
        res = supabase.table("tareas").insert(payload).execute().data
        return res[0] if res else None
    except Exception as e:
        st.error(f"No se pudo guardar la tarea: {e}")
        return None

def update_tarea(tid, payload):
    try:
        supabase.table("tareas").update(payload).eq("id", tid).execute()
        return True
    except Exception as e:
        st.error(f"No se pudo actualizar la tarea: {e}")
        return False

def add_historial(tid, detalle):
    if not detalle or not detalle.strip():
        return
    try:
        supabase.table("historial_tareas").insert({
            "tarea_id": tid,
            "detalle": detalle.strip()
        }).execute()
    except Exception:
        pass

def add_proveedor_tarea(payload):
    try:
        supabase.table("proveedores_tarea").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"No se pudo guardar el proveedor de la tarea: {e}")
        return False

def update_proveedor_tarea(pid, payload):
    try:
        supabase.table("proveedores_tarea").update(payload).eq("id", pid).execute()
        return True
    except Exception as e:
        st.error(f"No se pudo actualizar el proveedor: {e}")
        return False

def add_proveedor_base(payload):
    try:
        supabase.table("proveedores_base").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"No se pudo guardar el proveedor base: {e}")
        return False

# =========================================================
# NEGOCIO
# =========================================================
def cons_codigo(consorcios, cid):
    for c in consorcios:
        if c["id"] == cid:
            return str(c.get("codigo", cid))
    return str(cid)

def cons_label(consorcios, cid):
    for c in consorcios:
        if c["id"] == cid:
            nombre = c.get("nombre", "")
            codigo = c.get("codigo", "")
            return f"{codigo} - {nombre}" if nombre else str(codigo)
    return str(cid)

def tarea_esta_activa(t):
    return t.get("estado") not in ESTADOS_CERRADOS

def tarea_es_urgente(t):
    return t.get("prioridad") == "Urgente" and tarea_esta_activa(t)

def tarea_tiene_alarma(t):
    return bool(t.get("alarma_activa"))

def tarea_pendiente_consejo(t):
    return bool(t.get("requiere_consejo")) and not bool(t.get("enviado_consejo"))

def alarm_status(t):
    if not t.get("alarma_activa"):
        return None, None

    alarma = parse_iso_date(t.get("alarma_fecha"))
    if not alarma:
        return "sin_fecha", "Sin fecha"

    hoy = date.today()
    if alarma < hoy:
        return "vencida", f"Vencida ({format_date(alarma)})"
    if alarma == hoy:
        return "hoy", "Vence hoy"
    if alarma <= hoy + timedelta(days=7):
        return "proxima", f"Próxima ({format_date(alarma)})"
    return "futura", format_date(alarma)

def proveedor_requiere_reclamo(p):
    hoy = date.today()

    visita_prom = parse_iso_date(p.get("fecha_visita_prometida"))
    fue = p.get("fue_al_consorcio")
    presupuesto_rec = p.get("presupuesto_recibido")
    estado = p.get("estado_proveedor", "")

    if visita_prom and visita_prom < hoy and not fue:
        return "No fue a la visita prometida"

    if fue and not presupuesto_rec and estado in ["Visitó el consorcio", "Presupuesto recibido", "Aprobado", "Trabajo en curso"]:
        return "Visitó pero falta presupuesto"

    return None

def build_tareas_table(consorcios, tareas):
    rows = []
    for t in tareas:
        rows.append({
            "Consorcio": cons_codigo(consorcios, t["consorcio_id"]),
            "Título": t.get("titulo", ""),
            "Categoría": t.get("tipo_gestion", ""),
            "Prioridad": t.get("prioridad", ""),
            "Estado": t.get("estado", ""),
            "Fecha límite": format_date(t.get("fecha_limite")),
            "Alarma": format_date(t.get("alarma_fecha")) if t.get("alarma_activa") else "",
            "Consejo": "Pendiente" if tarea_pendiente_consejo(t) else ("Enviado" if t.get("requiere_consejo") else ""),
            "Próximo paso": t.get("proximo_paso", ""),
        })
    return pd.DataFrame(rows)

def build_weekly_report_df(consorcios, tareas):
    rows = []
    for t in tareas:
        rows.append({
            "Consorcio": cons_codigo(consorcios, t["consorcio_id"]),
            "Título": t.get("titulo", ""),
            "Detalle": t.get("descripcion", ""),
            "Categoría": t.get("tipo_gestion", ""),
            "Prioridad": t.get("prioridad", ""),
            "Estado": t.get("estado", ""),
            "Fecha límite": format_date(t.get("fecha_limite")),
            "Próximo paso": t.get("proximo_paso", ""),
            "Requiere consejo": "Sí" if t.get("requiere_consejo") else "No",
            "Enviado al consejo": "Sí" if t.get("enviado_consejo") else "No",
            "Alarma": format_date(t.get("alarma_fecha")) if t.get("alarma_activa") else "",
            "Motivo alarma": t.get("alarma_motivo", "") if t.get("alarma_activa") else "",
            "Observaciones": t.get("observaciones", ""),
        })
    return pd.DataFrame(rows)

# =========================================================
# DATOS
# =========================================================
consorcios = get_consorcios()
logo_html = get_logo_html()

# =========================================================
# HEADER
# =========================================================
st.markdown(f"""
<div class="hero-card">
    <div class="hero-grid">
        <div class="hero-logo-box">
            {logo_html}
        </div>
        <div>
            <div class="hero-title">Inés (Repa 9)</div>
            <div class="hero-sub">Panel personal de seguimiento</div>
            <div class="hero-line"></div>
            <div class="hero-mini">
                Seguimiento de consorcios, tareas, presupuestos, consejo, proveedores y reportes ♡
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Inicio",
    "Nueva tarea",
    "Tareas",
    "Proveedores",
    "Reporte por consorcio",
    "Reporte semanal",
])

# =========================================================
# TAB 1 - INICIO
# =========================================================
with tab1:
    tareas = get_tareas()

    activas = [t for t in tareas if tarea_esta_activa(t)]
    urgentes = [t for t in tareas if tarea_es_urgente(t)]
    con_alarma = [t for t in tareas if tarea_tiene_alarma(t)]
    pendientes_consejo = [t for t in tareas if tarea_pendiente_consejo(t)]

    # Reclamos de proveedores
    reclamos_prov = []
    for t in tareas:
        provs = get_proveedores_tarea(t["id"])
        for p in provs:
            motivo = proveedor_requiere_reclamo(p)
            if motivo:
                reclamos_prov.append({
                    "consorcio": cons_codigo(consorcios, t["consorcio_id"]),
                    "tarea": t.get("titulo", ""),
                    "proveedor": p.get("nombre", ""),
                    "motivo": motivo
                })

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tareas activas</div>
            <div class="metric-value">{len(activas)}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Urgentes</div>
            <div class="metric-value">{len(urgentes)}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Con alarma</div>
            <div class="metric-value">{len(con_alarma)}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pendientes de consejo</div>
            <div class="metric-value">{len(pendientes_consejo)}</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Reclamos a proveedores</div>
            <div class="metric-value">{len(reclamos_prov)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_alarmas, col_reclamos = st.columns(2)

    with col_alarmas:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Alarmas pendientes</div>', unsafe_allow_html=True)

        alarmas_ordenadas = []
        for t in con_alarma:
            tipo, etiqueta = alarm_status(t)
            prioridad = {"vencida": 0, "hoy": 1, "proxima": 2, "futura": 3, "sin_fecha": 4}.get(tipo, 5)
            alarmas_ordenadas.append((prioridad, t, tipo, etiqueta))

        alarmas_ordenadas.sort(key=lambda x: x[0])

        if not alarmas_ordenadas:
            st.info("No hay alarmas cargadas.")
        else:
            for _, t, tipo, etiqueta in alarmas_ordenadas:
                clase = "alarm-card"
                if tipo == "vencida":
                    clase += " vencida"
                elif tipo == "hoy":
                    clase += " hoy"
                elif tipo == "proxima":
                    clase += " proxima"

                motivo = t.get("alarma_motivo") or "Sin motivo cargado"

                st.markdown(f"""
                <div class="{clase}">
                    <div class="alarm-cons">Consorcio {cons_codigo(consorcios, t["consorcio_id"])}</div>
                    <div class="alarm-title">{t.get("titulo","(sin título)")}</div>
                    <div class="small-muted">{etiqueta}</div>
                    <div style="margin-top:4px;">{motivo}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_reclamos:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Proveedores para reclamar</div>', unsafe_allow_html=True)

        if not reclamos_prov:
            st.info("No hay reclamos pendientes de proveedores.")
        else:
            for r in reclamos_prov[:20]:
                st.markdown(f"""
                <div class="soft-box">
                    <strong>Consorcio {r['consorcio']}</strong><br>
                    <strong>{r['proveedor']}</strong><br>
                    Tarea: {r['tarea']}<br>
                    <span class="small-muted">{r['motivo']}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Vista rápida de tareas</div>', unsafe_allow_html=True)

    if tareas:
        df_inicio = build_tareas_table(consorcios, tareas)
        st.dataframe(df_inicio, use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay tareas cargadas.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 2 - NUEVA TAREA
# =========================================================
with tab2:
    proveedores_base = get_proveedores_base()

    if not consorcios:
        st.warning("No hay consorcios cargados en la base.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Cargar nueva tarea</div>', unsafe_allow_html=True)

        with st.form("nueva_tarea_form"):
            c1, c2 = st.columns(2)

            with c1:
                cons = st.selectbox(
                    "Consorcio",
                    consorcios,
                    format_func=lambda c: str(c.get("codigo", ""))
                )
                titulo = st.text_input("Título / asunto")
                detalle = st.text_area("Detalle")
                categoria = st.selectbox("Categoría", CATEGORIAS)
                prioridad = st.selectbox("Prioridad", PRIORIDADES, index=1)

            with c2:
                estado = st.selectbox("Estado", ESTADOS, index=0)
                fecha_limite = st.date_input("Fecha límite", value=None, format="DD/MM/YYYY")
                proximo_paso = st.text_input("Próximo paso")
                requiere_consejo = st.checkbox("Requiere enviar al consejo")
                enviado_consejo = st.checkbox("Ya fue enviado al consejo")

            st.markdown("### Alarma interna")
            a1, a2 = st.columns([1, 1.2])
            with a1:
                alarma_activa = st.checkbox("Activar alarma")
                alarma_fecha = st.date_input("Fecha del recordatorio", value=None, format="DD/MM/YYYY")
            with a2:
                alarma_motivo = st.text_input("Motivo del recordatorio")

            st.markdown("### Proveedores de esta tarea")
            st.caption("Podés cargar hasta 5. Si el proveedor ya existe en la base, podés elegirlo.")

            proveedores_payload = []

            for i in range(1, 6):
                st.markdown(f"**Proveedor {i}**")
                p0, p1 = st.columns([1.2, 1.2])

                with p0:
                    usar_base = st.checkbox("Elegir de base", key=f"usar_base_{i}")
                    prov_base_id = None
                    prov_nombre = ""
                    prov_tel = ""
                    prov_mail = ""

                    if usar_base and proveedores_base:
                        elegido = st.selectbox(
                            "Proveedor guardado",
                            options=[None] + proveedores_base,
                            format_func=lambda p: "—" if p is None else p.get("nombre", ""),
                            key=f"base_sel_{i}"
                        )
                        if elegido:
                            prov_base_id = elegido.get("id")
                            prov_nombre = elegido.get("nombre", "")
                            prov_tel = elegido.get("telefono", "")
                            prov_mail = elegido.get("email", "")
                    else:
                        prov_nombre = st.text_input("Nombre", key=f"nuevo_p_nombre_{i}")

                    estado_prov = st.selectbox("Estado del proveedor", ESTADOS_PROVEEDOR, key=f"estado_prov_{i}")
                    fecha_contacto = st.date_input("Fecha de contacto", value=None, format="DD/MM/YYYY", key=f"f_contacto_{i}")
                    fecha_visita_prometida = st.date_input("Fecha prometida de visita", value=None, format="DD/MM/YYYY", key=f"f_visita_prom_{i}")

                with p1:
                    fue_al_consorcio = st.checkbox("Fue al consorcio", key=f"fue_{i}")
                    fecha_visita_real = st.date_input("Fecha real de visita", value=None, format="DD/MM/YYYY", key=f"f_visita_real_{i}")
                    presupuesto_recibido = st.checkbox("Presupuesto recibido", key=f"pres_rec_{i}")
                    fecha_presupuesto = st.date_input("Fecha presupuesto", value=None, format="DD/MM/YYYY", key=f"f_pres_{i}")
                    monto = st.text_input("Monto", key=f"monto_{i}")

                p2, p3 = st.columns(2)
                with p2:
                    aprobado = st.checkbox("Proveedor aprobado", key=f"aprobado_{i}")
                    fecha_inicio = st.date_input("Fecha de inicio", value=None, format="DD/MM/YYYY", key=f"f_inicio_{i}")
                with p3:
                    fecha_fin = st.date_input("Fecha de finalización", value=None, format="DD/MM/YYYY", key=f"f_fin_{i}")
                    observaciones_prov = st.text_area("Observaciones del proveedor", key=f"obs_prov_{i}")

                proveedores_payload.append({
                    "orden": i,
                    "proveedor_base_id": prov_base_id,
                    "nombre": prov_nombre,
                    "estado_proveedor": estado_prov,
                    "fecha_contacto": to_iso_or_none(fecha_contacto),
                    "fecha_visita_prometida": to_iso_or_none(fecha_visita_prometida),
                    "fue_al_consorcio": fue_al_consorcio,
                    "fecha_visita_real": to_iso_or_none(fecha_visita_real),
                    "presupuesto_recibido": presupuesto_recibido,
                    "fecha_presupuesto": to_iso_or_none(fecha_presupuesto),
                    "monto": money_to_float(monto),
                    "aprobado": aprobado,
                    "fecha_inicio": to_iso_or_none(fecha_inicio),
                    "fecha_fin": to_iso_or_none(fecha_fin),
                    "observaciones": observaciones_prov,
                    "telefono": prov_tel,
                    "email": prov_mail,
                })

                st.markdown("<div class='divider-soft'></div>", unsafe_allow_html=True)

            observaciones = st.text_area("Observaciones generales de la tarea")
            primer_mov = st.text_area("Primer movimiento / nota interna")

            guardar = st.form_submit_button("Guardar tarea")

            if guardar:
                if not titulo.strip():
                    st.error("La tarea necesita un título.")
                else:
                    payload = {
                        "consorcio_id": cons["id"],
                        "titulo": titulo.strip(),
                        "descripcion": detalle.strip() if detalle else "",
                        "tipo_gestion": categoria,
                        "prioridad": prioridad,
                        "estado": estado,
                        "fecha_limite": to_iso_or_none(fecha_limite),
                        "proximo_paso": proximo_paso.strip() if proximo_paso else "",
                        "requiere_consejo": requiere_consejo,
                        "enviado_consejo": enviado_consejo,
                        "observaciones": observaciones.strip() if observaciones else "",
                        "alarma_activa": alarma_activa,
                        "alarma_fecha": to_iso_or_none(alarma_fecha) if alarma_activa else None,
                        "alarma_motivo": alarma_motivo.strip() if alarma_motivo else None,
                    }

                    tarea = add_tarea(payload)

                    if tarea:
                        for p in proveedores_payload:
                            if str(p.get("nombre", "")).strip():
                                add_proveedor_tarea({
                                    "tarea_id": tarea["id"],
                                    "orden": p["orden"],
                                    "proveedor_base_id": p.get("proveedor_base_id"),
                                    "nombre": p.get("nombre", "").strip(),
                                    "estado_proveedor": p.get("estado_proveedor"),
                                    "fecha_contacto": p.get("fecha_contacto"),
                                    "fecha_visita_prometida": p.get("fecha_visita_prometida"),
                                    "fue_al_consorcio": p.get("fue_al_consorcio"),
                                    "fecha_visita_real": p.get("fecha_visita_real"),
                                    "presupuesto_recibido": p.get("presupuesto_recibido"),
                                    "fecha_presupuesto": p.get("fecha_presupuesto"),
                                    "monto": p.get("monto"),
                                    "aprobado": p.get("aprobado"),
                                    "fecha_inicio": p.get("fecha_inicio"),
                                    "fecha_fin": p.get("fecha_fin"),
                                    "observaciones": p.get("observaciones"),
                                    "telefono": p.get("telefono"),
                                    "email": p.get("email"),
                                })

                        if primer_mov.strip():
                            add_historial(tarea["id"], primer_mov)

                        st.success("Tarea guardada.")
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 3 - TAREAS
# =========================================================
with tab3:
    tareas = get_tareas()
    proveedores_base = get_proveedores_base()

    if not tareas:
        st.info("No hay tareas cargadas.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Editar tareas y seguimiento</div>', unsafe_allow_html=True)

        filtro_cons = st.selectbox(
            "Filtrar por consorcio",
            ["Todos"] + [c["id"] for c in consorcios],
            format_func=lambda x: "Todos" if x == "Todos" else str(next((c["codigo"] for c in consorcios if c["id"] == x), x))
        )

        tareas_f = tareas if filtro_cons == "Todos" else [t for t in tareas if t["consorcio_id"] == filtro_cons]

        if not tareas_f:
            st.info("No hay tareas para ese filtro.")
        else:
            opciones = {
                f'{cons_codigo(consorcios, t["consorcio_id"])} | {t.get("titulo","(sin título)")}': t
                for t in tareas_f
            }
            tarea = opciones[st.selectbox("Elegí tarea", list(opciones.keys()))]
            proveedores = get_proveedores_tarea(tarea["id"])
            historial = get_historial(tarea["id"])

            st.markdown("### Datos de la tarea")
            with st.form(f"editar_tarea_{tarea['id']}"):
                e1, e2 = st.columns(2)

                with e1:
                    titulo = st.text_input("Título", value=tarea.get("titulo", ""))
                    detalle = st.text_area("Detalle", value=tarea.get("descripcion", ""))
                    categoria_actual = tarea.get("tipo_gestion", "Otro")
                    if categoria_actual not in CATEGORIAS:
                        categoria_actual = "Otro"
                    categoria = st.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(categoria_actual))
                    prioridad_actual = tarea.get("prioridad", "Media")
                    if prioridad_actual not in PRIORIDADES:
                        prioridad_actual = "Media"
                    prioridad = st.selectbox("Prioridad", PRIORIDADES, index=PRIORIDADES.index(prioridad_actual))

                with e2:
                    estado_actual = tarea.get("estado", "Pendiente")
                    if estado_actual not in ESTADOS:
                        estado_actual = "Pendiente"
                    estado = st.selectbox("Estado", ESTADOS, index=ESTADOS.index(estado_actual))
                    fecha_limite = st.date_input("Fecha límite", value=parse_iso_date(tarea.get("fecha_limite")), format="DD/MM/YYYY")
                    proximo_paso = st.text_input("Próximo paso", value=tarea.get("proximo_paso", ""))
                    requiere_consejo = st.checkbox("Requiere consejo", value=tarea.get("requiere_consejo", False))
                    enviado_consejo = st.checkbox("Enviado al consejo", value=tarea.get("enviado_consejo", False))

                st.markdown("### Alarma")
                a1, a2 = st.columns([1, 1.2])
                with a1:
                    alarma_activa = st.checkbox("Activar alarma", value=tarea.get("alarma_activa", False))
                    alarma_fecha = st.date_input("Fecha de alarma", value=parse_iso_date(tarea.get("alarma_fecha")), format="DD/MM/YYYY")
                with a2:
                    alarma_motivo = st.text_input("Motivo de alarma", value=tarea.get("alarma_motivo") or "")

                observaciones = st.text_area("Observaciones", value=tarea.get("observaciones", ""))
                nuevo_mov = st.text_area("Agregar movimiento al historial")
                save = st.form_submit_button("Guardar cambios")

                if save:
                    ok = update_tarea(tarea["id"], {
                        "titulo": titulo.strip(),
                        "descripcion": detalle.strip() if detalle else "",
                        "tipo_gestion": categoria,
                        "prioridad": prioridad,
                        "estado": estado,
                        "fecha_limite": to_iso_or_none(fecha_limite),
                        "proximo_paso": proximo_paso.strip() if proximo_paso else "",
                        "requiere_consejo": requiere_consejo,
                        "enviado_consejo": enviado_consejo,
                        "alarma_activa": alarma_activa,
                        "alarma_fecha": to_iso_or_none(alarma_fecha) if alarma_activa else None,
                        "alarma_motivo": alarma_motivo.strip() if alarma_motivo else None,
                        "observaciones": observaciones.strip() if observaciones else "",
                    })
                    if ok and nuevo_mov.strip():
                        add_historial(tarea["id"], nuevo_mov.strip())
                    if ok:
                        st.success("Cambios guardados.")
                        st.rerun()

            st.markdown("<div class='divider-soft'></div>", unsafe_allow_html=True)

            st.markdown("### Proveedores de esta tarea")
            if proveedores:
                for p in proveedores:
                    titulo_exp = f"Proveedor #{p.get('orden', '')}: {p.get('nombre', 'Sin nombre')}"
                    with st.expander(titulo_exp):
                        with st.form(f"prov_{p['id']}"):
                            c1, c2 = st.columns(2)

                            with c1:
                                p_nombre = st.text_input("Nombre", value=p.get("nombre", ""))
                                estado_prov_actual = p.get("estado_proveedor", ESTADOS_PROVEEDOR[0])
                                if estado_prov_actual not in ESTADOS_PROVEEDOR:
                                    estado_prov_actual = ESTADOS_PROVEEDOR[0]
                                estado_prov = st.selectbox("Estado del proveedor", ESTADOS_PROVEEDOR, index=ESTADOS_PROVEEDOR.index(estado_prov_actual))
                                fecha_contacto = st.date_input("Fecha de contacto", value=parse_iso_date(p.get("fecha_contacto")), format="DD/MM/YYYY")
                                fecha_visita_prom = st.date_input("Fecha prometida de visita", value=parse_iso_date(p.get("fecha_visita_prometida")), format="DD/MM/YYYY")
                                fue = st.checkbox("Fue al consorcio", value=p.get("fue_al_consorcio", False))
                                fecha_visita_real = st.date_input("Fecha real de visita", value=parse_iso_date(p.get("fecha_visita_real")), format="DD/MM/YYYY")

                            with c2:
                                presupuesto_recibido = st.checkbox("Presupuesto recibido", value=p.get("presupuesto_recibido", False))
                                fecha_presupuesto = st.date_input("Fecha presupuesto", value=parse_iso_date(p.get("fecha_presupuesto")), format="DD/MM/YYYY")
                                monto = st.text_input("Monto", value="" if p.get("monto") is None else str(p.get("monto")))
                                aprobado = st.checkbox("Aprobado", value=p.get("aprobado", False))
                                fecha_inicio = st.date_input("Fecha inicio", value=parse_iso_date(p.get("fecha_inicio")), format="DD/MM/YYYY")
                                fecha_fin = st.date_input("Fecha fin", value=parse_iso_date(p.get("fecha_fin")), format="DD/MM/YYYY")

                            observaciones_p = st.text_area("Observaciones del proveedor", value=p.get("observaciones", ""))

                            guardar_prov = st.form_submit_button("Guardar proveedor")
                            if guardar_prov:
                                ok = update_proveedor_tarea(p["id"], {
                                    "nombre": p_nombre.strip(),
                                    "estado_proveedor": estado_prov,
                                    "fecha_contacto": to_iso_or_none(fecha_contacto),
                                    "fecha_visita_prometida": to_iso_or_none(fecha_visita_prom),
                                    "fue_al_consorcio": fue,
                                    "fecha_visita_real": to_iso_or_none(fecha_visita_real),
                                    "presupuesto_recibido": presupuesto_recibido,
                                    "fecha_presupuesto": to_iso_or_none(fecha_presupuesto),
                                    "monto": money_to_float(monto),
                                    "aprobado": aprobado,
                                    "fecha_inicio": to_iso_or_none(fecha_inicio),
                                    "fecha_fin": to_iso_or_none(fecha_fin),
                                    "observaciones": observaciones_p.strip() if observaciones_p else "",
                                })
                                if ok:
                                    st.success("Proveedor actualizado.")
                                    st.rerun()
            else:
                st.caption("Esta tarea no tiene proveedores cargados.")

            with st.expander("Agregar proveedor a esta tarea"):
                with st.form(f"nuevo_prov_{tarea['id']}"):
                    usar_base = st.checkbox("Elegir proveedor desde la base")
                    proveedor_base_id = None
                    nombre = ""
                    telefono = ""
                    email = ""

                    if usar_base and proveedores_base:
                        elegido = st.selectbox(
                            "Proveedor",
                            options=[None] + proveedores_base,
                            format_func=lambda p: "—" if p is None else p.get("nombre", "")
                        )
                        if elegido:
                            proveedor_base_id = elegido.get("id")
                            nombre = elegido.get("nombre", "")
                            telefono = elegido.get("telefono", "")
                            email = elegido.get("email", "")
                    else:
                        nombre = st.text_input("Nombre")

                    c1, c2 = st.columns(2)
                    with c1:
                        estado_prov = st.selectbox("Estado del proveedor", ESTADOS_PROVEEDOR)
                        fecha_contacto = st.date_input("Fecha de contacto", value=None, format="DD/MM/YYYY")
                        fecha_visita_prom = st.date_input("Fecha prometida de visita", value=None, format="DD/MM/YYYY")
                        fue = st.checkbox("Fue al consorcio")
                    with c2:
                        fecha_visita_real = st.date_input("Fecha real de visita", value=None, format="DD/MM/YYYY")
                        presupuesto_recibido = st.checkbox("Presupuesto recibido")
                        fecha_presupuesto = st.date_input("Fecha presupuesto", value=None, format="DD/MM/YYYY")
                        monto = st.text_input("Monto")

                    aprobado = st.checkbox("Aprobado")
                    fecha_inicio = st.date_input("Fecha inicio", value=None, format="DD/MM/YYYY")
                    fecha_fin = st.date_input("Fecha fin", value=None, format="DD/MM/YYYY")
                    observaciones_p = st.text_area("Observaciones")

                    agregar_prov = st.form_submit_button("Agregar proveedor")
                    if agregar_prov:
                        if not nombre.strip():
                            st.error("Escribí el nombre del proveedor.")
                        else:
                            orden_nuevo = len(proveedores) + 1
                            ok = add_proveedor_tarea({
                                "tarea_id": tarea["id"],
                                "orden": orden_nuevo,
                                "proveedor_base_id": proveedor_base_id,
                                "nombre": nombre.strip(),
                                "telefono": telefono,
                                "email": email,
                                "estado_proveedor": estado_prov,
                                "fecha_contacto": to_iso_or_none(fecha_contacto),
                                "fecha_visita_prometida": to_iso_or_none(fecha_visita_prom),
                                "fue_al_consorcio": fue,
                                "fecha_visita_real": to_iso_or_none(fecha_visita_real),
                                "presupuesto_recibido": presupuesto_recibido,
                                "fecha_presupuesto": to_iso_or_none(fecha_presupuesto),
                                "monto": money_to_float(monto),
                                "aprobado": aprobado,
                                "fecha_inicio": to_iso_or_none(fecha_inicio),
                                "fecha_fin": to_iso_or_none(fecha_fin),
                                "observaciones": observaciones_p.strip() if observaciones_p else "",
                            })
                            if ok:
                                st.success("Proveedor agregado.")
                                st.rerun()

            st.markdown("<div class='divider-soft'></div>", unsafe_allow_html=True)

            st.markdown("### Historial de movimientos")
            if historial:
                for h in historial:
                    fecha_h = h.get("created_at", "") or ""
                    st.markdown(f"""
                    <div class="soft-box">
                        <strong>{fecha_h}</strong><br>
                        {h.get("detalle", "")}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Sin movimientos registrados.")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 4 - PROVEEDORES
# =========================================================
with tab4:
    proveedores_base = get_proveedores_base()
    tareas = get_tareas()

    subt1, subt2, subt3 = st.tabs([
        "Base de proveedores",
        "Agenda / seguimiento",
        "Pendientes de reclamar"
    ])

    # -----------------------------------------------------
    # SUBTAB 1 - BASE
    # -----------------------------------------------------
    with subt1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Base de proveedores</div>', unsafe_allow_html=True)

        with st.expander("Agregar proveedor a la base"):
            with st.form("nuevo_proveedor_base"):
                c1, c2 = st.columns(2)
                with c1:
                    nombre = st.text_input("Nombre")
                    telefono = st.text_input("Teléfono")
                with c2:
                    email = st.text_input("Email")
                    rubro = st.text_input("Rubro")
                observaciones = st.text_area("Observaciones")
                guardar = st.form_submit_button("Guardar proveedor")
                if guardar:
                    if not nombre.strip():
                        st.error("El proveedor necesita un nombre.")
                    else:
                        ok = add_proveedor_base({
                            "nombre": nombre.strip(),
                            "telefono": telefono.strip() if telefono else "",
                            "email": email.strip() if email else "",
                            "rubro": rubro.strip() if rubro else "",
                            "observaciones": observaciones.strip() if observaciones else "",
                        })
                        if ok:
                            st.success("Proveedor guardado.")
                            st.rerun()

        if proveedores_base:
            rows = []
            for p in proveedores_base:
                rows.append({
                    "Nombre": p.get("nombre", ""),
                    "Teléfono": p.get("telefono", ""),
                    "Email": p.get("email", ""),
                    "Rubro": p.get("rubro", ""),
                    "Observaciones": p.get("observaciones", ""),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay proveedores en la base.")

        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBTAB 2 - AGENDA / SEGUIMIENTO
    # -----------------------------------------------------
    with subt2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Agenda / seguimiento del proveedor</div>', unsafe_allow_html=True)

        agenda_rows = []
        for t in tareas:
            provs = get_proveedores_tarea(t["id"])
            for p in provs:
                agenda_rows.append({
                    "Consorcio": cons_codigo(consorcios, t["consorcio_id"]),
                    "Tarea": t.get("titulo", ""),
                    "Proveedor": p.get("nombre", ""),
                    "Estado proveedor": p.get("estado_proveedor", ""),
                    "Visita prometida": format_date(p.get("fecha_visita_prometida")),
                    "Fue": "Sí" if p.get("fue_al_consorcio") else "No",
                    "Visita real": format_date(p.get("fecha_visita_real")),
                    "Presupuesto": "Sí" if p.get("presupuesto_recibido") else "No",
                    "Fecha presupuesto": format_date(p.get("fecha_presupuesto")),
                    "Monto": format_money(p.get("monto")),
                    "Aprobado": "Sí" if p.get("aprobado") else "No",
                    "Inicio": format_date(p.get("fecha_inicio")),
                    "Fin": format_date(p.get("fecha_fin")),
                    "Observaciones": p.get("observaciones", ""),
                })

        if agenda_rows:
            df_agenda = pd.DataFrame(agenda_rows)
            proveedores_unicos = ["Todos"] + sorted(df_agenda["Proveedor"].dropna().unique().tolist())
            prov_sel = st.selectbox("Elegí proveedor", proveedores_unicos)

            if prov_sel != "Todos":
                df_agenda = df_agenda[df_agenda["Proveedor"] == prov_sel]

            st.dataframe(df_agenda, use_container_width=True, hide_index=True)

            st.download_button(
                "Descargar agenda de proveedores",
                data=export_excel(df_agenda, "Proveedores"),
                file_name=f"agenda_proveedores_{date.today().isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Todavía no hay proveedores asociados a tareas.")

        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBTAB 3 - RECLAMOS
    # -----------------------------------------------------
    with subt3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Pendientes de reclamar</div>', unsafe_allow_html=True)

        reclamos = []
        for t in tareas:
            provs = get_proveedores_tarea(t["id"])
            for p in provs:
                motivo = proveedor_requiere_reclamo(p)
                if motivo:
                    reclamos.append({
                        "Consorcio": cons_codigo(consorcios, t["consorcio_id"]),
                        "Tarea": t.get("titulo", ""),
                        "Proveedor": p.get("nombre", ""),
                        "Motivo": motivo,
                        "Visita prometida": format_date(p.get("fecha_visita_prometida")),
                        "Observaciones": p.get("observaciones", ""),
                    })

        if reclamos:
            df_rec = pd.DataFrame(reclamos)
            st.dataframe(df_rec, use_container_width=True, hide_index=True)
            st.download_button(
                "Descargar reclamos pendientes",
                data=export_excel(df_rec, "Reclamos"),
                file_name=f"reclamos_proveedores_{date.today().isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay reclamos pendientes de proveedores.")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 5 - REPORTE POR CONSORCIO
# =========================================================
with tab5:
    if not consorcios:
        st.warning("No hay consorcios cargados.")
    else:
        cons = st.selectbox(
            "Elegí el consorcio",
            consorcios,
            format_func=lambda c: str(c.get("codigo", ""))
        )

        tareas_cons = get_tareas(cons["id"])

        if not tareas_cons:
            st.info("Ese consorcio no tiene tareas.")
        else:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">Consorcio {cons.get("codigo","")}</div>', unsafe_allow_html=True)
            st.caption("Incluye todas las tareas del consorcio, incluso finalizadas y canceladas.")

            texto = []
            rows = []

            for i, t in enumerate(tareas_cons, start=1):
                texto.append(f"{i}. {t.get('titulo','(sin título)')} — {t.get('estado','')}")
                if t.get("descripcion"):
                    texto.append(f"   Detalle: {t['descripcion']}")
                if t.get("tipo_gestion"):
                    texto.append(f"   Categoría: {t['tipo_gestion']}")
                if t.get("prioridad"):
                    texto.append(f"   Prioridad: {t['prioridad']}")
                if t.get("fecha_limite"):
                    texto.append(f"   Fecha límite: {format_date(t['fecha_limite'])}")
                if t.get("proximo_paso"):
                    texto.append(f"   Próximo paso: {t['proximo_paso']}")

                if t.get("requiere_consejo"):
                    texto.append(f"   Consejo: {'enviado' if t.get('enviado_consejo') else 'pendiente de envío'}")

                if t.get("alarma_activa"):
                    alarma_txt = format_date(t.get("alarma_fecha"))
                    motivo = t.get("alarma_motivo") or ""
                    texto.append(f"   Alarma: {alarma_txt} {('- ' + motivo) if motivo else ''}")

                provs = get_proveedores_tarea(t["id"])
                if provs:
                    texto.append("   Proveedores:")
                    for p in provs:
                        partes = [p.get("nombre", "Proveedor")]
                        if p.get("estado_proveedor"):
                            partes.append(p.get("estado_proveedor"))
                        if p.get("monto") is not None:
                            partes.append(f"monto: {format_money(p['monto'])}")
                        texto.append("   - " + " | ".join(partes))

                texto.append("")

                rows.append({
                    "Título": t.get("titulo", ""),
                    "Estado": t.get("estado", ""),
                    "Categoría": t.get("tipo_gestion", ""),
                    "Prioridad": t.get("prioridad", ""),
                    "Fecha límite": format_date(t.get("fecha_limite")),
                    "Próximo paso": t.get("proximo_paso", ""),
                    "Requiere consejo": "Sí" if t.get("requiere_consejo") else "No",
                    "Enviado al consejo": "Sí" if t.get("enviado_consejo") else "No",
                    "Alarma": format_date(t.get("alarma_fecha")) if t.get("alarma_activa") else "",
                    "Motivo alarma": t.get("alarma_motivo", "") if t.get("alarma_activa") else "",
                    "Observaciones": t.get("observaciones", ""),
                })

            st.text_area("Resumen del consorcio", value="\n".join(texto), height=520)

            df_rep = pd.DataFrame(rows)
            st.dataframe(df_rep, use_container_width=True, hide_index=True)

            st.download_button(
                "Descargar Excel del consorcio",
                data=export_excel(df_rep, "Consorcio"),
                file_name=f"reporte_consorcio_{cons.get('codigo','')}_{date.today().isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 6 - REPORTE SEMANAL
# =========================================================
with tab6:
    tareas = get_tareas()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Reporte semanal general</div>', unsafe_allow_html=True)
    st.caption("Este reporte incluye todas las tareas de todos los consorcios, no solo las movidas de la semana.")

    if tareas:
        df_week = build_weekly_report_df(consorcios, tareas)
        st.dataframe(df_week, use_container_width=True, hide_index=True)

        st.download_button(
            "Descargar reporte semanal",
            data=export_excel(df_week, "Reporte semanal"),
            file_name=f"reporte_semanal_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay tareas cargadas.")

    st.markdown('</div>', unsafe_allow_html=True)
