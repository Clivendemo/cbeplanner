"""
Notes PDF Generator
Generates clean, textbook-style A4 PDFs for learner notes.
Uses ReportLab (already installed for lesson plan PDFs).
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List


def _create_styles():
    """Create text styles for the notes PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="NoteTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1F2937"),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName="Times-Bold",
    ))
    styles.add(ParagraphStyle(
        name="NoteSubTitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#4B5563"),
        alignment=TA_CENTER,
        spaceAfter=16,
        fontName="Times-Roman",
    ))
    styles.add(ParagraphStyle(
        name="SchoolHeader",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor("#111827"),
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName="Times-Bold",
    ))
    styles.add(ParagraphStyle(
        name="SectionHead",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=14,
        spaceAfter=6,
        fontName="Times-Bold",
    ))
    styles.add(ParagraphStyle(
        name="ConceptHead",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=10,
        spaceAfter=4,
        fontName="Times-Bold",
    ))
    styles.add(ParagraphStyle(
        name="NotesBody",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#374151"),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=16,
        fontName="Times-Roman",
    ))
    styles.add(ParagraphStyle(
        name="KeyTermLabel",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#1F2937"),
        fontName="Times-Bold",
    ))
    styles.add(ParagraphStyle(
        name="QuestionText",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
        leading=15,
        fontName="Times-Roman",
    ))
    styles.add(ParagraphStyle(
        name="FooterText",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#9CA3AF"),
        alignment=TA_CENTER,
    ))

    return styles


def generate_notes_pdf(notes_data: Dict[str, Any]) -> bytes:
    """
    Generate a clean textbook-style A4 PDF from structured notes data.
    Returns the PDF as bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    styles = _create_styles()
    story = []

    school_name = notes_data.get("schoolName", "").upper() or "SCHOOL NAME"
    subject = notes_data.get("subjectName", "")
    strand = notes_data.get("strandName", "")
    substrand = notes_data.get("substrandName", "")
    grade = notes_data.get("gradeName", "")
    teacher = notes_data.get("teacherName", "")
    content = notes_data.get("generatedContent", {})

    # ── Header ──
    story.append(Paragraph(school_name, styles["SchoolHeader"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("NOTES", styles["NoteTitle"]))
    story.append(Spacer(1, 6))

    # Meta info table
    meta_data = [
        ["Subject:", subject, "Grade:", grade],
        ["Strand:", strand, "Teacher:", teacher],
        ["Sub-strand:", substrand, "Date:", datetime.utcnow().strftime("%d %B %Y")],
    ]
    meta_table = Table(meta_data, colWidths=[70, 180, 60, 150])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Times-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
        ("FONTNAME", (3, 0), (3, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#374151")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D1D5DB")))
    story.append(Spacer(1, 10))

    # ── Introduction ──
    intro = content.get("introduction", "")
    if intro:
        story.append(Paragraph("INTRODUCTION", styles["SectionHead"]))
        story.append(Paragraph(intro, styles["NotesBody"]))

    # ── Main Content (concept sections) ──
    sections = content.get("sections", [])
    if sections:
        story.append(Paragraph("MAIN CONTENT", styles["SectionHead"]))
        for i, sec in enumerate(sections):
            title = sec.get("title", f"Concept {i+1}")
            story.append(Paragraph(f"{i+1}. {title}", styles["ConceptHead"]))

            explanation = sec.get("explanation", "")
            if explanation:
                story.append(Paragraph(explanation, styles["NotesBody"]))

            examples = sec.get("examples", "")
            if examples:
                story.append(Paragraph(f"<b>Examples:</b> {examples}", styles["NotesBody"]))

            applications = sec.get("applications", "")
            if applications:
                story.append(Paragraph(f"<b>Real-life Applications:</b> {applications}", styles["NotesBody"]))

    # ── Key Terms ──
    key_terms = content.get("key_terms", [])
    if key_terms:
        story.append(Paragraph("KEY TERMS", styles["SectionHead"]))
        for kt in key_terms:
            term = kt.get("term", "")
            meaning = kt.get("meaning", "")
            story.append(Paragraph(f"<b>{term}:</b> {meaning}", styles["NotesBody"]))

    # ── Practice Questions ──
    questions = content.get("practice_questions", [])
    if questions:
        story.append(Paragraph("PRACTICE QUESTIONS", styles["SectionHead"]))
        for j, q in enumerate(questions):
            story.append(Paragraph(f"{j+1}. {q}", styles["QuestionText"]))
        story.append(Spacer(1, 6))

    # ── Summary ──
    summary = content.get("summary", "")
    if summary:
        story.append(Paragraph("SUMMARY", styles["SectionHead"]))
        story.append(Paragraph(summary, styles["NotesBody"]))

    # ── Footer ──
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by CBE Planner | KICD-Aligned Curriculum | {datetime.utcnow().strftime('%d %B %Y')}",
        styles["FooterText"],
    ))

    doc.build(story)
    return buffer.getvalue()
