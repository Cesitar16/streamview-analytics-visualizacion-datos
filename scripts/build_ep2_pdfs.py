"""Build the EP2 written report and presentation PDF from repository sources."""

from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf"
OUT.mkdir(parents=True, exist_ok=True)
FIG = ROOT / "outputs/figures"
NAVY, TEAL, ORANGE, WHITE = colors.HexColor("#071722"), colors.HexColor("#39b5a7"), colors.HexColor("#f29d58"), colors.HexColor("#eef4f7")
FONT = Path("C:/Windows/Fonts/arial.ttf")
BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
if FONT.exists() and BOLD.exists():
    pdfmetrics.registerFont(TTFont("EP2", str(FONT)))
    pdfmetrics.registerFont(TTFont("EP2Bold", str(BOLD)))
else:
    raise FileNotFoundError("Arial fonts are required for Spanish Unicode text")


def inline(text: str) -> str:
    from xml.sax.saxutils import escape
    text = escape(text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font color='#147c75'>\1</font>", text)
    return text


def report() -> None:
    source = (ROOT / "docs/Informe_Ejecutivo_EP2.md").read_text(encoding="utf-8")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="E2Title", fontName="EP2Bold", fontSize=19, leading=24, textColor=NAVY, spaceAfter=14))
    styles.add(ParagraphStyle(name="E2H2", fontName="EP2Bold", fontSize=12.5, leading=16, textColor=colors.HexColor("#117c75"), spaceBefore=13, spaceAfter=7, keepWithNext=True))
    styles.add(ParagraphStyle(name="E2Body", fontName="EP2", fontSize=9.4, leading=14, textColor=NAVY, spaceAfter=8))
    styles.add(ParagraphStyle(name="E2Bullet", parent=styles["E2Body"], leftIndent=12, firstLineIndent=-9, bulletIndent=0))
    story = []
    for raw in source.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["E2Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["E2H2"]))
        elif match := re.fullmatch(r"!\[(.+)\]\((outputs/figures/[^)]+\.png)\)", line):
            from reportlab.lib.utils import ImageReader
            figure = ROOT / match.group(2)
            iw, ih = ImageReader(str(figure)).getSize()
            scale = min(16.3 * cm / iw, 8.4 * cm / ih)
            story.append(KeepTogether([
                Image(str(figure), width=iw * scale, height=ih * scale),
                Paragraph(inline(match.group(1)), styles["E2Body"]),
            ]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + inline(line[2:]), styles["E2Bullet"]))
        else:
            story.append(Paragraph(inline(line.replace("  ", " ")), styles["E2Body"]))
    path = OUT / "StreamView_EP2_Informe.pdf"
    def footer(c, d):
        c.setFont("EP2", 8)
        c.setFillColor(colors.grey)
        c.drawString(1.8 * cm, 1.25 * cm, "StreamView Analytics · Evaluación 2 · ADY1104")
        c.drawRightString(A4[0] - 1.8 * cm, 1.25 * cm, str(d.page))
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=1.8 * cm,
                            leftMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(path)


SLIDES = [
    ("StreamView Analytics", "Evaluación de experiencia 2 | ADY1104", ["Una lectura común del catálogo para dos audiencias", "Python · D3 · Power BI", "Datos oficiales de películas y series · corte 2025"], None),
    ("Problema y audiencias", "De EP1 a decisiones explorables", ["Dirección: composición y concentración de la oferta", "Adquisición: valoración, popularidad y costos", "31.991 contenidos únicos; no hay datos de consumo de usuarios"], "peliculas_vs_series.png"),
    ("Preparación de datos", "Dos CSV originales → vistas EP1 → dashboards", ["32.000 filas originales → 31.991 títulos únicos; nueve IDs de series tienen popularidad conflictiva", "La clave content_id combina tipo y show_id; evita 397 colisiones entre películas y series", "Géneros, países y créditos pasan a tablas puente; cada título conserva una sola fila en el catálogo", "Finanzas incluye 3.540 películas con presupuesto e ingresos positivos; los CSV originales no se modifican"], None),
    ("Dashboard 1 · Streamlit", "Vista ejecutiva construida con Python, Plotly y D3", ["Python reconstruye las vistas EP1; Streamlit aplica tipo, año y género antes de calcular KPI", "Plotly muestra barras y mapa coroplético; D3 dibuja el treemap de géneros", "16.000 películas · 15.991 series · 147 países; los conteos por género y país se solapan"], "generos_predominantes.png"),
    ("Dashboard 2 · Power BI", "Seis tablas relacionadas por content_id", ["Las vistas EP1 se exportan a catálogo, géneros, países, directores, actores y finanzas", "Cinco relaciones propagan filtros; DAX usa DISTINCTCOUNT para contar títulos sin duplicarlos", "Dos páginas PBIR combinan tarjetas, segmentadores, gráficos, mapa y botón de restablecimiento"], None),
    ("Contenidos y adquisición", "Valoración, popularidad y cobertura", ["Popularidad es un índice relativo, no reproducciones; la nota requiere un mínimo de votos", "Dispersión, géneros y Top 10 responden al segmento; el mapa exige cobertura mínima por país", "Streamlit permite ajustar umbrales; Power BI ofrece medidas DAX y cruces entre visuales"], "lucas_popularidad_vs_valoracion.png"),
    ("Demostración de filtros", "Dos recorridos de interacción", ["Streamlit: filtrar tipo y género; observar KPI, barras, treemap y mapa; restablecer", "Power BI: filtrar Movie y un género; comprobar tarjetas, ranking y mapa; restablecer", "Seleccionar TV Show en la página analítica: las finanzas quedan vacías y la nota explica la cobertura"], None),
    ("Finanzas: alcance y lectura", "Solo 3.540 películas elegibles", ["Presupuesto: 125.960,8 millones; ingresos: 367.371,4 millones", "Ingresos/presupuesto: 2,9166×, no utilidad neta", "La dispersión muestra asociación y variación entre títulos"], "ignacio_budget_vs_revenue.png"),
    ("Calidad y límites", "Lo que los tableros permiten afirmar", ["rating repite la nota numérica: no existe clasificación etaria confiable", "La fecha de incorporación coincide con el año de estreno: no describe altas reales", "Solo el 22,1 % de las películas tiene finanzas elegibles; la popularidad no mide visualizaciones", "17 pruebas automáticas y revisión interactiva de ambas herramientas respaldan la demostración"], None),
    ("Conclusiones", "Qué decisión puede apoyar cada audiencia", ["Dirección: identificar concentración por tipo, género, país e idioma", "Adquisición: combinar popularidad, nota, votos y cobertura antes de revisar candidatos", "Antes de invertir: verificar derechos, costos completos y señales reales de audiencia"], None),
]


def presentation() -> None:
    path = OUT / "StreamView_EP2_Presentacion.pdf"
    w, h = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(w, h))
    for num, (title, subtitle, bullets, figure) in enumerate(SLIDES, start=1):
        c.setFillColor(NAVY); c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(TEAL); c.rect(0, h - 0.23 * cm, w, 0.23 * cm, fill=1, stroke=0)
        c.setFont("EP2Bold", 27); c.setFillColor(WHITE); c.drawString(1.4 * cm, h - 2.2 * cm, title)
        c.setFont("EP2", 14); c.setFillColor(ORANGE); c.drawString(1.45 * cm, h - 3.1 * cm, subtitle)
        text_width = 12.3 * cm if figure else w - 3 * cm
        y = h - 5.1 * cm
        for bullet in bullets:
            c.setFillColor(TEAL); c.circle(1.7 * cm, y + 0.09 * cm, 0.08 * cm, fill=1, stroke=0)
            body_size = 16.5 if figure is None else 15
            c.setFont("EP2", body_size); c.setFillColor(WHITE)
            p = Paragraph(inline(bullet), ParagraphStyle("slide", fontName="EP2", fontSize=body_size,
                                  leading=22, textColor=WHITE, alignment=TA_LEFT))
            _, ph = p.wrap(text_width - 1.5 * cm, 2 * cm)
            p.drawOn(c, 2.2 * cm, y - ph + 0.35 * cm)
            y -= max(1.65 * cm, ph + 0.6 * cm)
        if figure and (FIG / figure).exists():
            from reportlab.lib.utils import ImageReader
            img = ImageReader(str(FIG / figure))
            iw, ih = img.getSize()
            box_w, box_h = 12.3 * cm, 11.5 * cm
            scale = min(box_w / iw, box_h / ih)
            dw, dh = iw * scale, ih * scale
            c.drawImage(img, w - 1.2 * cm - dw, 2.5 * cm + (box_h - dh) / 2,
                        width=dw, height=dh, preserveAspectRatio=True, mask="auto")
        c.setFont("EP2", 9); c.setFillColor(colors.HexColor("#a7bbc7"))
        c.drawString(1.4 * cm, 1.1 * cm, "ADY1104 · Datos oficiales hasta 2025")
        c.drawRightString(w - 1.4 * cm, 1.1 * cm, f"{num} / {len(SLIDES)}")
        c.showPage()
    c.save()
    print(path)


if __name__ == "__main__":
    report()
    presentation()
