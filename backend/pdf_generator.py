"""
Lesson Plan PDF Generator
Generates professional PDF documents from lesson plan data
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List


def create_styles():
    """Create custom styles for the PDF"""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#6366F1'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4B5563'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold',
        borderPadding=4,
        backColor=colors.HexColor('#F3F4F6')
    ))
    
    # Body text style
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14
    ))
    
    # List item style
    styles.add(ParagraphStyle(
        name='ListItem',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        leftIndent=20,
        spaceAfter=4,
        bulletIndent=10
    ))
    
    # Info label style
    styles.add(ParagraphStyle(
        name='InfoLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6B7280'),
        fontName='Helvetica-Bold'
    ))
    
    # Info value style
    styles.add(ParagraphStyle(
        name='InfoValue',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#111827')
    ))
    
    # Footer style
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER
    ))
    
    return styles


def generate_lesson_plan_pdf(lesson_plan: Dict[str, Any]) -> bytes:
    """Generate a PDF document from lesson plan data"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = create_styles()
    elements = []
    
    # Header
    elements.append(Paragraph("LESSON PLAN", styles['MainTitle']))
    elements.append(Paragraph("CBE Lesson Planner - Kenya CBC Curriculum", styles['SubTitle']))
    
    # Divider
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB')))
    elements.append(Spacer(1, 12))
    
    # Basic Information Table
    info_data = [
        ['Grade:', lesson_plan.get('gradeName', 'N/A'), 'Subject:', lesson_plan.get('subjectName', 'N/A')],
        ['Strand:', lesson_plan.get('strandName', 'N/A'), 'Sub-strand:', lesson_plan.get('substrandName', 'N/A')],
        ['Duration:', f"{lesson_plan.get('duration', '40')} minutes", 'Date:', format_date(lesson_plan.get('createdAt', ''))]
    ]
    
    info_table = Table(info_data, colWidths=[70, 170, 80, 170])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6B7280')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#6B7280')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#111827')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))
    
    # Specific Learning Outcome
    elements.append(Paragraph("SPECIFIC LEARNING OUTCOME", styles['SectionHeader']))
    slo_text = lesson_plan.get('sloName', '') or lesson_plan.get('sloDescription', 'N/A')
    elements.append(Paragraph(slo_text, styles['BodyText']))
    
    # Introduction
    if lesson_plan.get('introduction'):
        elements.append(Paragraph("INTRODUCTION", styles['SectionHeader']))
        elements.append(Paragraph(lesson_plan['introduction'], styles['BodyText']))
    
    # Lesson Development
    if lesson_plan.get('lessonDevelopment'):
        elements.append(Paragraph("LESSON DEVELOPMENT", styles['SectionHeader']))
        # Split by paragraphs if too long
        dev_text = lesson_plan['lessonDevelopment']
        if len(dev_text) > 500:
            paragraphs = dev_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), styles['BodyText']))
        else:
            elements.append(Paragraph(dev_text, styles['BodyText']))
    
    # Extended Activity
    if lesson_plan.get('extendedActivity'):
        elements.append(Paragraph("EXTENDED ACTIVITY", styles['SectionHeader']))
        elements.append(Paragraph(lesson_plan['extendedActivity'], styles['BodyText']))
    
    # Conclusion
    if lesson_plan.get('conclusion'):
        elements.append(Paragraph("CONCLUSION", styles['SectionHeader']))
        elements.append(Paragraph(lesson_plan['conclusion'], styles['BodyText']))
    
    # Assessment
    if lesson_plan.get('assessment'):
        elements.append(Paragraph("ASSESSMENT", styles['SectionHeader']))
        elements.append(Paragraph(lesson_plan['assessment'], styles['BodyText']))
    
    # Learning Resources
    resources = lesson_plan.get('learningResources', [])
    if resources:
        elements.append(Paragraph("LEARNING RESOURCES", styles['SectionHeader']))
        for resource in resources:
            elements.append(Paragraph(f"• {resource}", styles['ListItem']))
    
    # Core Competencies, Values, PCIs in a table
    competencies = lesson_plan.get('competencies', [])
    values = lesson_plan.get('values', [])
    pcis = lesson_plan.get('pcis', [])
    
    if competencies or values or pcis:
        elements.append(Spacer(1, 8))
        
        # Create three-column layout
        comp_text = '\n'.join([f"• {c}" for c in competencies]) if competencies else 'N/A'
        values_text = '\n'.join([f"• {v}" for v in values]) if values else 'N/A'
        pcis_text = '\n'.join([f"• {p}" for p in pcis]) if pcis else 'N/A'
        
        cbc_data = [
            ['Core Competencies', 'Values', 'PCIs'],
            [Paragraph(comp_text.replace('\n', '<br/>'), styles['ListItem']),
             Paragraph(values_text.replace('\n', '<br/>'), styles['ListItem']),
             Paragraph(pcis_text.replace('\n', '<br/>'), styles['ListItem'])]
        ]
        
        cbc_table = Table(cbc_data, colWidths=[170, 170, 170])
        cbc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366F1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ]))
        elements.append(cbc_table)
    
    # Key Inquiry Questions
    inquiry_questions = lesson_plan.get('inquiryQuestions', [])
    if inquiry_questions:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("KEY INQUIRY QUESTIONS", styles['SectionHeader']))
        for i, q in enumerate(inquiry_questions, 1):
            elements.append(Paragraph(f"{i}. {q}", styles['ListItem']))
    
    # Footer
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB')))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"Generated by CBE Lesson Planner | {datetime.now().strftime('%d %B %Y, %H:%M')}",
        styles['Footer']
    ))
    elements.append(Paragraph(
        "Developed by LEGIT LAB | https://play.google.com/store/apps/details?id=com.legitlab.cbeplanner",
        styles['Footer']
    ))
    
    # Build PDF
    doc.build(elements)
    
    return buffer.getvalue()


def format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return 'N/A'
    try:
        if isinstance(date_str, str):
            # Parse ISO format
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = date_str
        return dt.strftime('%d %b %Y')
    except Exception:
        return str(date_str)[:10] if date_str else 'N/A'
