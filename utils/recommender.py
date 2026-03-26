"""
utils/recommender.py

Intelligent, personalized recommendation engine.
Generates actionable suggestions based on:
  - ATS score breakdown
  - Missing skills from job description
  - Resume completeness (email, phone, sections)
  - Category detected by ML model
"""


from typing import List, Dict

def generate_recommendations(
    parsed_data: dict,
    ats_breakdown: Dict[str, int],
    missing_skills: List[str],
    category: str,
    match_score: float,
) -> List[str]:
    """
    Generate a list of personalized improvement suggestions.

    Args:
        parsed_data:    Dict from parse_resume()
        ats_breakdown:  Per-section scores from compute_ats_score()
        missing_skills: Skills missing relative to job description
        category:       ML-predicted resume category
        match_score:    Cosine similarity match % with job description

    Returns:
        List of recommendation strings (ordered by priority).
    """
    recommendations = []

    # ── 1. Contact completeness ───────────────────────────────────────────────
    if not parsed_data.get("email"):
        recommendations.append(
            "📧 Add a professional email address — it is missing from your resume."
        )
    if not parsed_data.get("phone"):
        recommendations.append(
            "📱 Include a contact phone number to make your resume complete."
        )

    # ── 2. Skills section ─────────────────────────────────────────────────────
    skills = parsed_data.get("skills", [])
    if len(skills) < 5:
        recommendations.append(
            "🛠️ Your skills section appears thin. Aim to list at least 10–15 relevant technical and soft skills."
        )
    elif len(skills) < 10:
        recommendations.append(
            "🛠️ Expand your skills section — add more domain-specific tools, frameworks, and technologies."
        )

    # ── 3. Missing skills from JD ─────────────────────────────────────────────
    if missing_skills:
        top_missing = [x for i, x in enumerate(missing_skills) if i < 8]
        recommendations.append(
            f"🎯 Add these skills found in the job description but missing from your resume: "
            f"{', '.join(top_missing)}."
        )

    # ── 4. Experience section ─────────────────────────────────────────────────
    if ats_breakdown.get("experience", 0) < 12:
        recommendations.append(
            "💼 Strengthen your experience section — use action verbs (developed, deployed, designed) "
            "and quantify achievements (e.g., 'Improved API response time by 30%')."
        )

    # ── 5. Education section ──────────────────────────────────────────────────
    if ats_breakdown.get("education", 0) < 10:
        recommendations.append(
            "🎓 Ensure your education section clearly lists your degree, institution, and graduation year."
        )

    # ── 6. Job match score ────────────────────────────────────────────────────
    if match_score < 40:
        recommendations.append(
            "📋 Your resume matches less than 40% of the job description. "
            "Tailor your resume by mirroring keywords from the job posting."
        )
    elif match_score < 60:
        recommendations.append(
            "📋 Moderate job match. Incorporate more JD-specific terminology to improve ATS pass rate."
        )

    # ── 7. Keyword density ────────────────────────────────────────────────────
    if ats_breakdown.get("keywords", 0) < 5:
        recommendations.append(
            "🔑 Low keyword density detected. Add industry-specific buzzwords and technical terminology "
            "relevant to your field."
        )

    # ── 8. Projects & portfolio ───────────────────────────────────────────────
    recommendations.append(
        "📂 Add links to your GitHub profile, portfolio, or project repositories to stand out."
    )

    # ── 9. Category-specific advice ───────────────────────────────────────────
    category_tips = {
        "Data Science": "📊 Highlight specific ML models, datasets, and evaluation metrics you have worked with.",
        "Web Development": "🌐 Showcase live project links, frameworks (React, Django), and responsive design work.",
        "DevOps": "⚙️ Mention CI/CD pipelines, IaC tools (Terraform), and monitoring platforms you have experience with.",
        "Android": "📱 List published apps on the Play Store and mention Kotlin/Java proficiency.",
        "Java Developer": "☕ Highlight Spring Boot, REST APIs, and any design pattern expertise.",
        "Python Developer": "🐍 Emphasize libraries (FastAPI, Pandas, SQLAlchemy) and any automation scripts.",
        "Database": "🗄️ Detail experience with query optimization, indexing, and database administration.",
        "HR": "👥 Highlight HRIS systems used, hiring metrics, and employee engagement programs.",
        "Advocate": "⚖️ List case types handled, courts practiced in, and notable achievements.",
        "Mechanical Engineer": "🔧 Mention CAD software, simulation tools, and manufacturing experience.",
    }
    tip = category_tips.get(category)
    if tip:
        recommendations.append(tip)

    # ── 10. ATS formatting tips ───────────────────────────────────────────────
    recommendations.append(
        "📄 Use a clean, single-column ATS-friendly format. Avoid tables, images, or headers/footers "
        "that parsers often cannot read."
    )

    return recommendations
