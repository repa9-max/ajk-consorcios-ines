import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import date
from supabase import create_client

st.set_page_config(page_title="AJK Consorcios", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ESTADOS = ["Pendiente","Pidiendo presupuestos","Presupuestos recibidos","Enviado al consejo","Aprobado","En ejecución","Finalizado","Cancelado"]
PRIORIDADES = ["Baja","Media","Alta","Urgente"]
CATEGORIAS = ["Plomería","Electricidad","Ascensor","Pintura","Humedad","Limpieza","Matafuegos","Seguro","Bombas","Administración / reclamo","Otro"]

st.markdown("""<style>
.stApp {background: linear-gradient(180deg, #fffafc 0%, #f8fdff 100%);}
.block-container {padding-top: 1rem; max-width: 1350px;}
h1,h2,h3 {color:#b66a86;}
.alert-box {background:#fff6f8;border:1px solid #f3cbd8;border-radius:12px;padding:10px 12px;margin-bottom:8px;}
</style>""", unsafe_allow_html=True)

def get_consorcios():
    return supabase.table("consorcios").select("*").order("codigo").execute().data or []

def get_tareas(consorcio_id=None):
    q = supabase.table("tareas").select("*").order("created_at", desc=True)
    if consorcio_id:
        q = q.eq("consorcio_id", consorcio_id)
    return q.execute().data or []

def get_proveedores(tarea_id):
    return supabase.table("proveedores_tarea").select("*").eq("tarea_id", tarea_id).order("orden").execute().data or []

def get_historial(tarea_id):
    return supabase.table("historial_tareas").select("*").eq("tarea_id", tarea_id).order("fecha", desc=True).execute().data or []

def add_tarea(payload):
    return supabase.table("tareas").insert(payload).execute().data[0]

def update_tarea(tid, payload):
    supabase.table("tareas").update(payload).eq("id", tid).execute()

def add_proveedor(payload):
    supabase.table("proveedores_tarea").insert(payload).execute()

def update_proveedor(pid, payload):
    supabase.table("proveedores_tarea").update(payload).eq("id", pid).execute()

def add_historial(tid, detalle):
    if detalle.strip():
        supabase.table("historial_tareas").insert({"tarea_id": tid, "detalle": detalle.strip()}).execute()

def cons_label(consorcios, cid):
    for c in consorcios:
        if c["id"] == cid:
            return f'{c["codigo"]} - {c["nombre"]}'
    return cid

def export_excel(df):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
    bio.seek(0)
    return bio

consorcios = get_consorcios()
st.title("AJK Consorcios")
st.caption("Panel de seguimiento de tareas, presupuestos, consejos y reportes.")

tab1, tab2, tab3, tab4 = st.tabs(["Inicio","Nueva tarea","Tareas","Reporte por consorcio"])

with tab1:
    tareas = get_tareas()
    activas = [t for t in tareas if t.get("estado") not in ["Finalizado","Cancelado"]]
    urgentes = [t for t in tareas if t.get("prioridad") == "Urgente" and t.get("estado") not in ["Finalizado","Cancelado"]]
    con_alarma = [t for t in tareas if t.get("alarma_activa")]
    pendientes_consejo = [t for t in tareas if t.get("requiere_consejo") and not t.get("enviado_consejo")]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Tareas activas", len(activas))
    c2.metric("Urgentes", len(urgentes))
    c3.metric("Con alarma", len(con_alarma))
    c4.metric("Pendientes de consejo", len(pendientes_consejo))

    st.subheader("Alarmas pendientes")
    if con_alarma:
        for t in con_alarma:
            st.markdown(f'<div class="alert-box"><strong>{cons_label(consorcios, t["consorcio_id"])}</strong> — {t["titulo"]}<br>Fecha: {t.get("alarma_fecha") or ""}<br>Motivo: {t.get("alarma_motivo") or ""}</div>', unsafe_allow_html=True)
    else:
        st.info("No hay alarmas cargadas.")

    rows = []
    for t in tareas:
        rows.append({
            "Consorcio": cons_label(consorcios, t["consorcio_id"]),
            "Título": t.get("titulo",""),
            "Categoría": t.get("tipo_gestion",""),
            "Prioridad": t.get("prioridad",""),
            "Estado": t.get("estado",""),
            "Fecha límite": t.get("fecha_limite",""),
            "Próximo paso": t.get("proximo_paso",""),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay tareas cargadas.")

with tab2:
    with st.form("nueva"):
        c1,c2 = st.columns(2)
        with c1:
            cons = st.selectbox("Consorcio", consorcios, format_func=lambda c: f'{c["codigo"]} - {c["nombre"]}')
            titulo = st.text_input("Título / asunto")
            detalle = st.text_area("Detalle")
            categoria = st.selectbox("Categoría", CATEGORIAS)
            prioridad = st.selectbox("Prioridad", PRIORIDADES)
        with c2:
            estado = st.selectbox("Estado", ESTADOS)
            fecha_limite = st.text_input("Fecha límite (AAAA-MM-DD)")
            proximo_paso = st.text_input("Próximo paso")
            requiere_consejo = st.checkbox("Requiere enviar al consejo")
            enviado_consejo = st.checkbox("Ya fue enviado al consejo")

        st.markdown("### Alarma interna")
        alarma_activa = st.checkbox("Activar alarma")
        alarma_fecha = st.text_input("Fecha recordatorio (AAAA-MM-DD)")
        alarma_motivo = st.text_input("Motivo del recordatorio")

        st.markdown("### Proveedores")
        proveedores = []
        for i in range(1,6):
            p1,p2,p3,p4 = st.columns(4)
            nombre = p1.text_input(f"Proveedor {i}", key=f"pn{i}")
            pedido = p2.checkbox("Presupuesto pedido", key=f"pp{i}")
            respondio = p3.checkbox("Respondió", key=f"pr{i}")
            monto = p4.text_input("Monto", key=f"pm{i}")
            proveedores.append((i,nombre,pedido,respondio,monto))

        observaciones = st.text_area("Observaciones")
        primer_mov = st.text_area("Primer movimiento / nota interna")
        ok = st.form_submit_button("Guardar tarea")
        if ok:
            tarea = add_tarea({
                "consorcio_id": cons["id"],
                "titulo": titulo,
                "descripcion": detalle,
                "tipo_gestion": categoria,
                "prioridad": prioridad,
                "estado": estado,
                "fecha_limite": fecha_limite or None,
                "proximo_paso": proximo_paso,
                "requiere_consejo": requiere_consejo,
                "enviado_consejo": enviado_consejo,
                "observaciones": observaciones,
                "alarma_activa": alarma_activa,
                "alarma_fecha": alarma_fecha or None,
                "alarma_motivo": alarma_motivo or None
            })
            for orden,nombre,pedido,respondio,monto in proveedores:
                if nombre.strip():
                    add_proveedor({
                        "tarea_id": tarea["id"], "orden": orden, "nombre": nombre,
                        "contactado": pedido, "presupuesto_recibido": respondio,
                        "monto": float(monto.replace(",", ".")) if monto.strip() else None
                    })
            if primer_mov.strip():
                add_historial(tarea["id"], primer_mov)
            st.success("Tarea guardada.")

with tab3:
    tareas = get_tareas()
    if not tareas:
        st.info("No hay tareas cargadas.")
    else:
        filtro_cons = st.selectbox("Filtrar por consorcio", ["Todos"]+[c["id"] for c in consorcios], format_func=lambda x: "Todos" if x=="Todos" else cons_label(consorcios, x))
        tareas_f = tareas if filtro_cons == "Todos" else [t for t in tareas if t["consorcio_id"] == filtro_cons]
        opciones = {f'{cons_label(consorcios,t["consorcio_id"])} | {t["titulo"]}': t for t in tareas_f}
        tarea = opciones[st.selectbox("Elegí tarea", list(opciones.keys()))]
        proveedores = get_proveedores(tarea["id"])
        historial = get_historial(tarea["id"])

        with st.form("editar"):
            titulo = st.text_input("Título", value=tarea.get("titulo",""))
            detalle = st.text_area("Detalle", value=tarea.get("descripcion",""))
            categoria = st.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(tarea.get("tipo_gestion","Otro")) if tarea.get("tipo_gestion","Otro") in CATEGORIAS else len(CATEGORIAS)-1)
            prioridad = st.selectbox("Prioridad", PRIORIDADES, index=PRIORIDADES.index(tarea.get("prioridad","Media")) if tarea.get("prioridad","Media") in PRIORIDADES else 1)
            estado = st.selectbox("Estado", ESTADOS, index=ESTADOS.index(tarea.get("estado","Pendiente")) if tarea.get("estado","Pendiente") in ESTADOS else 0)
            fecha_limite = st.text_input("Fecha límite (AAAA-MM-DD)", value=tarea.get("fecha_limite") or "")
            proximo_paso = st.text_input("Próximo paso", value=tarea.get("proximo_paso",""))
            requiere_consejo = st.checkbox("Requiere consejo", value=tarea.get("requiere_consejo",False))
            enviado_consejo = st.checkbox("Enviado al consejo", value=tarea.get("enviado_consejo",False))
            alarma_activa = st.checkbox("Activar alarma", value=tarea.get("alarma_activa",False))
            alarma_fecha = st.text_input("Fecha alarma", value=tarea.get("alarma_fecha") or "")
            alarma_motivo = st.text_input("Motivo alarma", value=tarea.get("alarma_motivo") or "")
            observaciones = st.text_area("Observaciones", value=tarea.get("observaciones",""))
            nuevo_mov = st.text_area("Agregar movimiento")

            save = st.form_submit_button("Guardar cambios")
            if save:
                update_tarea(tarea["id"], {
                    "titulo": titulo, "descripcion": detalle, "tipo_gestion": categoria,
                    "prioridad": prioridad, "estado": estado, "fecha_limite": fecha_limite or None,
                    "proximo_paso": proximo_paso, "requiere_consejo": requiere_consejo,
                    "enviado_consejo": enviado_consejo, "alarma_activa": alarma_activa,
                    "alarma_fecha": alarma_fecha or None, "alarma_motivo": alarma_motivo or None,
                    "observaciones": observaciones
                })
                if nuevo_mov.strip():
                    add_historial(tarea["id"], nuevo_mov)
                st.success("Cambios guardados.")

        st.markdown("### Historial")
        if historial:
            for h in historial:
                st.markdown(f"- **{h['fecha']}** — {h['detalle']}")
        else:
            st.caption("Sin movimientos registrados.")

with tab4:
    cons = st.selectbox("Elegí el consorcio", consorcios, format_func=lambda c: f'{c["codigo"]} - {c["nombre"]}')
    tareas = get_tareas(cons["id"])
    if not tareas:
        st.info("Ese consorcio no tiene tareas.")
    else:
        st.markdown(f"## {cons['codigo']} - {cons['nombre']}")
        texto = []
        rows = []
        for i,t in enumerate(tareas, start=1):
            texto.append(f"{i}. {t['titulo']} — {t.get('estado','')}")
            if t.get("descripcion"):
                texto.append(f"   Detalle: {t['descripcion']}")
            if t.get("proximo_paso"):
                texto.append(f"   Próximo paso: {t['proximo_paso']}")
            if t.get("requiere_consejo"):
                texto.append(f"   Consejo: {'enviado' if t.get('enviado_consejo') else 'pendiente de envío'}")
            provs = get_proveedores(t["id"])
            if provs:
                texto.append("   Proveedores:")
                for p in provs:
                    partes = [p.get("nombre","Proveedor")]
                    if p.get("contactado"): partes.append("presupuesto pedido")
                    if p.get("presupuesto_recibido"): partes.append("respondió")
                    if p.get("monto") is not None: partes.append(f"monto: {p['monto']}")
                    texto.append("   - " + " | ".join(partes))
            texto.append("")
            rows.append({"Título": t.get("titulo",""), "Estado": t.get("estado",""), "Categoría": t.get("tipo_gestion",""), "Prioridad": t.get("prioridad",""), "Fecha límite": t.get("fecha_limite",""), "Próximo paso": t.get("proximo_paso","")})

        st.text_area("Resumen del consorcio", value="\n".join(texto), height=500)
        st.download_button("Descargar Excel del consorcio", data=export_excel(pd.DataFrame(rows)), file_name=f"reporte_{cons['codigo']}_{date.today().isoformat()}.xlsx")
