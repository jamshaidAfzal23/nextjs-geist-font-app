"""
Report generation service for the Smart CRM SaaS application.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

def generate_pdf_report(title: str, content: list) -> BytesIO:
    """
    Generates a PDF report with the given title and content.
    Content should be a list of ReportLab flowables (e.g., Paragraph, Table).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph(title, styles['h1']))
    story.append(Spacer(1, 0.2 * 100))
    
    for item in content:
        if isinstance(item, str):
            story.append(Paragraph(item, styles['Normal']))
        else:
            story.append(item)
        story.append(Spacer(1, 0.1 * 100))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_table_flowable(data: list, col_widths: list = None) -> Table:
    """
    Creates a ReportLab Table flowable from a list of lists.
    The first sublist is assumed to be the header.
    """
    styles = getSampleStyleSheet()
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    return table
