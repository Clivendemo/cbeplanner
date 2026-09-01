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
from xml.sax.saxutils import escape as _xml_escape


def _pdf_text(value: Any) -> str:
    """XML-escape any raw text before it reaches a ReportLab Paragraph.

    ReportLab's Paragraph markup is a restricted XML dialect — it looks for
    tags like <br/>, <b>, <font>. Any raw curriculum or admin-entered text
    (a strand/substrand name, an SLO outcome, a resource, a break label,
    a school name) can legitimately contain '<', '>', or '&' with no
    relation to markup at all — a Math SLO reading "compare values using <
    and >", a subject called "Business & Entrepreneurship", a school name
    with an ampersand, a break label someone typed with a stray angle
    bracket. Passed through unescaped, ReportLab's parser tries to read
    the '<' as the start of a tag and fails with "parse ended with N
    unclosed tags" — which aborts the whole PDF and (per the download
    flow) refunds the user for a document that should have generated
    fine. Escaping first means our own deliberately-added tags (<br/>,
    <b>, etc.) must always be added AFTER this call, never text that's
    then run through it, or they'd be escaped into visible text too.
    """
    if value is None:
        return ''
    return _xml_escape(str(value))


# ---------------------------------------------------------------------------
# Key Inquiry Question (KIQ / Swali Ibuka / Maswali Dadisi) sanitisation
# ---------------------------------------------------------------------------
#
# Some KICD PDFs wrap a Kiswahili KIQ across two lines in the source layout
# (e.g. "Je,\n  nini umuhimu wa fasihi…?"). Earlier renderer logic split on
# '\n' and kept only the first physical line, so the user saw a bare "Je,"
# in the Swali Ibuka column. We also occasionally see the AI extractor pick
# up an isolated question particle ("Je", "Kwa nini") with no follow-up
# clause. ``_is_meaningful_kiq`` rejects those fragments so the cell stays
# blank instead of misleading the teacher.

_KIQ_PARTICLES = {
    # Kiswahili question particles that, when alone, are NOT a question.
    'je', 'je,', 'je.', 'je?', 'je:',
    'kwa', 'kwa nini', 'kwa nini?',
    'vipi', 'vipi?',
    'nini', 'nini?',
    'nani', 'nani?',
    'lini', 'lini?',
    'wapi', 'wapi?',
    'gani', 'gani?',
    'ipi', 'ipi?', 'yapi', 'yapi?',
    # English question stems likewise meaningless on their own
    'what', 'why', 'how', 'when', 'where', 'who', 'which',
    'what?', 'why?', 'how?', 'when?', 'where?', 'who?', 'which?',
}


def _is_meaningful_kiq(text: str) -> bool:
    """True iff `text` looks like a real, complete inquiry question.

    A meaningful KIQ has at least 3 words (so "Je nini umuhimu" passes but
    "Je nini" doesn't), spans at least 12 characters once whitespace is
    collapsed, and is not just a question particle in isolation.
    """
    if not text:
        return False
    collapsed = ' '.join(str(text).split()).strip()
    if not collapsed:
        return False
    if collapsed.lower().rstrip('.,;: ?!') in _KIQ_PARTICLES:
        return False
    if len(collapsed) < 12:
        return False
    if len(collapsed.split()) < 3:
        return False
    return True


