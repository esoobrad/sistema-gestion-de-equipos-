# pdfs.py — generación de reportes PDF/CSV

import os
import csv
from typing import List, Sequence
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from mi_modelo import obtener_todos

RUTA_REPORTES = "static"
os.makedirs(RUTA_REPORTES, exist_ok=True)

# ---------- util PDF ----------

_STYLES = getSampleStyleSheet()
_BODY = ParagraphStyle(
    "BodySmall",
    parent=_STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=9,
    leading=11,
)
_TITLE = _STYLES["Title"]

_WEIGHT_HINTS = {
    "Nombre": 2.0,
    "Usuario": 2.0,
    "Descripción": 2.2,
    "Equipo": 1.6,
    "Empresa": 1.2,
    "Modelo": 1.3,
    "MAC": 1.3,
    "IP": 1.1,
    "Fecha registro": 1.1,
    "Compra": 1.1,
    "Vence": 1.1,
    "Marca": 1.0,
    "Serie": 1.0,
    "Área": 1.0,
    "Estado": 1.0,
    "Dominio": 0.9,
    "Symantec": 0.9,
    "BitLocker": 0.9,
    "Internet": 0.9,
}


def _p(text) -> Paragraph:
    if text is None:
        text = ""
    return Paragraph(str(text), _BODY)


def _col_widths(titulos: Sequence[str], page_width: float) -> List[float]:
    weights = [_WEIGHT_HINTS.get(t, 1.0) for t in titulos]
    total = sum(weights) if sum(weights) > 0 else len(titulos)
    return [page_width * (w / total) for w in weights]


def _crear_tabla_pdf(nombre: str, titulos: Sequence[str], filas: Sequence[Sequence]) -> SimpleDocTemplate:
    pdf_path = os.path.join(RUTA_REPORTES, f"reporte_{nombre}.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=18,
        rightMargin=18,
        topMargin=24,
        bottomMargin=24,
    )

    elementos = [Paragraph(f"Reporte de {nombre.capitalize()}", _TITLE), Spacer(1, 8)]
    data = [list(titulos)] + [[_p(c) for c in fila] for fila in filas]

    page_w, _ = letter
    content_w = page_w - (doc.leftMargin + doc.rightMargin)
    col_widths = _col_widths(titulos, content_w)

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]
    left_titles = {"Nombre", "Usuario", "Descripción", "Equipo", "Modelo"}
    for idx, t in enumerate(titulos):
        if t in left_titles:
            style_cmds.append(("ALIGN", (idx, 1), (idx, -1), "LEFT"))

    tabla.setStyle(TableStyle(style_cmds))
    elementos.append(tabla)
    doc.build(elementos)
    return doc


# ---------- util CSV ----------

def _crear_csv(nombre: str, titulos: Sequence[str], filas: Sequence[Sequence]) -> None:
    csv_path = os.path.join(RUTA_REPORTES, f"reporte_{nombre}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(titulos)
        for fila in filas:
            w.writerow(["" if c is None else c for c in fila])


# ===== EQUIPOS =====
def generar_reporte_pdf_equipos():
    equipos = obtener_todos("equipos")
    titulos = ["Empresa","Nombre","Marca","Modelo","Usuario","Dominio","Symantec","BitLocker","Internet","Fecha registro"]
    filas = [
        [e[17] or "N/A", e[1] or "", e[5] or "", e[6] or "", e[9] or "",
         e[11] or "No", e[12] or "No", e[13] or "No", e[14] or "No", (e[16] or "")[:10]]
        for e in equipos
    ]
    _crear_tabla_pdf("equipos", titulos, filas)


def generar_reporte_csv_equipos():
    equipos = obtener_todos("equipos")
    titulos = ["Empresa","Nombre","Marca","Modelo","Usuario","Dominio","Symantec","BitLocker","Internet","Fecha registro"]
    filas = [
        [e[17] or "N/A", e[1] or "", e[5] or "", e[6] or "", e[9] or "",
         e[11] or "No", e[12] or "No", e[13] or "No", e[14] or "No", (e[16] or "")[:10]]
        for e in equipos
    ]
    _crear_csv("equipos", titulos, filas)


# ===== IMPRESORAS =====
def generar_reporte_pdf_impresoras():
    datos = obtener_todos("impresoras")
    titulos = ["Marca","Modelo","MAC","IP","Serie","Área"]
    filas = [[d[1] or "", d[2] or "", d[3] or "", d[4] or "", d[5] or "", d[6] or ""] for d in datos]
    _crear_tabla_pdf("impresoras", titulos, filas)


def generar_reporte_csv_impresoras():
    datos = obtener_todos("impresoras")
    titulos = ["Marca","Modelo","MAC","IP","Serie","Área"]
    filas = [[d[1] or "", d[2] or "", d[3] or "", d[4] or "", d[5] or "", d[6] or ""] for d in datos]
    _crear_csv("impresoras", titulos, filas)


# ===== CÁMARAS =====
def generar_reporte_pdf_camaras():
    datos = obtener_todos("camaras")
    titulos = ["Marca","Modelo","MAC","IP","Serie","Ubicación","Estado"]
    filas = [[d[1] or "", d[2] or "", d[3] or "", d[4] or "", d[5] or "", d[6] or "", d[7] or ""] for d in datos]
    _crear_tabla_pdf("camaras", titulos, filas)


def generar_reporte_csv_camaras():
    datos = obtener_todos("camaras")
    titulos = ["Marca","Modelo","MAC","IP","Serie","Ubicación","Estado"]
    filas = [[d[1] or "", d[2] or "", d[3] or "", d[4] or "", d[5] or "", d[6] or "", d[7] or ""] for d in datos]
    _crear_csv("camaras", titulos, filas)


# ===== OTROS =====
def generar_reporte_pdf_otros():
    datos = obtener_todos("otros")
    titulos = ["Nombre","Área","IP","Marca","Modelo","Serie","Descripción"]
    filas = [[d[7] or (d[2] or ""), d[6] or "", d[4] or "", d[1] or "", d[2] or "", d[5] or "", d[8] or ""] for d in datos]
    _crear_tabla_pdf("otros", titulos, filas)


def generar_reporte_csv_otros():
    datos = obtener_todos("otros")
    titulos = ["Nombre","Área","IP","Marca","Modelo","Serie","Descripción"]
    filas = [[d[7] or (d[2] or ""), d[6] or "", d[4] or "", d[1] or "", d[2] or "", d[5] or "", d[8] or ""] for d in datos]
    _crear_csv("otros", titulos, filas)
