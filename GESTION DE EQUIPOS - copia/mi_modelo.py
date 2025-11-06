import sqlite3, os
from datetime import datetime

DB_PATH = "datos.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = conectar()
    c = conn.cursor()

    # equipos
    c.execute("""
    CREATE TABLE IF NOT EXISTS equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        num_factura TEXT,
        mac TEXT,
        ip TEXT,
        marca TEXT,
        modelo TEXT,
        serie TEXT,
        fecha_compra TEXT,
        usuario_asignado TEXT,
        usuario_dominio TEXT,
        en_dominio TEXT,
        tiene_symantec TEXT,
        bitlocker TEXT,
        conectada_internet TEXT,
        archivo TEXT,
        fecha_registro TEXT,
        empresa TEXT,
        activo INTEGER DEFAULT 1
    )
    """)

    # =componentes
    c.execute("""
    CREATE TABLE IF NOT EXISTS componentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo_id INTEGER,
        software TEXT,
        version TEXT,
        serie_software TEXT,
        id_producto TEXT,
        llave TEXT,
        proveedor TEXT,
        aplica_proveedor TEXT,
        fecha_compra TEXT,
        fecha_vencimiento TEXT,
        archivo TEXT,
        activo INTEGER DEFAULT 1
    )
    """)

    # impres
    c.execute("""
    CREATE TABLE IF NOT EXISTS impresoras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        modelo TEXT,
        mac TEXT,
        ip TEXT,
        serie TEXT,
        area TEXT,
        archivo TEXT
    )
    """)

    # camaras
    c.execute("""
    CREATE TABLE IF NOT EXISTS camaras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        modelo TEXT,
        mac TEXT,
        ip TEXT,
        serie TEXT,
        area TEXT,
        estado TEXT,
        archivo TEXT
    )
    """)

    # otros
    c.execute("""
    CREATE TABLE IF NOT EXISTS otros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        marca TEXT,
        modelo TEXT,
        mac TEXT,
        ip TEXT,
        serie TEXT,
        area TEXT,
        descripcion TEXT,
        archivo TEXT
    )
    """)

    # busqueda de ip
    c.execute("CREATE INDEX IF NOT EXISTS idx_equipos_ip ON equipos(ip)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_impresoras_ip ON impresoras(ip)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_camaras_ip ON camaras(ip)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_otros_ip ON otros(ip)")

    conn.commit()
    conn.close()


# funciones

def obtener_todos(tabla):
    conn = conectar()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {tabla}")
    datos = c.fetchall()
    conn.close()
    return datos


def eliminar_simple(tabla, id_reg):
    conn = conectar()
    c = conn.cursor()
    c.execute(f"DELETE FROM {tabla} WHERE id=?", (id_reg,))
    conn.commit()
    conn.close()



def obtener_equipo_por_id(eid):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM equipos WHERE id=?", (eid,))
    equipo = c.fetchone()
    conn.close()
    return equipo


def obtener_componentes_por_equipo(eid):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM componentes WHERE equipo_id=?", (eid,))
    comp = c.fetchall()
    conn.close()
    return comp


