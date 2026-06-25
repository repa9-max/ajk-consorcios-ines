import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import date, datetime, timedelta
from supabase import create_client

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="AJK Consorcios",
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

# =========================================================
# ESTILOS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(255, 209, 220, 0.35), transparent 25%),
            radial-gradient(circle at top left, rgba(191, 236, 255, 0.28), transparent 30%),
            linear-gradient(180deg, #fff9fb 0%, #f8fcff 100%);
    }

    .block-container {
        max-width: 1420px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #b76b85;
        letter-spacing: -0.02em;
    }

    /* ---------- HERO ---------- */
    .hero-card {
        background:
            linear-gradient(135deg,
                rgba(255, 247, 250, 0.98) 0%,
                rgba(255, 252, 247, 0.96) 35%,
                rgba(245, 252, 255, 0.96) 100%);
        border: 1px solid #f1d8e1;
        border-radius: 30px;
        padding: 26px 28px;
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
        font-size: 2.6rem;
        line-height: 1.05;
        font-weight: 800;
        color: #b46884;
        margin-bottom: 0.35rem;
    }

    .hero-sub {
        color: #7f6e77;
        font-size: 1rem;
        margin-bottom: 0.85rem;
    }

    .hero-line {
        height: 1px;
        background: linear-gradient(90deg, rgba(232,195,209,0.8), rgba(232,195,209,0.08));
        margin: 10px 0 12px 0;
    }

    .hero-mini {
        color: #9a7081;
        font-size: 0.92rem;
    }

    .heart-soft {
        color: #d78ca7;
        font-weight: 700;
    }

    /* ---------- MÉTRICAS ---------- */
    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(255,252,253,0.93) 100%);
        border: 1px solid #f0d7e1;
        border-radius: 22px;
        padding: 18px 18px;
        box-shadow: 0 10px 26px rgba(183, 107, 133, 0.08);
        min-height: 120px;
    }

    .metric-label {
        font-size: 0.96rem;
        color: #7d6d75;
        margin-bottom: 12px;
    }

    .metric-value {
        font-size: 2.25rem;
        font-weight: 800;
        color: #304055;
        line-height: 1;
    }

    /* ---------- TARJETAS ---------- */
    .section-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(255,253,254,0.94) 100%);
        border: 1px solid #eef1f6;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(40, 55, 80, 0.05);
    }

    .section-title {
        font-size: 1.25rem;
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

    /* ---------- ALARMAS ---------- */
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

    /* ---------- BOXES ---------- */
    .soft-box {
        background: #fff;
        border: 1px solid #ece8ef;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    .report-box {
        background: #fffdfd;
        border: 1px solid #f0e5eb;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* ---------- TABS ---------- */
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

    /* ---------- INPUTS ---------- */
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

    /* ---------- DATAFRAME ---------- */
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

def export_excel(df):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
    bio.seek(0)
    return bio

# =========================================================
# SUPABASE
# =========================================================
def get_consorcios():
    try:
        return supabase.table("consorcios").select("*").order("codigo").execute().data or []
    except Exception:
        return []

def get_tareas(consorcio_id=None):
    try:
        q = supabase.table("tareas").select("*").order("created_at", desc=True)
        if consorcio_id:
            q = q.eq("consorcio_id", consorcio_id)
        return q.execute().data or []
    except Exception:
        return []

def get_proveedores(tarea_id):
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

def get_historial(tarea_id):
    try:
        return (
            supabase.table("historial_tareas")
            .select("*")
            .eq("tarea_id", tarea_id)
            .order("fecha", desc=True)
            .execute()
            .data
            or []
        )
    except Exception:
        return []

def add_tarea(payload):
    res = supabase.table("tareas").insert(payload).execute().data
    return res[0] if res else None

def update_tarea(tid, payload):
    supabase.table("tareas").update(payload).eq("id", tid).execute()

def add_proveedor(payload):
    supabase.table("proveedores_tarea").insert(payload).execute()

def update_proveedor(pid, payload):
    supabase.table("proveedores_tarea").update(payload).eq("id", pid).execute()

def add_historial(tid, detalle):
    if detalle and detalle.strip():
        supabase.table("historial_tareas").insert(
            {"tarea_id": tid, "detalle": detalle.strip()}
        ).execute()

# =========================================================
# UTILIDADES DE NEGOCIO
# =========================================================
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

def build_tareas_table(consorcios, tareas):
    rows = []
    for t in tareas:
        rows.append({
            "Consorcio": cons_label(consorcios, t["consorcio_id"]),
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

def resumen_tarea_para_home(t):
    partes = [f"**{t.get('titulo','(sin título)')}**"]
    if t.get("proximo_paso"):
        partes.append(f"Próximo paso: {t.get('proximo_paso')}")
    if t.get("estado"):
        partes.append(f"Estado: {t.get('estado')}")
    return " · ".join(partes)

def get_logo_html():
    try:
        with open("ajk_logo.jpg", "rb") as f:
            import base64
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/jpeg;base64,{b64}" alt="AJK logo">'
    except Exception:
        return '<div style="font-size:2rem;">💗</div>'

# =========================================================
# CARGA DE DATOS
# =========================================================
consorcios = get_consorcios()

# =========================================================
# HEADER
# =========================================================
logo_html = get_logo_html()

st.markdown(f"""
<div class="hero-card">
    <div class="hero-grid">
        <div class="hero-logo-box">
            {logo_html}
        </div>
        <div>
            <div class="hero-title">AJK Consorcios</div>
            <div class="hero-sub">
                Panel de seguimiento de tareas, presupuestos, consejo, alarmas y reportes por consorcio.
            </div>
            <div class="hero-line"></div>
            <div class="hero-mini">
                Seguimiento REPA con foco en tareas, recordatorios, proveedores y reportes semanales
                <span class="heart-soft">♡</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Inicio",
    "Nueva tarea",
    "Tareas",
    "Reporte por consorcio"
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

    # MÉTRICAS
    m1, m2, m3, m4 = st.columns(4)

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

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_alarmas, col_resumen = st.columns([1.05, 1.25])

    # ALARMAS
    with col_alarmas:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Alarmas pendientes</div>', unsafe_allow_html=True)

        alarmas_ordenadas = []
        for t in con_alarma:
            tipo, etiqueta = alarm_status(t)
            prioridad = {
                "vencida": 0,
                "hoy": 1,
                "proxima": 2,
                "futura": 3,
                "sin_fecha": 4
            }.get(tipo, 5)
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
                    <div class="alarm-cons">{cons_label(consorcios, t["consorcio_id"])}</div>
                    <div class="alarm-title">{t.get("titulo","(sin título)")}</div>
                    <div class="small-muted">{etiqueta}</div>
                    <div style="margin-top:4px;">{motivo}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # RESUMEN
    with col_resumen:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Resumen general de tareas</div>', unsafe_allow_html=True)

        if tareas:
            st.markdown("##### Próximas a mirar")
            top_tareas = tareas[:8]
            for t in top_tareas:
                st.markdown(
                    f'<div class="soft-box">{resumen_tarea_para_home(t)}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Todavía no hay tareas cargadas.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Vista rápida de todas las tareas</div>', unsafe_allow_html=True)

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
                    format_func=lambda c: f'{c["codigo"]} - {c["nombre"]}'
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

            st.markdown("### Proveedores")
            st.caption("Podés cargar hasta 5 proveedores para esta tarea.")
            proveedores = []

            for i in range(1, 6):
                p1, p2, p3, p4 = st.columns([1.6, 1, 1, 1])
                nombre = p1.text_input(f"Proveedor {i}", key=f"nuevo_p_nombre_{i}")
                pedido = p2.checkbox("Pedido", key=f"nuevo_p_pedido_{i}")
                respondio = p3.checkbox("Respondió", key=f"nuevo_p_respondio_{i}")
                monto = p4.text_input("Monto", key=f"nuevo_p_monto_{i}")
                proveedores.append((i, nombre, pedido, respondio, monto))

            observaciones = st.text_area("Observaciones")
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
                        for orden, nombre, pedido, respondio, monto in proveedores:
                            if str(nombre).strip():
                                add_proveedor({
                                    "tarea_id": tarea["id"],
                                    "orden": orden,
                                    "nombre": nombre.strip(),
                                    "contactado": pedido,
                                    "presupuesto_recibido": respondio,
                                    "monto": money_to_float(monto),
                                })

                        if primer_mov.strip():
                            add_historial(tarea["id"], primer_mov)

                        st.success("Tarea guardada.")
                        st.rerun()
                    else:
                        st.error("No se pudo guardar la tarea.")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 3 - TAREAS
# =========================================================
with tab3:
    tareas = get_tareas()

    if not tareas:
        st.info("No hay tareas cargadas.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Editar tareas y seguimiento</div>', unsafe_allow_html=True)

        filtro_cons = st.selectbox(
            "Filtrar por consorcio",
            ["Todos"] + [c["id"] for c in consorcios],
            format_func=lambda x: "Todos" if x == "Todos" else cons_label(consorcios, x)
        )

        tareas_f = tareas if filtro_cons == "Todos" else [t for t in tareas if t["consorcio_id"] == filtro_cons]

        if not tareas_f:
            st.info("No hay tareas para ese filtro.")
        else:
            opciones = {
                f'{cons_label(consorcios, t["consorcio_id"])} | {t.get("titulo","(sin título)")}': t
                for t in tareas_f
            }
            tarea = opciones[st.selectbox("Elegí tarea", list(opciones.keys()))]
            proveedores = get_proveedores(tarea["id"])
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
                    fecha_limite = st.date_input(
                        "Fecha límite",
                        value=parse_iso_date(tarea.get("fecha_limite")),
                        format="DD/MM/YYYY"
                    )
                    proximo_paso = st.text_input("Próximo paso", value=tarea.get("proximo_paso", ""))
                    requiere_consejo = st.checkbox("Requiere consejo", value=tarea.get("requiere_consejo", False))
                    enviado_consejo = st.checkbox("Enviado al consejo", value=tarea.get("enviado_consejo", False))

                st.markdown("### Alarma")
                a1, a2 = st.columns([1, 1.2])
                with a1:
                    alarma_activa = st.checkbox("Activar alarma", value=tarea.get("alarma_activa", False))
                    alarma_fecha = st.date_input(
                        "Fecha de alarma",
                        value=parse_iso_date(tarea.get("alarma_fecha")),
                        format="DD/MM/YYYY"
                    )
                with a2:
                    alarma_motivo = st.text_input("Motivo de alarma", value=tarea.get("alarma_motivo") or "")

                observaciones = st.text_area("Observaciones", value=tarea.get("observaciones", ""))
                nuevo_mov = st.text_area("Agregar movimiento al historial")

                save = st.form_submit_button("Guardar cambios")

                if save:
                    update_tarea(tarea["id"], {
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
                    if nuevo_mov.strip():
                        add_historial(tarea["id"], nuevo_mov.strip())
                    st.success("Cambios guardados.")
                    st.rerun()

            st.markdown("<div class='divider-soft'></div>", unsafe_allow_html=True)

            st.markdown("### Proveedores de esta tarea")

            if proveedores:
                for p in proveedores:
                    titulo_exp = f"Proveedor #{p.get('orden', '')}: {p.get('nombre', 'Sin nombre')}"
                    with st.expander(titulo_exp):
                        with st.form(f"prov_{p['id']}"):
                            pc1, pc2, pc3, pc4 = st.columns([1.4, 1, 1, 1])
                            p_nombre = pc1.text_input("Nombre", value=p.get("nombre", ""))
                            p_pedido = pc2.checkbox("Presupuesto pedido", value=p.get("contactado", False))
                            p_respondio = pc3.checkbox("Respondió", value=p.get("presupuesto_recibido", False))
                            p_monto = pc4.text_input("Monto", value="" if p.get("monto") is None else str(p.get("monto")))

                            guardar_prov = st.form_submit_button("Guardar proveedor")
                            if guardar_prov:
                                update_proveedor(p["id"], {
                                    "nombre": p_nombre.strip(),
                                    "contactado": p_pedido,
                                    "presupuesto_recibido": p_respondio,
                                    "monto": money_to_float(p_monto),
                                })
                                st.success("Proveedor actualizado.")
                                st.rerun()
            else:
                st.caption("Esta tarea no tiene proveedores cargados.")

            with st.expander("Agregar proveedor a esta tarea"):
                with st.form(f"nuevo_prov_{tarea['id']}"):
                    np1, np2, np3, np4 = st.columns([1.4, 1, 1, 1])
                    nuevo_nombre = np1.text_input("Nombre del proveedor")
                    nuevo_pedido = np2.checkbox("Presupuesto pedido")
                    nuevo_respondio = np3.checkbox("Respondió")
                    nuevo_monto = np4.text_input("Monto")
                    agregar_prov = st.form_submit_button("Agregar proveedor")
                    if agregar_prov:
                        if not nuevo_nombre.strip():
                            st.error("Escribí el nombre del proveedor.")
                        else:
                            orden_nuevo = len(proveedores) + 1
                            add_proveedor({
                                "tarea_id": tarea["id"],
                                "orden": orden_nuevo,
                                "nombre": nuevo_nombre.strip(),
                                "contactado": nuevo_pedido,
                                "presupuesto_recibido": nuevo_respondio,
                                "monto": money_to_float(nuevo_monto),
                            })
                            st.success("Proveedor agregado.")
                            st.rerun()

            st.markdown("<div class='divider-soft'></div>", unsafe_allow_html=True)

            st.markdown("### Historial de movimientos")
            if historial:
                for h in historial:
                    fecha_h = h.get("fecha") or h.get("created_at") or ""
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
# TAB 4 - REPORTE POR CONSORCIO
# =========================================================
with tab4:
    if not consorcios:
        st.warning("No hay consorcios cargados.")
    else:
        cons = st.selectbox(
            "Elegí el consorcio",
            consorcios,
            format_func=lambda c: f'{c["codigo"]} - {c["nombre"]}'
        )

        tareas_cons = get_tareas(cons["id"])

        if not tareas_cons:
            st.info("Ese consorcio no tiene tareas.")
        else:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">{cons["codigo"]} - {cons["nombre"]}</div>',
                unsafe_allow_html=True
            )
            st.caption("Este reporte incluye todas las tareas del consorcio, incluso finalizadas y canceladas.")

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
                    texto.append(
                        f"   Consejo: {'enviado' if t.get('enviado_consejo') else 'pendiente de envío'}"
                    )

                if t.get("alarma_activa"):
                    alarma_txt = format_date(t.get("alarma_fecha"))
                    motivo = t.get("alarma_motivo") or ""
                    texto.append(f"   Alarma: {alarma_txt} {('- ' + motivo) if motivo else ''}")

                provs = get_proveedores(t["id"])
                if provs:
                    texto.append("   Proveedores:")
                    for p in provs:
                        partes = [p.get("nombre", "Proveedor")]
                        if p.get("contactado"):
                            partes.append("presupuesto pedido")
                        if p.get("presupuesto_recibido"):
                            partes.append("respondió")
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
                })

            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.text_area(
                "Resumen del consorcio",
                value="\n".join(texto),
                height=520
            )
            st.markdown('</div>', unsafe_allow_html=True)

            df_rep = pd.DataFrame(rows)
            st.dataframe(df_rep, use_container_width=True, hide_index=True)

            st.download_button(
                "Descargar Excel del consorcio",
                data=export_excel(df_rep),
                file_name=f"reporte_{cons['codigo']}_{date.today().isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.markdown('</div>', unsafe_allow_html=True)
