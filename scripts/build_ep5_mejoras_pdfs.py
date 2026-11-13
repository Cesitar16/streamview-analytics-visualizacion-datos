from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

root = Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('Auditoria', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('AuditoriaBold', 'C:/Windows/Fonts/arialbd.ttf'))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Titulo43', fontName='AuditoriaBold', fontSize=18, leading=22, spaceAfter=12, textColor=colors.HexColor('#173552')))
styles.add(ParagraphStyle(name='Sub43', fontName='AuditoriaBold', fontSize=11, leading=14, spaceBefore=10, spaceAfter=5, textColor=colors.HexColor('#117c75'), keepWithNext=True))
styles.add(ParagraphStyle(name='Texto43', fontName='Auditoria', fontSize=9.5, leading=14, spaceAfter=6))
styles.add(ParagraphStyle(name='Fila43', parent=styles['Texto43'], leftIndent=10, spaceAfter=4))
def fmt(s):
    s=escape(s.strip())
    s=re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s=re.sub(r'`(.+?)`', r'<font color="#117c75">\1</font>', s)
    return s
lines=(root/'docs/plan_mejoras_ep6.md').read_text(encoding='utf-8').splitlines()
story=[]; headers=[]
for line in lines:
    s=line.strip()
    if not s: continue
    if s.startswith('# '): story.append(Paragraph(fmt(s[2:]),styles['Titulo43']))
    elif s.startswith('## '): story.append(Paragraph(fmt(s[3:]),styles['Sub43']))
    elif s.startswith('|'):
        cells=[c.strip() for c in s.strip('|').split('|')]
        if all(re.fullmatch(r'[-: ]+', c) for c in cells): continue
        if cells[0] in ('Etapa y mejora','Prioridad'): headers=cells; continue
        if not headers or len(cells)!=len(headers): raise ValueError('Invalid table row: '+s)
        story.append(Paragraph(fmt(cells[0]) + (' · ' + fmt(cells[1]) if headers[0]=='Prioridad' else ''),styles['Sub43']))
        start=2 if headers[0]=='Prioridad' else 1
        for label,value in zip(headers[start:],cells[start:]):
            story.append(Paragraph('<b>'+fmt(label)+':</b> '+fmt(value),styles['Fila43']))
    elif s.startswith('- '): story.append(Paragraph('• '+fmt(s[2:]),styles['Texto43']))
    else: story.append(Paragraph(fmt(s),styles['Texto43']))
def footer(c,d):
    c.setFont('Auditoria',8); c.setFillColor(colors.grey)
    c.drawString(1.8*cm,1.1*cm,'StreamView Analytics · Anexo DUO-43')
    c.drawRightString(A4[0]-1.8*cm,1.1*cm,str(d.page))
doc=SimpleDocTemplate(str(root/'output/pdf/StreamView_EP6_Anexo_Mejoras.pdf'),pagesize=A4,leftMargin=1.8*cm,rightMargin=1.8*cm,topMargin=1.7*cm,bottomMargin=1.8*cm)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
source=(root/'scripts/build_ep2_pdfs.py').read_text(encoding='utf-8').replace('Informe_Ejecutivo_EP2.md','Informe_Ejecutivo_EP5.md').replace('StreamView_EP2_Informe.pdf','StreamView_EP5_Informe.pdf').replace('Evaluación 2 · ADY1104','Evaluación 5 · ADY1104').replace('fontSize=9.4, leading=14, textColor=NAVY', 'fontSize=9.4, leading=14, allowWidows=0, allowOrphans=0, textColor=NAVY')
namespace={'__name__':'ep5_report','__file__':str(root/'scripts/build_ep2_pdfs.py')}
exec(compile(source,str(root/'scripts/build_ep2_pdfs.py'),'exec'),namespace)
namespace['report']()
