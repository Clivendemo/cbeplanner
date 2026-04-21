"""
Lesson Plan PDF Generator
Generates professional PDF documents from lesson plan data.
Single-responsibility module — called by server.py's /lesson-plans/{id}/pdf endpoint.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def _create_styles():
    """Build the full stylesheet used by the PDF.  Called once per render."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#6366F1'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4B5563'),
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold',
        borderPadding=4,
        backColor=colors.HexColor('#F3F4F6'),
    ))

    # The ONE body text style used everywhere for running prose.
    styles.add(ParagraphStyle(
        name='Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
    ))

    # List items — NO bulletIndent so we control bullets ourselves.
    styles.add(ParagraphStyle(
        name='ListItem',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        leftIndent=20,
        spaceAfter=4,
        leading=14,
    ))

    # Compact list item for table cells (no extra left indent).
    styles.add(ParagraphStyle(
        name='TableListItem',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#374151'),
        spaceAfter=2,
        leading=12,
    ))

    # Accent label (e.g. "Lesson 2 of 4", "Lesson-Specific Outcomes:")
    styles.add(ParagraphStyle(
        name='AccentLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1E40AF'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER,
    ))

    return styles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_date(date_str) -> str:
    """Render a date value (str or datetime) as '13 Apr 2026'."""
    if not date_str:
        return 'N/A'
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = date_str
        return dt.strftime('%d %b %Y')
    except Exception:
        return str(date_str)[:10] if date_str else 'N/A'


def format_slo_text(lesson_plan: Dict[str, Any]) -> str:
    """Single source of truth for the SLO text shown in the PDF.

    Priority: sloName → sloDescription → fallback.
    """
    return (
        lesson_plan.get('sloName')
        or lesson_plan.get('sloDescription')
        or 'N/A'
    )


def _normalise_outcome(text: str) -> str:
    """Lowercase + collapse whitespace — used to detect duplicate SLO text."""
    return ' '.join(str(text or '').lower().split())


def dedupe_lesson_specific_outcomes(
    outcomes: List[str], primary_slo: str
) -> List[str]:
    """Remove duplicates within the list and any entry that repeats the
    main SPECIFIC LEARNING OUTCOME shown above.

    The slot schema commonly stores the *same* text in both `outcome` and
    `description`, and the outcome itself is often a restatement of the
    parent SLO — this was rendering as triplicate text in the PDF.
    """
    primary_norm = _normalise_outcome(primary_slo)
    seen: set = {primary_norm} if primary_norm and primary_norm != 'n/a' else set()
    cleaned: List[str] = []
    for item in outcomes or []:
        norm = _normalise_outcome(item)
        if not norm or norm in seen:
            continue
        # Also drop if it merely prefixes or contains the primary SLO text.
        if primary_norm and (primary_norm in norm or norm in primary_norm):
            continue
        seen.add(norm)
        cleaned.append(str(item).strip())
    return cleaned


def _bullet_list(items: List[str], style) -> List[Paragraph]:
    """Return a list of Paragraph elements, each prefixed with a bullet.

    Uses the HTML entity &bull; so ReportLab renders a clean bullet
    without any list-style duplication.
    """
    out: List[Paragraph] = []
    for item in items:
        text = str(item).strip()
        # Strip any leading bullet the caller may have accidentally included.
        if text.startswith(('\u2022 ', '• ', '- ')):
            text = text[2:]
        out.append(Paragraph(f"&bull;&nbsp; {text}", style))
    return out


