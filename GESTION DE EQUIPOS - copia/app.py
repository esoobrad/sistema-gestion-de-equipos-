from functools import wraps
import os
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, session, send_from_directory
)
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import secure_filename

from mi_modelo import (
    init_db,
    # General
    obtener_todos, eliminar_simple,
    # Equipos
    obtener_equipo_por_id, obtener_componentes_por_equipo,
    guardar_equipo, actualizar_equipo, eliminar_equipo,
    actualizar_equipo_archivo, buscar_equipos, contar_equipos, set_equipo_activo,
    # Componentes
    guardar_componente, eliminar_componente, obtener_componente_por_id,
    actualizar_componente, set_componente_activo,
    # Impresoras
    guardar_impresora, actualizar_impresora, obtener_impresora_por_id, actualizar_impresora_archivo,
    # Cámaras
    guardar_camara, actualizar_camara, obtener_camara_por_id,
    # Otros
    guardar_otro, actualizar_otro, actualizar_otro_archivo, obtener_otro_por_id,
    # Utilidades IP / búsqueda
    obtener_ips_disponibles, obtener_ips_usadas, buscar_por_ip
)

app = Flask(__name__)
app.secret_key = "seguro123" #esto esta en fase de prueba jajajaj no es el final
init_db()

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def login_requerido(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("usuario"):
            return redirect("/login")
        return f(*a, **kw)
    return wrapper


def guardar_archivo_opcional(file_storage):
    if not file_storage or not file_storage.filename.strip():
        return ""
    fname = secure_filename(file_storage.filename)
    ruta = os.path.join(UPLOAD_FOLDER, fname)
    file_storage.save(ruta)
    print(f"[UPLOAD] {ruta}")
    return ruta

@app.errorhandler(BadRequestKeyError)
def handle_bad_request_key_error(e):
    return render_template("login.html", error="Solicitud inválida o campos faltantes."), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario"):
        return redirect("/")
    if request.method != "POST":
        return render_template("login.html")
    user = (request.form.get("usuario") or "").strip()
    pwd = (request.form.get("clave") or "").strip()
    if not user or not pwd:
        return render_template("login.html", error="Por favor ingresa usuario y contraseña.")
    if user == "admin" and pwd == "123":
        session["usuario"] = user
        return redirect("/")
    return render_template("login.html", error="Credenciales inválidas.")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
@login_requerido
def dashboard():
    total_activos = contar_equipos(1)
    total_inactivos = contar_equipos(0)

    # 🔎 Búsqueda IP general (por coincidencia)
    ip_query = (request.args.get("ip") or "").strip()
    resultados_ip = None
    if ip_query:
        resultados_ip = buscar_por_ip(ip_query)

    return render_template(
        "dashboard.html",
        total_activos=total_activos,
        total_inactivos=total_inactivos,
        ip_query=ip_query,
        resultados_ip=resultados_ip
    )

#codigo de las ips libres para poder copiar y pegar

@app.route("/ips_disponibles")
@login_requerido
def ips_disponibles():
    ip_prefix = "192.168.3"
    ip_start_i = 1
    ip_end_i = 254
    disponibles = obtener_ips_disponibles(ip_prefix, ip_start_i, ip_end_i, max_resultados=1500)
    total_usadas = len(obtener_ips_usadas())
    return render_template(
        "ips_disponibles.html",
        ip_prefix=ip_prefix,
        ip_start=ip_start_i,
        ip_end=ip_end_i,
        disponibles=disponibles,
        total_usadas=total_usadas
    )


#rutas

@app.route("/equipos")
@login_requerido
def ver_equipos():
    empresa = request.args.get("empresa")
    q = (request.args.get("q") or "").strip()
    ver_inactivos = request.args.get("inactivos") == "1"
    equipos = buscar_equipos(q, empresa, solo_activos=not ver_inactivos)
    return render_template("dashboard_equipos.html",
                           equipos=equipos, empresa=empresa, q=q, ver_inactivos=ver_inactivos)


@app.route("/equipos/inactivos")
@login_requerido
def equipos_inactivos():
    return redirect("/equipos?inactivos=1")


@app.route("/equipo/<int:id>")
@login_requerido
def ver_equipo(id):
    equipo = obtener_equipo_por_id(id)
    if not equipo:
        return redirect("/equipos")
    comps = obtener_componentes_por_equipo(id)
    return render_template("equipo.html", equipo=equipo, componentes=comps)


@app.route("/nuevo_equipo", methods=["GET", "POST"])
@login_requerido
def nuevo_equipo():
    if request.method != "POST":
        return render_template("nuevo_equipo.html")
    archivo = guardar_archivo_opcional(request.files.get("archivo"))
    datos = (
        request.form.get("nombre", ""), request.form.get("num_factura", ""),
        request.form.get("mac", ""), request.form.get("ip", ""),
        request.form.get("marca", ""), request.form.get("modelo", ""),
        request.form.get("serie", ""), request.form.get("fecha_compra", ""),
        request.form.get("usuario_asignado", ""), request.form.get("usuario_dominio", ""),
        "Sí" if request.form.get("en_dominio") else "No",
        "Sí" if request.form.get("tiene_symantec") else "No",
        "Sí" if request.form.get("bitlocker") else "No",
        "Sí" if request.form.get("conectada_internet") else "No",
        archivo, datetime.now().strftime("%Y-%m-%d"),
        request.form.get("empresa", "Silicatos"),
    )
    guardar_equipo(datos)
    return redirect("/equipos")


@app.route("/editar_equipo/<int:id>", methods=["GET", "POST"])
@login_requerido
def editar_equipo(id):
    equipo = obtener_equipo_por_id(id)
    if not equipo:
        return redirect("/equipos")
    if request.method != "POST":
        return render_template("editar_equipo.html", equipo=equipo)

    datos = (
        request.form.get("nombre", ""), request.form.get("num_factura", ""),
        request.form.get("mac", ""), request.form.get("ip", ""),
        request.form.get("marca", ""), request.form.get("modelo", ""),
        request.form.get("serie", ""), request.form.get("fecha_compra", ""),
        request.form.get("usuario_asignado", ""), request.form.get("usuario_dominio", ""),
        request.form.get("en_dominio", "No"),
        request.form.get("tiene_symantec", "No"),
        request.form.get("bitlocker", "No"),
        request.form.get("conectada_internet", "No"),
        request.form.get("empresa", "Silicatos")
    )
    actualizar_equipo(id, datos)

    nuevo = guardar_archivo_opcional(request.files.get("archivo"))
    if nuevo:
        actualizar_equipo_archivo(id, nuevo)
    return redirect(f"/equipo/{id}")


@app.route("/equipo/<int:id>/toggle_activo", methods=["POST"])
@login_requerido
def toggle_activo_equipo(id):
    eq = obtener_equipo_por_id(id)
    if eq:
        set_equipo_activo(id, 0 if (eq[18] == 1) else 1)  
 
    return redirect(request.referrer or "/equipos")


@app.route("/eliminar_equipo/<int:id>")
@login_requerido
def eliminar_equipo_route(id):
    eliminar_equipo(id)
    return redirect("/equipos")


@app.route("/equipo/<int:id>/archivo")
@login_requerido
def archivo_equipo(id):
    eq = obtener_equipo_por_id(id)
    if not eq or not eq[15]:
        return "Archivo no encontrado", 404
    fname = os.path.basename(str(eq[15]).replace("\\", "/"))
    return send_from_directory(UPLOAD_FOLDER, fname)


@app.route("/equipo/<int:id>/eliminar_archivo", methods=["POST"])
@login_requerido
def eliminar_archivo_equipo(id):
    from pathlib import Path
    eq = obtener_equipo_por_id(id)
    if eq and eq[15]:
        fname = os.path.basename(str(eq[15]).replace("\\", "/"))
        real = Path(UPLOAD_FOLDER) / fname
        if real.exists():
            try:
                real.unlink()
            except Exception as e:
                print(f"No se pudo borrar {real}: {e}")
        actualizar_equipo_archivo(id, "")
    return redirect(f"/equipo/{id}")


@app.route("/equipo/<int:equipo_id>/nuevo", methods=["GET", "POST"])
@login_requerido
def nuevo_componente(equipo_id):
    if request.method != "POST":
        return render_template("nuevo_componente.html", equipo_id=equipo_id)
    archivo = guardar_archivo_opcional(request.files.get("archivo"))
    datos = (
        equipo_id,
        request.form.get("software", ""), request.form.get("version", ""),
        request.form.get("serie_software", ""), request.form.get("id_producto", ""),
        request.form.get("llave", ""),
        request.form.get("proveedor", ""),
        request.form.get("aplica_proveedor", "No"),
        request.form.get("fecha_compra", ""),
        request.form.get("fecha_vencimiento", ""),
        archivo
    )
    guardar_componente(datos)
    return redirect(f"/equipo/{equipo_id}")


@app.route("/editar_componente/<int:comp_id>/<int:equipo_id>", methods=["GET", "POST"])
@login_requerido
def editar_componente(comp_id, equipo_id):
    comp = obtener_componente_por_id(comp_id)
    if not comp:
        return redirect(f"/equipo/{equipo_id}")
    if request.method != "POST":
        return render_template("editar_componente.html", comp=comp, equipo_id=equipo_id)

    archivo_final = comp[11] or ""
    nuevo = guardar_archivo_opcional(request.files.get("archivo"))
    if nuevo:
        archivo_final = nuevo

    datos_update = (
        request.form.get("software", ""),
        request.form.get("version", ""),
        request.form.get("serie_software", ""),
        request.form.get("id_producto", ""),
        request.form.get("llave", ""),
        request.form.get("proveedor", ""),
        request.form.get("aplica_proveedor", "No"),
        request.form.get("fecha_compra", ""),
        request.form.get("fecha_vencimiento", ""),
        archivo_final,
    )
    actualizar_componente(comp_id, datos_update)
    return redirect(f"/equipo/{equipo_id}")


@app.route("/eliminar_componente/<int:comp_id>/<int:equipo_id>")
@login_requerido
def eliminar_componente_route(comp_id, equipo_id):
    eliminar_componente(comp_id)
    return redirect(f"/equipo/{equipo_id}")


@app.route("/eliminar_archivo_componente/<int:comp_id>/<int:equipo_id>", methods=["POST"])
@login_requerido
def eliminar_archivo_componente(comp_id, equipo_id):
    from pathlib import Path
    comp = obtener_componente_por_id(comp_id)
    if comp and comp[11]:
        fname = os.path.basename(str(comp[11]).replace("\\", "/"))
        real = Path(UPLOAD_FOLDER) / fname
        if real.exists():
            try:
                real.unlink()
            except Exception as e:
                print(f"No se pudo borrar {real}: {e}")
        datos_update = (comp[2], comp[3], comp[4], comp[5], comp[6],
                        comp[7], comp[8], comp[9], comp[10], "")
        actualizar_componente(comp_id, datos_update)
    return redirect(f"/equipo/{equipo_id}")



@app.route("/impresoras")
@login_requerido
def ver_impresoras():
    datos = obtener_todos("impresoras")
    return render_template("dashboard_impresoras.html", datos=datos)


@app.route("/nueva_impresora", methods=["GET", "POST"])
@login_requerido
def nueva_impresora():
    if request.method != "POST":
        return render_template("nueva_impresora.html")
    archivo = guardar_archivo_opcional(request.files.get("archivo"))
    datos = (
        request.form.get("marca", ""), request.form.get("modelo", ""),
        request.form.get("mac", ""), request.form.get("ip", ""),
        request.form.get("serie", ""), request.form.get("area", ""), archivo
    )
    guardar_impresora(datos)
    return redirect("/impresoras")


@app.route("/editar_impresora/<int:id>", methods=["GET", "POST"])
@login_requerido
def editar_impresora(id):
    impresora = obtener_impresora_por_id(id)
    if not impresora:
        return redirect("/impresoras")
    if request.method != "POST":
        return render_template("editar_impresora.html", impresora=impresora)
    datos = (
        request.form.get("marca", ""), request.form.get("modelo", ""),
        request.form.get("mac", ""), request.form.get("ip", ""),
        request.form.get("serie", ""), request.form.get("area", "")
    )
    actualizar_impresora(id, datos)
    nuevo = guardar_archivo_opcional(request.files.get("archivo"))
    if nuevo:
        actualizar_impresora_archivo(id, nuevo)
    return redirect("/impresoras")


@app.route("/eliminar_impresora/<int:id>")
@login_requerido
def eliminar_impresora(id):
    eliminar_simple("impresoras", id)
    return redirect("/impresoras")


@app.route("/impresora/<int:id>/archivo")
@login_requerido
def archivo_impresora(id):
    imp = obtener_impresora_por_id(id)
    if not imp or len(imp) < 8 or not imp[7]:
        return "Archivo no encontrado", 404
    fname = os.path.basename(str(imp[7]).replace("\\", "/"))
    return send_from_directory(UPLOAD_FOLDER, fname)


@app.route("/impresora/<int:id>/eliminar_archivo", methods=["POST"])
@login_requerido
def eliminar_archivo_impresora(id):
    from pathlib import Path
    imp = obtener_impresora_por_id(id)
    if imp and imp[7]:
        fname = os.path.basename(str(imp[7]).replace("\\", "/"))
        real = Path(UPLOAD_FOLDER) / fname
        if real.exists():
            try:
                real.unlink()
            except Exception as e:
                print(f"No se pudo borrar {real}: {e}")
        actualizar_impresora_archivo(id, "")
    return redirect("/impresoras")


@app.route("/camaras")
@login_requerido
def ver_camaras():
    datos = obtener_todos("camaras")
    return render_template("dashboard_camaras.html", datos=datos)


@app.route("/nueva_camara", methods=["GET", "POST"])
@login_requerido
def nueva_camara():
    if request.method != "POST":
        return render_template("nueva_camara.html")
    archivo = guardar_archivo_opcional(request.files.get("archivo"))
    datos = (
        request.form.get("marca",""), request.form.get("modelo",""),
        request.form.get("mac",""), request.form.get("ip",""),
        request.form.get("serie",""), request.form.get("area",""),
        request.form.get("estado",""), archivo
    )
    guardar_camara(datos)
    return redirect("/camaras")


@app.route("/editar_camara/<int:id>", methods=["GET","POST"])
@login_requerido
def editar_camara(id):
    cam = obtener_camara_por_id(id)
    if not cam:
        return redirect("/camaras")
    if request.method != "POST":
        return render_template("editar_camara.html", camara=cam)
    datos = (
        request.form.get("marca",""), request.form.get("modelo",""),
        request.form.get("mac",""), request.form.get("ip",""),
        request.form.get("serie",""), request.form.get("area",""),
        request.form.get("estado","")
    )
    actualizar_camara(id, datos)
    return redirect("/camaras")


@app.route("/eliminar_camara/<int:id>")
@login_requerido
def eliminar_camara(id):
    eliminar_simple("camaras", id)
    return redirect("/camaras")


@app.route("/otros")
@login_requerido
def ver_otros():
    datos = obtener_todos("otros")
    return render_template("dashboard_otros.html", datos=datos)


@app.route("/nuevo_otro", methods=["GET", "POST"])
@login_requerido
def nuevo_otro():
    if request.method != "POST":
        return render_template("nuevo_otro.html")
    archivo = guardar_archivo_opcional(request.files.get("archivo"))
    datos = (
        request.form.get("nombre","").strip(),
        request.form.get("marca",""), request.form.get("modelo",""),
        request.form.get("mac",""), request.form.get("ip",""),
        request.form.get("serie",""), request.form.get("area",""),
        request.form.get("descripcion",""), archivo
    )
    guardar_otro(datos)
    return redirect("/otros")


@app.route("/editar_otro/<int:id>", methods=["GET", "POST"])
@login_requerido
def editar_otro(id):
    otro = obtener_otro_por_id(id)
    if not otro:
        return redirect("/otros")
    if request.method != "POST":
        return render_template("editar_otro.html", otro=otro)

    datos = (
        request.form.get("nombre","").strip(),
        request.form.get("marca",""), request.form.get("modelo",""),
        request.form.get("mac",""), request.form.get("ip",""),
        request.form.get("serie",""), request.form.get("area",""),
        request.form.get("descripcion","")
    )
    actualizar_otro(id, datos)

    nuevo = guardar_archivo_opcional(request.files.get("archivo"))
    if nuevo:
        actualizar_otro_archivo(id, nuevo)
    return redirect("/otros")


@app.route("/eliminar_otro/<int:id>")
@login_requerido
def eliminar_otro(id):
    eliminar_simple("otros", id)
    return redirect("/otros")


@app.route("/otro/<int:id>/archivo")
@login_requerido
def archivo_otro(id):
    otro = obtener_otro_por_id(id)
    if not otro or len(otro) < 10 or not otro[9]:
        return "Archivo no encontrado", 404
    fname = os.path.basename(str(otro[9]).replace("\\", "/"))
    return send_from_directory(UPLOAD_FOLDER, fname)


@app.route("/otro/<int:id>/eliminar_archivo", methods=["POST"])
@login_requerido
def eliminar_archivo_otro(id):
    from pathlib import Path
    otro = obtener_otro_por_id(id)
    if otro and len(otro) >= 10 and otro[9]:
        fname = os.path.basename(str(otro[9]).replace("\\", "/"))
        real = Path(UPLOAD_FOLDER) / fname
        if real.exists():
            try:
                real.unlink()
            except Exception as e:
                print(f"No se pudo borrar {real}: {e}")
        actualizar_otro_archivo(id, "")
    return redirect("/otros")

@app.route("/reporte_equipos")
@login_requerido
def reporte_equipos_pdf():
    from pdfs import generar_reporte_pdf_equipos
    generar_reporte_pdf_equipos()
    return redirect("/static/reporte_equipos.pdf")


@app.route("/csv_equipos")
@login_requerido
def reporte_equipos_csv():
    from pdfs import generar_reporte_csv_equipos
    generar_reporte_csv_equipos()
    return redirect("/static/reporte_equipos.csv")


@app.route("/reporte_impresoras")
@login_requerido
def reporte_impresoras_pdf():
    from pdfs import generar_reporte_pdf_impresoras
    generar_reporte_pdf_impresoras()
    return redirect("/static/reporte_impresoras.pdf")


@app.route("/csv_impresoras")
@login_requerido
def reporte_impresoras_csv():
    from pdfs import generar_reporte_csv_impresoras
    generar_reporte_csv_impresoras()
    return redirect("/static/reporte_impresoras.csv")


@app.route("/reporte_camaras")
@login_requerido
def reporte_camaras_pdf():
    from pdfs import generar_reporte_pdf_camaras
    generar_reporte_pdf_camaras()
    return redirect("/static/reporte_camaras.pdf")


@app.route("/csv_camaras")
@login_requerido
def reporte_camaras_csv():
    from pdfs import generar_reporte_csv_camaras
    generar_reporte_csv_camaras()
    return redirect("/static/reporte_camaras.csv")


@app.route("/reporte_otros")
@login_requerido
def reporte_otros_pdf():
    from pdfs import generar_reporte_pdf_otros
    generar_reporte_pdf_otros()
    return redirect("/static/reporte_otros.pdf")


@app.route("/csv_otros")
@login_requerido
def reporte_otros_csv():
    from pdfs import generar_reporte_csv_otros
    generar_reporte_csv_otros()
    return redirect("/static/reporte_otros.csv")

@app.route("/uploads/<path:filename>")
@login_requerido
def descargar_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/routes")
@login_requerido
def routes():
    reglas = sorted([f"{r.endpoint:30s}  {r.rule}" for r in app.url_map.iter_rules()])
    return "<pre>" + "\n".join(reglas) + "</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