def clean_kiq_list(items) -> List[str]:
    """Return a de-duplicated list of meaningful KIQs from a raw input.

    Accepts a list, a single string, or None. Drops fragments that fail
    ``_is_meaningful_kiq`` and collapses internal whitespace so KIQs that
    were soft-wrapped in the source PDF render as single-line cells.
    """
    if not items:
        return []
    if isinstance(items, str):
        items = [items]
    out: List[str] = []
    seen = set()
    for raw in items:
        cleaned = ' '.join(str(raw).split()).strip()
        if not _is_meaningful_kiq(cleaned):
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
    return out


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
        "Kiswahili": 5,
        "Biology": 5,
        "Chemistry": 5,
        "Physics": 5,
        "Geography": 5,
        "History": 5,
        "Business Studies": 5,
        "Computer Science": 5,
        "French": 5,
        "German": 5,
        "Mandarin": 5,
        "Arabic": 5,
        "default": 5
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
        # ``splitLongWords`` lets ReportLab break a single absurdly long
        # token at any character, and ``wordWrap='LTR'`` makes every line
        # break candidate explicit. Together they prevent the
        # "Flowable too large on page" crash on schemes whose SLOs or
        # learning-experience strings happen to contain a long word with
        # no whitespace (URLs, hyphenated KICD descriptors, etc.).
        splitLongWords=1, wordWrap='LTR',
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
    elements.append(Paragraph(_pdf_text(school_name).upper(), cover_school))
    elements.append(Spacer(1, 0.7*cm))
    if is_kiswahili:
        elements.append(Paragraph('MPANGO WA KAZI', cover_title))
    else:
        elements.append(Paragraph('SCHEME OF WORK', cover_title))
    elements.append(Spacer(1, 0.7*cm))
    elements.append(Paragraph(_pdf_text(subject).upper() if subject else '', cover_subtitle))
    elements.append(Spacer(1, 0.4*cm))
    if is_kiswahili:
        elements.append(Paragraph(f'MUHULA WA {_pdf_text(term)} &middot; {_pdf_text(year)}', cover_meta))
    else:
        elements.append(Paragraph(f'TERM {_pdf_text(term)} &middot; {_pdf_text(year)}', cover_meta))
    if grade:
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(_pdf_text(grade).upper(), cover_meta))
    elements.append(PageBreak())

    # ===== CONTENT PAGE HEADER =====
    elements.append(Paragraph(_pdf_text(school_name).upper(), styles['SchoolName']))
    if is_kiswahili:
        elements.append(Paragraph(f"MPANGO WA KAZI – MUHULA WA {_pdf_text(term)}", styles['SchemeTitle']))
    else:
        elements.append(Paragraph(f"SCHEME OF WORK – TERM {_pdf_text(term)}", styles['SchemeTitle']))

    if is_kiswahili:
        info_text = f"<b>Darasa:</b> {_pdf_text(grade)}  |  <b>Somo:</b> {_pdf_text(subject)}  |  <b>Mwaka:</b> {_pdf_text(year)}"
    else:
        info_text = f"<b>Grade:</b> {_pdf_text(grade)}  |  <b>Subject:</b> {_pdf_text(subject)}  |  <b>Year:</b> {_pdf_text(year)}"
    elements.append(Paragraph(info_text, styles['InfoText']))
    
    # Table headers - Kiswahili or English
    if is_kiswahili:
        headers = ['WIKI', 'SOM', 'MADA KUU', 'MADA NDOGO', 'MATOKEO MAALUM YA UJIFUNZAJI', 
                   'SWALI IBUKA', 'SHUGHULI ZA UJIFUNZAJI', 'NYENZO ZA KUJIFUNZA', 
                   'TATHMINI', 'TAFAKARI']
    else:
        headers = ['WK', 'LSN', 'STRAND', 'SUB-STRAND', 'SPECIFIC LEARNING OUTCOMES', 
                   'KEY INQUIRY QUESTION', 'LEARNING EXPERIENCES', 'LEARNING RESOURCES', 
                   'ASSESSMENT', 'REFLECTION']
    
    # Column widths, redistributed to match how much text each column
    # actually needs to hold — not evenly split, and not the same
    # allocation as before. Two things changed since these were last set:
    # (1) Strand/Sub-strand now print on every row instead of only when
    # they change, so they need to stay comfortably wide rather than
    # shrink; (2) Specific Learning Outcomes has no bullet cap (unlike
    # every other column, which is capped at 2-4 items) — a merged row
    # combining two sub-strands' SLOs routinely carries 6+ bullets, and at
    # the old 4.3cm width each one wrapped across 2-3 lines, which was the
    # single biggest driver of rows tall enough that only one fit per
    # page. Widening it (and Learning Experiences and Key Inquiry
    # Question, the other bulleted columns) means the same bullets wrap
    # across fewer lines — shorter rows with zero content removed, not a
    # font/padding trick. The previous widths also only summed to 26.1cm
    # against a 27.7cm usable page width (1cm margins each side) — that
    # 1.6cm of dead space is reclaimed here too, on top of trimming the
    # columns that hold short, already-capped content (Week, Lesson,
    # Assessment, Resources).
    col_widths = [0.8*cm, 0.8*cm, 2.8*cm, 2.4*cm, 5.2*cm, 3.6*cm, 4.7*cm, 2.8*cm, 2.6*cm, 1.5*cm]
    
    # Build table data
    table_data = []
    
    # Header row
    header_row = [Paragraph(h, styles['TableHeader']) for h in headers]
    table_data.append(header_row)
    
    # Resolve the KEY INQUIRY QUESTION cell value.
    #
    # Two distinct shapes can arrive here:
    #  - A single string: the ordinary case, one lesson = one resolved KIQ.
    #    Never split on newlines — KICD designs often wrap a question across
    #    two source lines (e.g. "Je,\nKwa nini fasihi ni muhimu?"), and a
    #    naive split previously showed just the bare "Je," in this column.
    #    Collapse whitespace instead so the wrapped question renders whole.
    #  - A list of 2+ distinct questions: only ever produced when a row
    #    merges more than one lesson's content together (a double lesson, or
    #    a compressed row covering several subtopics at once). Each item was
    #    already independently resolved to a single clean question upstream,
    #    so here we just filter/dedupe and hand the whole list to `_cell()`
    #    to render as bullets — unlike the legacy single-string list case
    #    below, we deliberately do NOT collapse to just the first one.
    def _resolve_inquiry_cell(val):
        if not val:
            return ''
        if isinstance(val, list):
            cleaned_list = []
            for q in val:
                cleaned = ' '.join(str(q).strip().split())
                if _is_meaningful_kiq(cleaned) and cleaned not in cleaned_list:
                    cleaned_list.append(cleaned)
            if len(cleaned_list) > 1:
                return cleaned_list
            return cleaned_list[0] if cleaned_list else ''
        cleaned = str(val).strip()
        if not _is_meaningful_kiq(cleaned):
            return ''
        return ' '.join(cleaned.split())

    # Cell-content cap: a single Paragraph that is *taller than a page*
    # crashes ReportLab with "Flowable too large on page" because rows are
    # atomic. We cap free-form cells (SLO, KIQ, learning experiences,
    # resources, assessment) at a safe character budget and convert any
    # newlines into ``<br/>`` so the resulting Paragraph wraps cleanly and
    # is splittable across lines (rows are still atomic, but capped cells
    # never exceed the row-height ceiling).
    _MAX_CELL_CHARS = 800

    def _cell(value, *, max_chars: int = _MAX_CELL_CHARS, max_items: int | None = None) -> Paragraph:
        if value is None or value == '':
            return Paragraph('', styles['TableCell'])
        if isinstance(value, list):
            items = [str(v).strip() for v in value if v is not None and str(v).strip()]
            if max_items is not None:
                items = items[:max_items]
            raw_text = '\n'.join(items)
        else:
            raw_text = str(value)
        raw_text = raw_text.replace('\r\n', '\n').replace('\r', '\n')

        # Truncate BEFORE escaping and BEFORE inserting <br/> tags — this
        # order is load-bearing. Once escaped ('&' -> '&amp;', '<' ->
        # '&lt;') and once '\n' has become the literal 4-character string
        # '<br/>', a plain len()-based character slice can land in the
        # middle of either one (e.g. cutting "<br/>" down to "<br", or
        # "&amp;" down to "&am"). ReportLab's paraparser then reads that
        # dangling fragment as the start of a tag/entity with no closing
        # counterpart and aborts the whole PDF with "parse ended with N
        # unclosed tags" — deterministically, for that exact content,
        # every time it's rendered. Truncating the raw plain text first
        # means the cut can only ever fall on an ordinary character.
        if len(raw_text) > max_chars:
            raw_text = raw_text[: max_chars - 1].rstrip() + '…'

        # Escape each line independently, THEN join with our own <br/>
        # tags — escaping the already-joined text would also escape those
        # tags into literal "&lt;br/&gt;" text instead of line breaks.
        text = '<br/>'.join(_pdf_text(line) for line in raw_text.split('\n'))
        return Paragraph(text, styles['TableCell'])

    # Content rows with week / strand / substrand deduplication
    # Also: merge consecutive break rows of the same type into a single row,
    # keep the week column visible, span columns 2-10 for the break name.
    lessons = scheme_data.get('lessons', [])
    prev_week = None

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
            # Week cell visible; rest of the row spans as the break label.
            # break_name is admin-typed free text (a holiday/break label) —
            # escape it like any other free-text field before it reaches
            # Paragraph.
            break_row = [
                Paragraph(_pdf_text(week_cell), styles['TableCell']),
                Paragraph(_pdf_text(break_name), styles['BreakCell']),
            ] + [''] * 8
            table_data.append(break_row)
            prev_week = None
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

        # Week keeps the "only show if it changed" convention — a week
        # genuinely spans several lesson rows and grouping it visually is a
        # deliberate, separate choice. Strand and Sub-strand are always
        # printed on every row now (not deduped against the previous row),
        # so each row reads as complete on its own rather than depending on
        # scanning upward to see which topic it belongs to.
        week_display = str(week) if week != prev_week else ''
        strand_display = strand
        substrand_display = substrand

        prev_week = week

        # Single inquiry question per lesson
        inquiry = _resolve_inquiry_cell(inquiry_raw)

        # Lesson label: strip "(Dbl)" and similar double-lesson suffixes
        lsn_display = str(lsn)

        row = [
            Paragraph(_pdf_text(week_display), styles['TableCell']),
            Paragraph(_pdf_text(lsn_display), styles['TableCell']),
            _cell(strand_display, max_chars=120),
            _cell(substrand_display, max_chars=120),
            # SLO can be a multi-bullet list when a single-lesson substrand
            # has multiple parent SLOs (the route concatenates them with
            # "- bullets"). Allow more room than the other cells so a
            # 4-bullet list still fits cleanly without truncation.
            _cell(slo, max_chars=600),
            # A merged row (double lesson, or a compressed row covering
            # several subtopics) can carry more than one KIQ, bulleted — give
            # it more room than the single-question case so the second/third
            # question isn't cut off mid-sentence.
            _cell(inquiry, max_chars=240 if isinstance(inquiry, str) else 480, max_items=3),
            _cell(experiences, max_chars=320, max_items=3),
            _cell(resources, max_chars=200, max_items=4),
            _cell(assessment, max_chars=160, max_items=2),
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
        footer_text = f""
    else:
        footer_text = f""
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


def generate_learning_experiences(strand: str, substrand: str, slo: str, is_kiswahili: bool = False) -> List[str]:
    """Generate learning experiences"""
    import re
    clean = re.sub(r'^[\d]+(?:\.[\d]+)*\.?\s*', '', substrand).strip()
    if not clean:
        clean = substrand

    experiences = []

    if is_kiswahili:
        # SLO text for a Kiswahili subject is itself in Kiswahili, so the
        # English keyword checks below ('identify', 'describe', 'explain')
        # never matched — every Kiswahili lesson fell through to the
        # English default regardless of what the SLO actually asked for.
        # Kiswahili SLOs use their own verb set (bainisha/eleza/fafanua),
        # matched here the same way.
        slo_lower = slo.lower()
        if 'bainisha' in slo_lower or 'tambua' in slo_lower:
            experiences.append(f"Mwanafunzi anaongozwa kubainisha sifa za {clean.lower()}")
        elif 'eleza' in slo_lower:
            experiences.append(f"Mwanafunzi anaongozwa kueleza {clean.lower()} kwa mifano")
        elif 'fafanua' in slo_lower:
            experiences.append(f"Mwanafunzi anaongozwa kufafanua dhana zinazohusiana na {clean.lower()}")
        else:
            experiences.append(f"Mwanafunzi anaongozwa kuchunguza {clean.lower()}")
        experiences.append("Majadiliano ya kikundi na mawasilisho")
        experiences.append("Shughuli za vitendo na maonyesho")
        return experiences

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


def generate_learning_resources(strand: str, substrand: str, is_kiswahili: bool = False) -> List[str]:
    """Generate learning resources"""
    if is_kiswahili:
        return [
            "Vitabu vya kiada",
            "Chati na michoro",
            "Nyenzo za kidijitali",
            "Vifaa halisi/Mifano",
        ]
    return [
        "Textbooks",
        "Charts and diagrams",
        "Digital resources",
        "Realia/Models"
    ]