def guardar_equipo(datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO equipos (nombre, num_factura, mac, ip, marca, modelo, serie, fecha_compra,
            usuario_asignado, usuario_dominio, en_dominio, tiene_symantec, bitlocker,
            conectada_internet, archivo, fecha_registro, empresa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()


def actualizar_equipo(id, datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        UPDATE equipos SET nombre=?, num_factura=?, mac=?, ip=?, marca=?, modelo=?, serie=?, fecha_compra=?,
        usuario_asignado=?, usuario_dominio=?, en_dominio=?, tiene_symantec=?, bitlocker=?,
        conectada_internet=?, empresa=? WHERE id=?
    """, datos + (id,))
    conn.commit()
    conn.close()


def actualizar_equipo_archivo(id, ruta_archivo):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE equipos SET archivo=? WHERE id=?", (ruta_archivo, id))
    conn.commit()
    conn.close()


def eliminar_equipo(id):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM equipos WHERE id=?", (id,))
    conn.commit()
    conn.close()


def set_equipo_activo(id, valor):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE equipos SET activo=? WHERE id=?", (valor, id))
    conn.commit()
    conn.close()


def contar_equipos(valor_activo=1):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM equipos WHERE activo=?", (valor_activo,))
    total = c.fetchone()[0]
    conn.close()
    return total


def buscar_equipos(q, empresa=None, solo_activos=True):
    conn = conectar()
    c = conn.cursor()
    sql = "SELECT * FROM equipos WHERE 1=1"
    params = []
    if q:
        sql += " AND (nombre LIKE ? OR ip LIKE ? OR usuario_asignado LIKE ?)"
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if empresa:
        sql += " AND empresa=?"
        params.append(empresa)
    if solo_activos:
        sql += " AND activo=1"
    c.execute(sql, params)
    res = c.fetchall()
    conn.close()
    return res




def guardar_componente(datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO componentes (equipo_id, software, version, serie_software, id_producto,
            llave, proveedor, aplica_proveedor, fecha_compra, fecha_vencimiento, archivo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()


def obtener_componente_por_id(cid):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM componentes WHERE id=?", (cid,))
    comp = c.fetchone()
    conn.close()
    return comp


def actualizar_componente(id, datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        UPDATE componentes SET software=?, version=?, serie_software=?, id_producto=?,
        llave=?, proveedor=?, aplica_proveedor=?, fecha_compra=?, fecha_vencimiento=?, archivo=? WHERE id=?
    """, datos + (id,))
    conn.commit()
    conn.close()


def eliminar_componente(id_comp):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM componentes WHERE id=?", (id_comp,))
    conn.commit()
    conn.close()


def set_componente_activo(id, valor):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE componentes SET activo=? WHERE id=?", (valor, id))
    conn.commit()
    conn.close()



def guardar_impresora(datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO impresoras (marca, modelo, mac, ip, serie, area, archivo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()


def actualizar_impresora(id_impresora, datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        UPDATE impresoras SET marca=?, modelo=?, mac=?, ip=?, serie=?, area=? WHERE id=?
    """, datos + (id_impresora,))
    conn.commit()
    conn.close()


def actualizar_impresora_archivo(id, ruta):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE impresoras SET archivo=? WHERE id=?", (ruta, id))
    conn.commit()
    conn.close()


def obtener_impresora_por_id(iid):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM impresoras WHERE id=?", (iid,))
    r = c.fetchone()
    conn.close()
    return r



def guardar_camara(datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO camaras (marca, modelo, mac, ip, serie, area, estado, archivo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()


def actualizar_camara(id_camara, datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        UPDATE camaras SET marca=?, modelo=?, mac=?, ip=?, serie=?, area=?, estado=? WHERE id=?
    """, datos + (id_camara,))
    conn.commit()
    conn.close()


def obtener_camara_por_id(cid):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM camaras WHERE id=?", (cid,))
    r = c.fetchone()
    conn.close()
    return r


def guardar_otro(datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO otros (nombre, marca, modelo, mac, ip, serie, area, descripcion, archivo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()


def actualizar_otro(id, datos):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        UPDATE otros SET nombre=?, marca=?, modelo=?, mac=?, ip=?, serie=?, area=?, descripcion=? WHERE id=?
    """, datos + (id,))
    conn.commit()
    conn.close()


def actualizar_otro_archivo(id, ruta):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE otros SET archivo=? WHERE id=?", (ruta, id))
    conn.commit()
    conn.close()


def obtener_otro_por_id(iid):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM otros WHERE id=?", (iid,))
    r = c.fetchone()
    conn.close()
    return r



def buscar_por_ip(ip):
    """
    Busca coincidencias parciales de IP en las tablas principales del sistema.
    """
    if not ip:
        return {"equipos": [], "impresoras": [], "camaras": [], "otros": []}

    ip_like = f"%{ip}%"
    conn = conectar()
    c = conn.cursor()

    # Equipos
    c.execute("SELECT * FROM equipos WHERE ip LIKE ?", (ip_like,))
    equipos = c.fetchall()

    # Impresoras
    c.execute("SELECT * FROM impresoras WHERE ip LIKE ?", (ip_like,))
    impresoras = c.fetchall()

    # Cámaras
    c.execute("SELECT * FROM camaras WHERE ip LIKE ?", (ip_like,))
    camaras = c.fetchall()

    # Otros
    c.execute("SELECT * FROM otros WHERE ip LIKE ?", (ip_like,))
    otros = c.fetchall()

    conn.close()
    return {
        "equipos": equipos,
        "impresoras": impresoras,
        "camaras": camaras,
        "otros": otros
    }


def obtener_ips_usadas():
    """Devuelve un set con todas las IPs (no vacías) encontradas en las tablas."""
    conn = conectar()
    c = conn.cursor()
    usados = set()
    tablas = ["equipos", "impresoras", "camaras", "otros"]
    for t in tablas:
        try:
            c.execute(f"SELECT ip FROM {t} WHERE ip IS NOT NULL AND ip != ''")
            rows = c.fetchall()
            for r in rows:
                if r and r[0]:
                    usados.add(str(r[0]).strip())
        except Exception:
            continue
    conn.close()
    return usados


def obtener_ips_disponibles(base_prefix, inicio=1, fin=254, max_resultados=500):
    """
    Genera IPs base_prefix.inicio .. base_prefix.fin y filtra las ya usadas.
    - base_prefix: p.ej. "192.168.1" (puede venir con o sin punto final)
    - inicio, fin: enteros
    - max_resultados: limita la cantidad devuelta (por UI)
    Retorna lista ordenada de IPs disponibles.
    """
    if not base_prefix:
        return []

    bp = str(base_prefix).strip()
    if bp.endswith("."):
        bp = bp[:-1]

    try:
        inicio = int(inicio)
    except Exception:
        inicio = 1
    try:
        fin = int(fin)
    except Exception:
        fin = 254

    if inicio < 0:
        inicio = 1
    if fin < inicio:
        fin = inicio
    if fin - inicio > 2000:
        fin = inicio + 2000

    usados = obtener_ips_usadas()
    disponibles = []
    for i in range(inicio, fin + 1):
        ip = f"{bp}.{i}"
        if ip not in usados:
            disponibles.append(ip)
            if len(disponibles) >= max_resultados:
                break

    return disponibles

