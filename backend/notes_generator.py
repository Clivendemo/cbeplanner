"""
Notes Content Generator
Generates rich, paragraph-based educational notes from curriculum data.
Follows KICD CBC format for Kenyan teachers.
"""

from typing import Dict, List, Any, Optional


def generate_notes_content(
    subject_name: str,
    strand_name: str,
    substrand_name: str,
    slos: List[Dict[str, Any]],
    activities: List[Dict[str, Any]],
    grade_name: str = "",
) -> Dict[str, Any]:
    """
    Generate structured educational notes for a given sub-strand.
    Returns a dict with title, introduction, sections, key_terms, questions, summary.
    """

    slo_names = [s.get("name", s.get("description", "")) for s in slos if s]
    slo_descriptions = [s.get("description", "") for s in slos if s and s.get("description")]

    # Build main content sections from SLOs
    concept_sections = []
    for i, slo in enumerate(slos):
        name = slo.get("name", slo.get("description", f"Concept {i+1}"))
        desc = slo.get("description", "")
        section = _build_concept_section(name, desc, subject_name, strand_name, substrand_name, i + 1)
        concept_sections.append(section)

    # If no SLOs, build a generic section from strand/substrand
    if not concept_sections:
        concept_sections.append(_build_generic_section(subject_name, strand_name, substrand_name))

    introduction = _build_introduction(subject_name, strand_name, substrand_name, grade_name, slo_names)
    key_terms = _extract_key_terms(substrand_name, strand_name, slo_names, subject_name)
    questions = _build_practice_questions(substrand_name, strand_name, slo_names, subject_name)
    summary = _build_summary(substrand_name, strand_name, slo_names, subject_name)

    activity_texts = []
    for a in activities:
        if isinstance(a, dict):
            activity_texts.append(a.get("description", a.get("name", str(a))))
        elif isinstance(a, str):
            activity_texts.append(a)

    return {
        "title": substrand_name,
        "strand": strand_name,
        "substrand": substrand_name,
        "subject": subject_name,
        "grade": grade_name,
        "introduction": introduction,
        "sections": concept_sections,
        "key_terms": key_terms,
        "practice_questions": questions,
        "summary": summary,
        "activities": activity_texts,
    }


def _build_introduction(subject: str, strand: str, substrand: str, grade: str, slo_names: List[str]) -> str:
    """Build an engaging introduction paragraph."""
    slo_preview = ""
    if slo_names:
        topics = ", ".join(slo_names[:3])
        slo_preview = f" In this section, learners will explore key concepts including {topics}."

    return (
        f"{substrand} is an essential topic within the broader area of {strand} "
        f"in {subject}. Understanding this topic provides learners with foundational "
        f"knowledge and practical skills that are applicable both inside and outside "
        f"the classroom.{slo_preview} These notes have been prepared in alignment with "
        f"the KICD Competency-Based Curriculum to support effective teaching and learning."
    )


def _build_concept_section(name: str, description: str, subject: str, strand: str, substrand: str, index: int) -> Dict[str, str]:
    """Build a detailed concept section with explanation, examples, and applications."""

    # Explanation paragraph
    if description:
        explanation = (
            f"{name} is a key learning outcome within {substrand}. "
            f"{description} "
            f"This concept helps learners develop a deeper understanding of {strand} "
            f"and its relevance to everyday life. Teachers should ensure that learners "
            f"engage with this concept through both theoretical discussion and practical activities."
        )
    else:
        explanation = (
            f"{name} is an important concept within the study of {substrand}. "
            f"It forms part of the broader strand of {strand} in {subject}. "
            f"Learners are expected to demonstrate understanding of this concept through "
            f"various classroom activities, group discussions, and individual practice. "
            f"Teachers should guide learners to connect this concept with their prior "
            f"knowledge and real-world experiences."
        )

    # Examples
    examples = (
        f"To illustrate {name.lower() if len(name) < 80 else 'this concept'}, consider situations "
        f"where learners can observe or practice the concept in their immediate environment. "
        f"For instance, teachers can use locally available materials, classroom demonstrations, "
        f"or community-based examples to make the learning more meaningful and relatable. "
        f"Group activities where learners share their own examples are particularly effective."
    )

    # Applications
    applications = (
        f"The knowledge gained from studying {name.lower() if len(name) < 80 else 'this topic'} "
        f"can be applied in various real-life contexts. Learners should be encouraged to identify "
        f"how this concept relates to their daily lives, their community, and the wider world. "
        f"This helps to develop critical thinking and problem-solving skills as outlined in the "
        f"CBC framework."
    )

    return {
        "title": name,
        "explanation": explanation,
        "examples": examples,
        "applications": applications,
    }


def _build_generic_section(subject: str, strand: str, substrand: str) -> Dict[str, str]:
    """Build a generic section when no SLOs are available."""
    return {
        "title": substrand,
        "explanation": (
            f"{substrand} is an important area of study within {strand} in {subject}. "
            f"This topic covers fundamental concepts that help learners build a strong "
            f"foundation for further learning. Teachers should use a variety of teaching "
            f"strategies including discussion, demonstration, and hands-on activities "
            f"to ensure all learners can access the content."
        ),
        "examples": (
            f"Teachers can use locally available resources and real-life scenarios to "
            f"help learners understand the key concepts. Classroom activities should be "
            f"designed to cater for different learning styles and abilities."
        ),
        "applications": (
            f"The skills and knowledge acquired in this topic are applicable in daily "
            f"life and form the basis for more advanced learning in {subject}."
        ),
    }


def _extract_key_terms(substrand: str, strand: str, slo_names: List[str], subject: str) -> List[Dict[str, str]]:
    """Extract and define key terms from the topic."""
    terms = []

    # Add strand and substrand as key terms
    terms.append({
        "term": strand,
        "meaning": f"A major thematic area in {subject} that encompasses related topics and learning outcomes."
    })
    terms.append({
        "term": substrand,
        "meaning": f"A specific topic within {strand} that focuses on particular concepts and skills."
    })

    # Add first few SLOs as terms
    for slo in slo_names[:4]:
        if len(slo) < 100:
            terms.append({
                "term": slo,
                "meaning": f"A specific learning outcome that learners are expected to achieve in the study of {substrand}."
            })

    return terms


def _build_practice_questions(substrand: str, strand: str, slo_names: List[str], subject: str) -> List[str]:
    """Build practice questions for learners."""
    questions = [
        f"Define the term '{substrand}' and explain its importance in {subject}.",
        f"Describe how {substrand} relates to the broader topic of {strand}.",
    ]

    for slo in slo_names[:3]:
        short = slo if len(slo) < 60 else slo[:57] + "..."
        questions.append(f"Explain in your own words what is meant by: {short}")

    questions.extend([
        f"Give two real-life examples where the concepts learned in {substrand} can be applied.",
        f"Why is it important for learners to study {substrand}? Discuss with examples.",
    ])

    return questions


def _build_summary(substrand: str, strand: str, slo_names: List[str], subject: str) -> str:
    """Build a brief summary paragraph."""
    slo_summary = ""
    if slo_names:
        slo_summary = f" The key concepts covered include {', '.join(slo_names[:3])}."

    return (
        f"In this topic, we have explored {substrand} as part of {strand} in {subject}.{slo_summary} "
        f"Learners are encouraged to review the key terms, revisit the practice questions, "
        f"and discuss the concepts with their peers. Teachers should assess learner understanding "
        f"through both formative and summative assessment methods as recommended by the KICD CBC framework."
    )