def _add_body_text(elements: list, text: str, style) -> None:
    """Append body prose.  Splits on double-newlines when long."""
    if not text:
        return
    if len(text) > 500:
        for para in text.split('\n\n'):
            stripped = para.strip()
            if stripped:
                elements.append(Paragraph(stripped, style))
    else:
        elements.append(Paragraph(text, style))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_lesson_plan_pdf(lesson_plan: Dict[str, Any]) -> bytes:
    """Generate a PDF document from *lesson_plan* dict and return raw bytes."""

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    S = _create_styles()
    elements: list = []

    # ── Header ────────────────────────────────────────────────────────────
    elements.append(Paragraph("LESSON PLAN", S['MainTitle']))
    elements.append(Paragraph("CBE Lesson Planner - Kenya CBC Curriculum", S['SubTitle']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB')))
    elements.append(Spacer(1, 12))

    # ── Basic information table ───────────────────────────────────────────
    info_data = [
        ['Grade:', lesson_plan.get('gradeName', 'N/A'),
         'Subject:', lesson_plan.get('subjectName', 'N/A')],
        ['Strand:', lesson_plan.get('strandName', 'N/A'),
         'Sub-strand:', lesson_plan.get('substrandName', 'N/A')],
        ['Duration:', f"{lesson_plan.get('duration', '40')} minutes",
         'Date:', _format_date(lesson_plan.get('createdAt', ''))],
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

    # ── Multi-lesson indicator ────────────────────────────────────────────
    lesson_number = lesson_plan.get('lessonNumber')
    total_lessons = lesson_plan.get('totalLessonsInSubstrand')
    if lesson_number and total_lessons:
        elements.append(Paragraph(
            f"Lesson {lesson_number} of {total_lessons}", S['AccentLabel']))

    # ── Specific Learning Outcome ─────────────────────────────────────────
    elements.append(Paragraph("SPECIFIC LEARNING OUTCOME", S['SectionHeader']))
    slo_text = format_slo_text(lesson_plan)
    elements.append(Paragraph(slo_text, S['Body']))

    # ── Lesson-Specific Outcomes (multi-lesson architecture) ──────────────
    # Dedupe against the main SLO shown above AND within the list itself so
    # the slot's outcome + description (which are frequently identical, or
    # paraphrase the parent SLO) don't render as triplicate text.
    lesson_specific_outcomes = dedupe_lesson_specific_outcomes(
        lesson_plan.get('lessonSpecificOutcomes') or [], slo_text
    )
    if lesson_specific_outcomes:
        elements.append(Paragraph("Lesson-Specific Outcomes:", S['AccentLabel']))
        elements.extend(_bullet_list(lesson_specific_outcomes, S['ListItem']))

    # ── Introduction ──────────────────────────────────────────────────────
    if lesson_plan.get('introduction'):
        elements.append(Paragraph("INTRODUCTION", S['SectionHeader']))
        elements.append(Paragraph(lesson_plan['introduction'], S['Body']))

    # ── Lesson Development ────────────────────────────────────────────────
    if lesson_plan.get('lessonDevelopment'):
        elements.append(Paragraph("LESSON DEVELOPMENT", S['SectionHeader']))
        _add_body_text(elements, lesson_plan['lessonDevelopment'], S['Body'])

    # ── Extended Activity ─────────────────────────────────────────────────
    if lesson_plan.get('extendedActivity'):
        elements.append(Paragraph("EXTENDED ACTIVITY", S['SectionHeader']))
        elements.append(Paragraph(lesson_plan['extendedActivity'], S['Body']))

    # ── Conclusion ────────────────────────────────────────────────────────
    if lesson_plan.get('conclusion'):
        elements.append(Paragraph("CONCLUSION", S['SectionHeader']))
        elements.append(Paragraph(lesson_plan['conclusion'], S['Body']))

    # ── Assessment ────────────────────────────────────────────────────────
    if lesson_plan.get('assessment'):
        elements.append(Paragraph("ASSESSMENT", S['SectionHeader']))
        elements.append(Paragraph(lesson_plan['assessment'], S['Body']))

    # ── Learning Resources ────────────────────────────────────────────────
    resources: list = lesson_plan.get('learningResources') or []
    if resources:
        elements.append(Paragraph("LEARNING RESOURCES", S['SectionHeader']))
        elements.extend(_bullet_list(resources, S['ListItem']))

    # ── Core Competencies / Values / PCIs table ───────────────────────────
    competencies: list = lesson_plan.get('competencies') or []
    values: list = lesson_plan.get('values') or []
    pcis: list = lesson_plan.get('pcis') or []

    if competencies or values or pcis:
        elements.append(Spacer(1, 8))

        def _cell_html(items: list) -> str:
            if not items:
                return 'N/A'
            return '<br/>'.join(f"&bull;&nbsp; {str(i).strip()}" for i in items)

        cbc_data = [
            ['Core Competencies', 'Values', 'PCIs'],
            [
                Paragraph(_cell_html(competencies), S['TableListItem']),
                Paragraph(_cell_html(values), S['TableListItem']),
                Paragraph(_cell_html(pcis), S['TableListItem']),
            ],
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

    # ── Key Inquiry Questions ─────────────────────────────────────────────
    inquiry_questions: list = lesson_plan.get('inquiryQuestions') or []
    if inquiry_questions:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("KEY INQUIRY QUESTIONS", S['SectionHeader']))
        for idx, q in enumerate(inquiry_questions, 1):
            elements.append(Paragraph(f"{idx}. {q}", S['ListItem']))

    # ── Footer ────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB')))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"Generated by CBE Lesson Planner | {datetime.now().strftime('%d %B %Y, %H:%M')}",
        S['Footer'],
    ))
    elements.append(Paragraph(
        "Developed by LEGIT LAB | https://play.google.com/store/apps/details?id=com.legitlab.cbeplanner",
        S['Footer'],
    ))

    # ── Build ─────────────────────────────────────────────────────────────
    doc.build(elements)
    return buf.getvalue()
