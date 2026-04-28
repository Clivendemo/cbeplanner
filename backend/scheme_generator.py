"""
Scheme of Work PDF Generator
Generates professional landscape A4 PDF documents
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List


# Default lessons per week based on subject and grade level
LESSONS_PER_WEEK_CONFIG = {
    # Lower Primary (Grade 1-3)
    "lower_primary": {
        "Literacy Activities": 5,
        "Literacy": 5,
        "English": 5,
        "Kiswahili": 5,
        "Mathematics Activities": 5,
        "Mathematics": 5,
        "Environmental Activities": 4,
        "Hygiene and Nutrition Activities": 3,
        "Creative Activities": 4,
        "Religious Education Activities": 3,
        "CRE": 3,
        "IRE": 3,
        "HRE": 3,
        "default": 4
    },
    # Upper Primary (Grade 4-6)
    "upper_primary": {
        "English": 5,
        "Kiswahili": 5,
        "Mathematics": 5,
        "Science and Technology": 4,
        "Social Studies": 3,
        "Religious Education": 2,
        "CRE": 2,
        "IRE": 2,
        "Creative Arts": 3,
        "Physical and Health Education": 2,
        "Agriculture": 2,
        "Home Science": 2,
        "default": 3
    },
    # Junior Secondary (Grade 7-9)
    "junior_secondary": {
        "English": 5,
        "Kiswahili": 4,
        "Mathematics": 5,
        "Integrated Science": 5,
        "Social Studies": 4,
        "Religious Education": 2,
        "CRE": 2,
        "IRE": 2,
        "Pre-Technical Studies": 4,
        "Agriculture": 3,
        "Business Studies": 3,
        "Creative Arts and Sports": 3,
        "default": 4
    },
    # Senior Secondary (Grade 10+)
    "senior_secondary": {
        "Mathematics": 5,
        "English": 5,
        "Kiswahili": 4,
        "Biology": 4,
        "Chemistry": 4,
        "Physics": 4,
        "Geography": 3,
        "History": 3,
        "Business Studies": 3,
        "Computer Science": 3,
        "French": 3,
        "German": 3,
        "Mandarin": 3,
        "Arabic": 3,
        "default": 4
    }
}


def get_grade_level(grade_name: str) -> str:
    """Determine grade level category from grade name"""
    grade_lower = grade_name.lower()
    
    if any(x in grade_lower for x in ['pp1', 'pp2', 'grade 1', 'grade 2', 'grade 3']):
        return "lower_primary"
    elif any(x in grade_lower for x in ['grade 4', 'grade 5', 'grade 6']):
        return "upper_primary"
    elif any(x in grade_lower for x in ['grade 7', 'grade 8', 'grade 9']):
        return "junior_secondary"
    else:
        return "senior_secondary"


def get_lessons_per_week(grade_name: str, subject_name: str) -> int:
    """Get the default lessons per week for a subject in a grade"""
    grade_level = get_grade_level(grade_name)
    config = LESSONS_PER_WEEK_CONFIG.get(grade_level, LESSONS_PER_WEEK_CONFIG["upper_primary"])
    
    # Try exact match first
    if subject_name in config:
        return config[subject_name]
    
    # Try partial match
    for key, value in config.items():
        if key.lower() in subject_name.lower() or subject_name.lower() in key.lower():
            return value
    
    return config.get("default", 4)


def create_scheme_styles():
    """Create custom styles for scheme PDF — pure black text on white background."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='SchoolName', parent=styles['Heading1'],
        fontSize=14, textColor=colors.black, alignment=TA_CENTER,
        spaceAfter=4, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='SchemeTitle', parent=styles['Heading2'],
        fontSize=12, textColor=colors.black, alignment=TA_CENTER,
        spaceAfter=8, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='InfoText', parent=styles['Normal'],
        fontSize=11, textColor=colors.black, alignment=TA_CENTER,
        spaceAfter=14, fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        name='TableCell', parent=styles['Normal'],
        fontSize=10, textColor=colors.black, leading=12, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='TableHeader', parent=styles['Normal'],
        fontSize=11, textColor=colors.black, fontName='Helvetica-Bold',
        alignment=TA_CENTER, leading=13,
    ))
    styles.add(ParagraphStyle(
        name='BreakCell', parent=styles['Normal'],
        fontSize=10, textColor=colors.black, fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    ))
    return styles


