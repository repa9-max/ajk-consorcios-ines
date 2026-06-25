
import json
from datetime import datetime, date
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Inés | AJK Consorcios", layout="wide")

DATA_FILE = "consorcios_data.json"
LOGO_FILE = "ajk_logo.jpg"

DEFAULT_CONSORCIOS = [{"id": x, "nombre": f"Consorcio {x}"} for x in [
    "851","1445","1767","2151","2275","2430","2445","2544","2545","2669","2838","2860","2865","2871","3356","4263"
]]

ESTADOS = [
    "Pendiente","Pidiendo presupuestos","Presupuestos recibidos",
    "Enviado a administración","Enviado al consejo","Aprobado",
    "En ejecución","Finalizado"
]
PRIORIDADES = ["Alta","Media","Baja"]
TIPOS = ["Plomería","Electricidad","Ascensor","Pintura","Humedad","Limpieza","Matafuegos","Seguro","Administración / reclamo","Otro"]

def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background:
          radial-gradient(circle at top right, #ffe7f0 0%, transparent 20%),
          radial-gradient(circle at top left, #e8fbff 0%, transparent 18%),
          linear-gradient(180deg,#fff9fc 0%, #f8fdff 100%);
    }
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    h1,h2,h3 {color:#b56a86;}
    .title {
        font-size:2.2rem; font-weight:800; color:#b56a86; margin-bottom:0.2rem;
    }
    .subtitle {color:#8b6f7a; margin-bottom:0.8rem;}
    .soft {
        background: rgba(255,255,255,.92);
        border:1px solid #f7d7e4;
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(201,126,156,.08);
    }
    .badge {
        display:inline-block; padding:6px 12px; border-radius:999px;
        background:#fff1f6; border:1px solid #f6d4e1; color:#b56a86;
        margin-right:8px; margin-bottom:8px; font-size:.9rem;
    }
    .danger {background:#fff0f4;border:1px solid #ffc6d8;color:#b00040;padding:10px 14px;border-radius:14px;margin-bottom:8px}
    .warn {background:#fff9ec;border:1px solid #ffe1a1;color:#8a5a00;padding:10px 14px;border-radius:14px;margin-bottom:8px}
    .ok {background:#eefcf5;border:1px solid #c4efd8;color:#216b4b;padding:10px 14px;border-radius:14px;margin-bottom:8px}
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        data = {"consorcios": DEFAULT_CONSORCIOS, "tareas": []}
        save_data(data)
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cons_name(data, cid):
    for c in data["consorcios"]:
        if c["id"] == cid:
            return c["nombre"]
    return cid

def next_id(data):
    return max([t["id"] for t in data["tareas"]], default=0) + 1

def ensure_task_shape(t):
    if "historial" not in t: t["historial"] = []
    if "checklist" not in t:
        t["checklist"] = {
            "reclamo_recibido": False,
            "pedido_p1": False, "pedido_p2": False, "pedido_p3": False, "pedido_p4": False, "pedido_p5": False,
            "presupuestos_recibidos": False,
            "enviado_administracion": False,
            "enviado_consejo": False,
            "aprobado": False,
            "trabajo_coordinado": False,
            "trabajo_finalizado": False
        }
    if "proveedores" not in t:
        t["proveedores"] = [{"nombre":"","contactado":False,"presupuesto":False} for _ in range(5)]
    while len(t["proveedores"]) < 5:
        t["proveedores"].append({"nombre":"","contactado":False,"presupuesto":False})
    return t

def task_to_row(data, t):
    ensure_task_shape(t)
    vencida = False
    vence_pronto = False
    if t.get("fecha_limite"):
        try:
            d = datetime.strptime(t["fecha_limite"], "%Y-%m-%d").date()
            vencida = d < date.today() and t.get("estado") != "Finalizado"
            vence_pronto = date.today() <= d <= date.today().replace(day=date.today().day) and False
        except:
            pass
    return {
        "id": t["id"],
        "consorcio_id": t["consorcio_id"],
        "consorcio": cons_name(data, t["consorcio_id"]),
        "titulo": t["titulo"],
        "tipo": t.get("tipo",""),
        "estado": t.get("estado","Pendiente"),
        "prioridad": t.get("prioridad","Media"),
        "fecha_limite": t.get("fecha_limite",""),
        "proximo_paso": t.get("proximo_paso",""),
        "alarma": t.get("alarma",""),
        "enviado_administracion": "Sí" if t.get("enviado_administracion") else "No",
        "enviado_consejo": "Sí" if t.get("enviado_consejo") else "No",
        "ultima_actualizacion": t.get("ultima_actualizacion",""),
        "vencida": "Sí" if vencida else "No",
    }

def tasks_df(data):
    return pd.DataFrame([task_to_row(data, ensure_task_shape(t)) for t in data["tareas"]])

def export_excel(df):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
    bio.seek(0)
    return bio

def add_history(task, text):
    if text.strip():
        task["historial"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "detalle": text.strip()
        })

inject_css()
data = load_data()
for t in data["tareas"]:
    ensure_task_shape(t)

# Header
col1, col2 = st.columns([1, 3])
with col1:
    if Path(LOGO_FILE).exists():
        st.image(LOGO_FILE, width=190)
with col2:
    st.markdown('<div class="title">Inés · AJK Consorcios</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Panel pastel para seguir REPA, presupuestos, consejos, vencimientos y reportes ✿ ♡</div>', unsafe_allow_html=True)
    st.markdown('<span class="badge">Hasta 5 proveedores</span><span class="badge">Alarmas</span><span class="badge">Historial</span><span class="badge">Checklist REPA</span>', unsafe_allow_html=True)

tabs = st.tabs(["🌷 Hoy", "📝 Nueva tarea", "🛠️ Editar tarea", "🏢 Consorcios", "📤 Reportes"])

with tabs[0]:
    df = tasks_df(data)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tareas activas", 0 if df.empty else len(df[df["estado"]!="Finalizado"]))
    c2.metric("Urgentes", 0 if df.empty else len(df[(df["prioridad"]=="Alta") & (df["estado"]!="Finalizado")]))
    c3.metric("Enviadas al consejo", 0 if df.empty else len(df[df["enviado_consejo"]=="Sí"]))
    c4.metric("Con alarma", len([t for t in data["tareas"] if t.get("alarma")]))

    if not df.empty:
        st.subheader("Alertas")
        hoy = date.today()
        alerts = []
        for t in data["tareas"]:
            ensure_task_shape(t)
            if t.get("fecha_limite") and t.get("estado") != "Finalizado":
                try:
                    lim = datetime.strptime(t["fecha_limite"], "%Y-%m-%d").date()
                    if lim < hoy:
                        alerts.append(("danger", f"{cons_name(data,t['consorcio_id'])} · {t['titulo']} está vencida desde {lim.strftime('%d/%m/%Y')}"))
                    elif (lim - hoy).days <= 3:
                        alerts.append(("warn", f"{cons_name(data,t['consorcio_id'])} · {t['titulo']} vence el {lim.strftime('%d/%m/%Y')}"))
                except:
                    pass
            if t.get("alarma") and t.get("estado") != "Finalizado":
                alerts.append(("warn", f"{cons_name(data,t['consorcio_id'])} · {t['titulo']} → recordatorio: {t['alarma']}"))

        if alerts:
            for level, text in alerts[:12]:
                st.markdown(f'<div class="{level}">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ok">No hay alertas urgentes ahora.</div>', unsafe_allow_html=True)

        st.subheader("Filtro general")
        f1, f2, f3, f4 = st.columns(4)
        cons = f1.selectbox("Consorcio", ["Todos"]+[c["id"] for c in data["consorcios"]], format_func=lambda x: "Todos" if x=="Todos" else f"{x} - {cons_name(data,x)}")
        estado = f2.selectbox("Estado", ["Todos"]+ESTADOS)
        prioridad = f3.selectbox("Prioridad", ["Todas"]+PRIORIDADES)
        tipo = f4.selectbox("Tipo", ["Todos"]+TIPOS)

        if cons != "Todos": df = df[df["consorcio_id"] == cons]
        if estado != "Todos": df = df[df["estado"] == estado]
        if prioridad != "Todas": df = df[df["prioridad"] == prioridad]
        if tipo != "Todos": df = df[df["tipo"] == tipo]

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Vistas rápidas")
        v1, v2, v3, v4 = st.columns(4)
        with v1:
            if st.button("Urgentes"):
                st.dataframe(df[(df["prioridad"]=="Alta") & (df["estado"]!="Finalizado")], use_container_width=True, hide_index=True)
        with v2:
            if st.button("Pendientes de consejo"):
                st.dataframe(df[(df["enviado_consejo"]=="No") & (df["estado"]!="Finalizado")], use_container_width=True, hide_index=True)
        with v3:
            if st.button("Finalizadas"):
                st.dataframe(df[df["estado"]=="Finalizado"], use_container_width=True, hide_index=True)
        with v4:
            if st.button("Vencidas"):
                st.dataframe(df[df["vencida"]=="Sí"], use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no cargaste tareas.")

with tabs[1]:
    with st.form("nueva_tarea"):
        c1, c2 = st.columns(2)
        with c1:
            cons = st.selectbox("Consorcio", [c["id"] for c in data["consorcios"]], format_func=lambda x: f"{x} - {cons_name(data,x)}")
            titulo = st.text_input("Título de la tarea")
            descripcion = st.text_area("Descripción")
            tipo = st.selectbox("Tipo de gestión", TIPOS)
            prioridad = st.selectbox("Prioridad", PRIORIDADES)
            estado = st.selectbox("Estado inicial", ESTADOS, index=0)
        with c2:
            fecha_limite = st.text_input("Fecha límite (AAAA-MM-DD)")
            proximo_paso = st.text_input("Próximo paso")
            alarma = st.text_input("Alarma / recordatorio")
            enviado_adm = st.checkbox("Enviado a administración")
            enviado_consejo = st.checkbox("Enviado al consejo")

        st.markdown("### Proveedores")
        proveedores = []
        for i in range(1, 6):
            a,b,c = st.columns([2,1,1])
            nombre = a.text_input(f"Proveedor {i}", key=f"prov{i}")
            contactado = b.checkbox("Contactado", key=f"cont{i}")
            presupuesto = c.checkbox("Presupuesto recibido", key=f"pres{i}")
            proveedores.append({"nombre":nombre,"contactado":contactado,"presupuesto":presupuesto})

        st.markdown("### Checklist REPA")
        ch1, ch2, ch3 = st.columns(3)
        checklist = {}
        with ch1:
            checklist["reclamo_recibido"] = st.checkbox("Reclamo recibido")
            checklist["pedido_p1"] = st.checkbox("Pedido a proveedor 1")
            checklist["pedido_p2"] = st.checkbox("Pedido a proveedor 2")
            checklist["pedido_p3"] = st.checkbox("Pedido a proveedor 3")
        with ch2:
            checklist["pedido_p4"] = st.checkbox("Pedido a proveedor 4")
            checklist["pedido_p5"] = st.checkbox("Pedido a proveedor 5")
            checklist["presupuestos_recibidos"] = st.checkbox("Presupuestos recibidos")
            checklist["enviado_administracion"] = st.checkbox("Enviado a administración (checklist)")
        with ch3:
            checklist["enviado_consejo"] = st.checkbox("Enviado al consejo (checklist)")
            checklist["aprobado"] = st.checkbox("Aprobado")
            checklist["trabajo_coordinado"] = st.checkbox("Trabajo coordinado")
            checklist["trabajo_finalizado"] = st.checkbox("Trabajo finalizado")

        observaciones = st.text_area("Observaciones")
        primer_historial = st.text_area("Primer movimiento / nota de historial (opcional)")
        ok = st.form_submit_button("Crear tarea")

        if ok and titulo.strip():
            task = {
                "id": next_id(data),
                "consorcio_id": cons,
                "titulo": titulo.strip(),
                "descripcion": descripcion.strip(),
                "tipo": tipo,
                "prioridad": prioridad,
                "estado": estado,
                "fecha_limite": fecha_limite.strip(),
                "proximo_paso": proximo_paso.strip(),
                "alarma": alarma.strip(),
                "proveedores": proveedores,
                "enviado_administracion": enviado_adm,
                "enviado_consejo": enviado_consejo,
                "checklist": checklist,
                "observaciones": observaciones.strip(),
                "fecha_alta": date.today().isoformat(),
                "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "historial": []
            }
            add_history(task, primer_historial)
            data["tareas"].append(task)
            save_data(data)
            st.success("Tarea creada.")

with tabs[2]:
    if not data["tareas"]:
        st.info("No hay tareas cargadas.")
    else:
        opciones = [t["id"] for t in data["tareas"]]
        tid = st.selectbox("Elegí la tarea", opciones, format_func=lambda x: f"Tarea #{x}")
        t = next(x for x in data["tareas"] if x["id"] == tid)
        ensure_task_shape(t)

        st.markdown(f"### {t['titulo']} · {cons_name(data, t['consorcio_id'])}")

        with st.form("editar"):
            c1, c2 = st.columns(2)
            with c1:
                t["titulo"] = st.text_input("Título", value=t.get("titulo",""))
                t["descripcion"] = st.text_area("Descripción", value=t.get("descripcion",""))
                t["tipo"] = st.selectbox("Tipo", TIPOS, index=TIPOS.index(t.get("tipo","Otro")) if t.get("tipo","Otro") in TIPOS else len(TIPOS)-1)
                t["estado"] = st.selectbox("Estado", ESTADOS, index=ESTADOS.index(t.get("estado","Pendiente")))
                t["prioridad"] = st.selectbox("Prioridad", PRIORIDADES, index=PRIORIDADES.index(t.get("prioridad","Media")))
            with c2:
                t["fecha_limite"] = st.text_input("Fecha límite (AAAA-MM-DD)", value=t.get("fecha_limite",""))
                t["proximo_paso"] = st.text_input("Próximo paso", value=t.get("proximo_paso",""))
                t["alarma"] = st.text_input("Alarma", value=t.get("alarma",""))
                t["enviado_administracion"] = st.checkbox("Enviado a administración", value=t.get("enviado_administracion",False))
                t["enviado_consejo"] = st.checkbox("Enviado al consejo", value=t.get("enviado_consejo",False))

            st.markdown("### Proveedores")
            for i in range(5):
                a,b,c = st.columns([2,1,1])
                t["proveedores"][i]["nombre"] = a.text_input(f"Proveedor {i+1}", value=t["proveedores"][i]["nombre"], key=f"ep{i}")
                t["proveedores"][i]["contactado"] = b.checkbox("Contactado", value=t["proveedores"][i]["contactado"], key=f"ec{i}")
                t["proveedores"][i]["presupuesto"] = c.checkbox("Presupuesto", value=t["proveedores"][i]["presupuesto"], key=f"er{i}")

            st.markdown("### Checklist REPA")
            cl = t["checklist"]
            q1,q2,q3 = st.columns(3)
            with q1:
                cl["reclamo_recibido"] = st.checkbox("Reclamo recibido", value=cl.get("reclamo_recibido",False))
                cl["pedido_p1"] = st.checkbox("Pedido a proveedor 1", value=cl.get("pedido_p1",False))
                cl["pedido_p2"] = st.checkbox("Pedido a proveedor 2", value=cl.get("pedido_p2",False))
                cl["pedido_p3"] = st.checkbox("Pedido a proveedor 3", value=cl.get("pedido_p3",False))
            with q2:
                cl["pedido_p4"] = st.checkbox("Pedido a proveedor 4", value=cl.get("pedido_p4",False))
                cl["pedido_p5"] = st.checkbox("Pedido a proveedor 5", value=cl.get("pedido_p5",False))
                cl["presupuestos_recibidos"] = st.checkbox("Presupuestos recibidos", value=cl.get("presupuestos_recibidos",False))
                cl["enviado_administracion"] = st.checkbox("Enviado a administración (checklist)", value=cl.get("enviado_administracion",False))
            with q3:
                cl["enviado_consejo"] = st.checkbox("Enviado al consejo (checklist)", value=cl.get("enviado_consejo",False))
                cl["aprobado"] = st.checkbox("Aprobado", value=cl.get("aprobado",False))
                cl["trabajo_coordinado"] = st.checkbox("Trabajo coordinado", value=cl.get("trabajo_coordinado",False))
                cl["trabajo_finalizado"] = st.checkbox("Trabajo finalizado", value=cl.get("trabajo_finalizado",False))

            t["observaciones"] = st.text_area("Observaciones", value=t.get("observaciones",""))
            nuevo_historial = st.text_area("Agregar movimiento al historial")
            guardar = st.form_submit_button("Guardar cambios")
            if guardar:
                add_history(t, nuevo_historial)
                t["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_data(data)
                st.success("Tarea actualizada.")

        st.markdown("### Historial")
        if t["historial"]:
            for item in reversed(t["historial"]):
                st.markdown(f"- **{item['fecha']}** — {item['detalle']}")
        else:
            st.caption("Esta tarea todavía no tiene movimientos registrados.")

with tabs[3]:
    st.subheader("Editar nombres de consorcios")
    with st.form("consorcios"):
        nuevos = []
        for c in data["consorcios"]:
            nombre = st.text_input(f"Consorcio {c['id']}", value=c["nombre"])
            nuevos.append({"id": c["id"], "nombre": nombre})
        if st.form_submit_button("Guardar nombres"):
            data["consorcios"] = nuevos
            save_data(data)
            st.success("Nombres actualizados.")

with tabs[4]:
    df = tasks_df(data)
    if df.empty:
        st.info("No hay tareas para reportar.")
    else:
        cons = st.selectbox("Consorcio para reporte", ["Todos"]+[c["id"] for c in data["consorcios"]], format_func=lambda x: "Todos" if x=="Todos" else f"{x} - {cons_name(data,x)}")
        estado = st.multiselect("Estados a incluir", ESTADOS, default=ESTADOS)
        if cons != "Todos":
            df = df[df["consorcio_id"] == cons]
        if estado:
            df = df[df["estado"].isin(estado)]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Descargar reporte Excel", data=export_excel(df), file_name=f"reporte_consorcios_{date.today().isoformat()}.xlsx")

        st.subheader("Resumen para copiar y mandar")
        lines = []
        ids = df["id"].tolist()
        for t in data["tareas"]:
            if t["id"] in ids:
                lines.append(
                    f"• {cons_name(data,t['consorcio_id'])} — {t['titulo']} | Estado: {t.get('estado','')} | "
                    f"Próximo paso: {t.get('proximo_paso','')} | Consejo: {'Sí' if t.get('enviado_consejo') else 'No'}"
                )
        st.code("\n".join(lines), language="markdown")