def generate_scheme_pdf(scheme_data: Dict[str, Any]) -> bytes:
    """Generate a professional landscape A4 PDF for Scheme of Work with title cover page."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    styles = create_scheme_styles()
    elements = []
    
    # Check if this is a Kiswahili subject
    subject = scheme_data.get('subjectName', '')
    is_kiswahili = 'kiswahili' in subject.lower() or 'fasihi' in subject.lower()
    
    school_name = scheme_data.get('schoolName', '') or 'SCHOOL NAME'
    term = scheme_data.get('term', 1)
    grade = scheme_data.get('gradeName', '')
    year = scheme_data.get('year', datetime.now().year)

    # ===== COVER / TITLE PAGE =====
    # Vertically center the block by pushing from the top with a Spacer.
    # Landscape A4 = 21cm height - 2cm margins = ~19cm usable.
    # Our title block is ~5cm tall, so spacer ≈ 7cm top-padding.
    cover_styles = getSampleStyleSheet()
    cover_title = ParagraphStyle(
        'CoverTitle', parent=cover_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=36, alignment=TA_CENTER,
        textColor=colors.black, spaceAfter=0, leading=44,
    )
    cover_school = ParagraphStyle(
        'CoverSchool', parent=cover_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER,
        textColor=colors.black, spaceAfter=0, leading=30,
    )
    cover_subtitle = ParagraphStyle(
        'CoverSubtitle', parent=cover_styles['Normal'],
        fontName='Helvetica', fontSize=18, alignment=TA_CENTER,
        textColor=colors.black, spaceAfter=0, leading=24,
    )
    cover_meta = ParagraphStyle(
        'CoverMeta', parent=cover_styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER,
        textColor=colors.black, spaceAfter=0, leading=18,
    )

    elements.append(Spacer(1, 4.5*cm))
    elements.append(Paragraph(school_name.upper(), cover_school))
    elements.append(Spacer(1, 0.7*cm))
    if is_kiswahili:
        elements.append(Paragraph('MPANGO WA KAZI', cover_title))
    else:
        elements.append(Paragraph('SCHEME OF WORK', cover_title))
    elements.append(Spacer(1, 0.7*cm))
    elements.append(Paragraph(subject.upper() if subject else '', cover_subtitle))
    elements.append(Spacer(1, 0.4*cm))
    if is_kiswahili:
        elements.append(Paragraph(f'MUHULA WA {term} &middot; {year}', cover_meta))
    else:
        elements.append(Paragraph(f'TERM {term} &middot; {year}', cover_meta))
    if grade:
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(grade.upper(), cover_meta))
    elements.append(PageBreak())

    # ===== CONTENT PAGE HEADER =====
    elements.append(Paragraph(school_name.upper(), styles['SchoolName']))
    if is_kiswahili:
        elements.append(Paragraph(f"MPANGO WA KAZI – MUHULA WA {term}", styles['SchemeTitle']))
    else:
        elements.append(Paragraph(f"SCHEME OF WORK – TERM {term}", styles['SchemeTitle']))

    if is_kiswahili:
        info_text = f"<b>Darasa:</b> {grade}  |  <b>Somo:</b> {subject}  |  <b>Mwaka:</b> {year}"
    else:
        info_text = f"<b>Grade:</b> {grade}  |  <b>Subject:</b> {subject}  |  <b>Year:</b> {year}"
    elements.append(Paragraph(info_text, styles['InfoText']))
    
    # Table headers - Kiswahili or English
    if is_kiswahili:
        headers = ['WIKI', 'SOM', 'MADA KUU', 'MADA NDOGO', 'MATOKEO MAALUM YA UJIFUNZAJI', 
                   'SWALI IBUKA', 'SHUGHULI ZA UJIFUNZAJI', 'NYENZO ZA KUJIFUNZA', 
                   'TATHMINI', 'TAFAK']
    else:
        headers = ['WK', 'LSN', 'STRAND', 'SUB-STRAND', 'SPECIFIC LEARNING OUTCOMES', 
                   'KEY INQUIRY QUESTION', 'LEARNING EXPERIENCES', 'LEARNING RESOURCES', 
                   'ASSESSMENT', 'REFL']
    
    # Column widths optimized for 10pt font (landscape A4 = ~29.7cm, minus margins = ~27.7cm)
    col_widths = [0.9*cm, 0.9*cm, 2.4*cm, 2.4*cm, 4.3*cm, 3.4*cm, 4.3*cm, 3*cm, 3*cm, 1.5*cm]
    
    # Build table data
    table_data = []
    
    # Header row
    header_row = [Paragraph(h, styles['TableHeader']) for h in headers]
    table_data.append(header_row)
    
    # Helper: pick first inquiry question from list/string
    def _single_inquiry(val) -> str:
        if not val:
            return ''
        if isinstance(val, list):
            return str(val[0]).strip() if val else ''
        return str(val).strip().split('\n')[0].strip()

    # Content rows with week / strand / substrand deduplication
    # Also: merge consecutive break rows of the same type into a single row,
    # keep the week column visible, span columns 2-10 for the break name.
    lessons = scheme_data.get('lessons', [])
    prev_week = None
    prev_strand = None
    prev_substrand = None

    # Merge consecutive break lessons of the same type
    def _merge_breaks(items):
        merged = []
        i = 0
        while i < len(items):
            cur = items[i]
            if cur.get('isBreak'):
                btype = str(cur.get('breakType', 'BREAK')).upper()
                week = cur.get('week', '')
                j = i + 1
                # Collect consecutive breaks of same type
                while j < len(items) and items[j].get('isBreak') and str(items[j].get('breakType', 'BREAK')).upper() == btype:
                    j += 1
                merged.append({
                    '_merged_break': True,
                    'breakType': btype,
                    'week': week,
                    'endWeek': items[j - 1].get('week', week),
                })
                i = j
            else:
                merged.append(cur)
                i += 1
        return merged

    for lesson in _merge_breaks(lessons):
        if lesson.get('_merged_break'):
            break_name = lesson['breakType']
            wk_from = lesson.get('week', '')
            wk_to = lesson.get('endWeek', wk_from)
            week_cell = str(wk_from) if wk_from == wk_to else f"{wk_from}-{wk_to}"
            # Week cell visible; rest of the row spans as the break label
            break_row = [
                Paragraph(week_cell, styles['TableCell']),
                Paragraph(break_name, styles['BreakCell']),
            ] + [''] * 8
            table_data.append(break_row)
            prev_week = None
            prev_strand = None
            prev_substrand = None
            continue

        week = lesson.get('week', '')
        lsn = lesson.get('lesson', '')
        strand = lesson.get('strand', '')
        substrand = lesson.get('substrand', '')
        slo = lesson.get('slo', '')
        inquiry_raw = lesson.get('keyInquiryQuestions', '')
        experiences = lesson.get('learningExperiences', '')
        resources = lesson.get('learningResources', '')
        assessment = lesson.get('assessmentMethods', '')

        # Dedupe: only show week / strand / sub-strand if they differ from prev row
        week_display = str(week) if week != prev_week else ''
        strand_display = strand if strand != prev_strand else ''
        substrand_display = substrand if (substrand != prev_substrand or strand != prev_strand) else ''

        prev_week = week
        prev_strand = strand
        prev_substrand = substrand

        # Single inquiry question per lesson
        inquiry = _single_inquiry(inquiry_raw)

        # Lesson label: strip "(Dbl)" and similar double-lesson suffixes
        lsn_display = str(lsn)

        row = [
            Paragraph(week_display, styles['TableCell']),
            Paragraph(lsn_display, styles['TableCell']),
            Paragraph(strand_display, styles['TableCell']),
            Paragraph(substrand_display, styles['TableCell']),
            Paragraph(slo, styles['TableCell']),
            Paragraph(inquiry, styles['TableCell']),
            Paragraph(experiences if isinstance(experiences, str) else '\n'.join(experiences[:3]) if experiences else '', styles['TableCell']),
            Paragraph(resources if isinstance(resources, str) else ', '.join(resources[:4]) if resources else '', styles['TableCell']),
            Paragraph(assessment if isinstance(assessment, str) else ', '.join(assessment[:2]) if assessment else '', styles['TableCell']),
            Paragraph('', styles['TableCell'])  # Reflection column (empty for teacher to fill)
        ]
        table_data.append(row)
    
    # Create table
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Table styling - PLAIN WHITE for clean B&W printing
    table_style = TableStyle([
        # Header styling - White background, black bold text, 11pt
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Content styling - plain white background, black text, 10pt
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Week and Lesson columns centered
        ('ALIGN', (2, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        
        # Grid - black lines for clean printing
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Thicker line below header
        
        # Padding - slightly more for larger text
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    
    # Style break rows: keep week col visible, span columns 2-10 for the break name
    # Break rows are detected by scanning built table_data for our sentinel.
    for row_idx, row in enumerate(table_data):
        if row_idx == 0:
            continue  # header
        # Our merged break row has Paragraph in cols 0 and 1, empty strings in 2-9
        if len(row) >= 10 and isinstance(row[2], str) and row[2] == '' and isinstance(row[1], Paragraph):
            # Detect by checking row[1] text style via Paragraph.style.name == 'BreakCell'
            try:
                style_name = getattr(row[1].style, 'name', '')
            except Exception:
                style_name = ''
            if style_name == 'BreakCell':
                table_style.add('SPAN', (1, row_idx), (-1, row_idx))
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.white)
                table_style.add('ALIGN', (1, row_idx), (-1, row_idx), 'CENTER')
                table_style.add('VALIGN', (0, row_idx), (-1, row_idx), 'MIDDLE')
                table_style.add('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold')
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 0.5*cm))
    if is_kiswahili:
        footer_text = f"Imetengenezwa na CBE Lesson Planner | {datetime.now().strftime('%d %B %Y')}"
    else:
        footer_text = f"Generated by CBE Lesson Planner | {datetime.now().strftime('%d %B %Y')}"
    elements.append(Paragraph(footer_text, styles['InfoText']))
    
    # Build PDF
    doc.build(elements)
    
    return buffer.getvalue()


# Assessment methods based on SLO action verbs
ASSESSMENT_METHODS = {
    "identify": ["Oral questions", "Matching exercise"],
    "describe": ["Written description", "Oral explanation"],
    "explain": ["Short answer questions", "Discussion"],
    "apply": ["Practical activity", "Problem solving"],
    "analyze": ["Case study", "Group discussion"],
    "appreciate": ["Reflection", "Portfolio entry"],
    "demonstrate": ["Practical demonstration", "Observation"],
    "create": ["Project work", "Creative task"],
    "evaluate": ["Critical analysis", "Peer review"],
    "default": ["Oral questions", "Written exercise"]
}


def get_assessment_for_slo(slo_text: str, is_kiswahili: bool = False) -> List[str]:
    """Determine assessment method based on SLO action verb"""
    if is_kiswahili:
        slo_lower = slo_text.lower()
        if any(v in slo_lower for v in ["eleza", "fafanua", "elezea"]):
            return ["Maswali ya mdomo", "Maandishi"]
        elif any(v in slo_lower for v in ["andika", "tunga"]):
            return ["Kazi ya maandishi", "Tathmini ya wenzake"]
        elif any(v in slo_lower for v in ["soma", "changanua"]):
            return ["Ufahamu wa kusoma", "Maswali ya mdomo"]
        elif any(v in slo_lower for v in ["onyesha", "fanya", "tumia"]):
            return ["Uchunguzi", "Kazi ya vitendo"]
        else:
            return ["Maswali ya mdomo", "Kazi ya maandishi"]

    slo_lower = slo_text.lower()
    for action, methods in ASSESSMENT_METHODS.items():
        if action in slo_lower:
            return methods
    return ASSESSMENT_METHODS["default"]


def format_slo_with_prefix(slo: str, is_kiswahili: bool = False) -> str:
    """Prefix the SLO with the standard KICD CBC lesson-outcome preamble."""
    if not slo:
        return ''
    text = str(slo).strip()
    if not text:
        return ''
    # Strip any existing preamble to avoid duplication
    import re
    patterns_en = [
        r'^by the end of the lesson,?\s*the learner should be able to:?\s*',
        r'^by the end of the lesson,?\s*the learner will be able to:?\s*',
        r'^the learner should be able to:?\s*',
    ]
    patterns_sw = [
        r'^kufikia mwisho wa somo,?\s*mwanafunzi aweze(?:\s+kuweza)?:?\s*',
        r'^mwanafunzi aweze(?:\s+kuweza)?:?\s*',
    ]
    for pat in (patterns_sw if is_kiswahili else patterns_en):
        text = re.sub(pat, '', text, flags=re.IGNORECASE).strip()
    if not text:
        return ''
    if is_kiswahili:
        return f'Kufikia mwisho wa somo, mwanafunzi aweze: {text}'
    # Ensure body begins with a verb/lowercase; preserve proper nouns as-is
    return f'By the end of the lesson, the learner should be able to: {text}'


def generate_learning_experiences(strand: str, substrand: str, slo: str) -> List[str]:
    """Generate learning experiences"""
    import re
    clean = re.sub(r'^[\d]+(?:\.[\d]+)*\.?\s*', '', substrand).strip()
    if not clean:
        clean = substrand
    
    experiences = []
    
    slo_lower = slo.lower()
    
    if 'identify' in slo_lower:
        experiences.append(f"The learner is guided to identify characteristics of {clean.lower()}")
    elif 'describe' in slo_lower:
        experiences.append(f"The learner is guided to describe {clean.lower()} using examples")
    elif 'explain' in slo_lower:
        experiences.append(f"The learner is guided to explain concepts related to {clean.lower()}")
    else:
        experiences.append(f"The learner is guided to explore {clean.lower()}")
    
    experiences.append("Group discussion and presentations")
    experiences.append("Practical activities and demonstrations")
    
    return experiences


def generate_learning_resources(strand: str, substrand: str) -> List[str]:
    """Generate learning resources"""
    return [
        "Textbooks",
        "Charts and diagrams",
        "Digital resources",
        "Realia/Models"
    ]
