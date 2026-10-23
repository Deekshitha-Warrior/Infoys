"""Personalized, downloadable career development reports."""

import io
import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

PRACTICE = {
    "python": "Learn functions, collections, files and error handling. Build a small application with automated tests.",
    "sql": "Practice joins, grouping, subqueries and window functions. Analyze a public dataset and explain five findings.",
    "javascript": "Practice arrays, async/await, DOM events and API calls. Build an interactive page with loading and error states.",
    "react": "Practice components, state, effects and accessible forms. Build a dashboard connected to an API.",
    "git": "Practice branches, clear commits, pull requests and resolving conflicts. Keep your project history in a repository.",
    "java": "Practice object-oriented programming, collections and exceptions. Build and test a small REST service.",
    "rest api": "Learn HTTP methods, validation, authentication and error responses. Document and test a small API.",
    "machine learning": "Learn train/test splits, leakage, baselines and evaluation. Compare two models on a public dataset.",
    "pandas": "Practice cleaning missing values, joins and groupby. Create a reproducible notebook with charts and findings.",
    "statistics": "Practice distributions, sampling, confidence intervals and hypothesis testing. Explain the limits of your results.",
    "scikit-learn": "Build preprocessing and classifier pipelines. Use cross-validation without leaking test data.",
    "excel": "Practice lookup functions, pivot tables and charts. Build a spreadsheet that answers a real business question.",
    "tableau": "Build a dashboard with filters, clear measures and an explanation of the business question.",
    "power bi": "Practice data modeling, Power Query and DAX. Build an interactive dashboard with documented measures.",
    "html": "Learn semantic page structure, accessible forms and keyboard navigation. Build a structured portfolio page.",
    "css": "Practice Flexbox, Grid and responsive layouts. Test your page on narrow and wide screens.",
    "node.js": "Build an API with validation, persistence and tests. Document how to run it.",
    "selenium": "Write browser tests for a complete user journey, including failure cases and reliable selectors.",
    "testing": "Practice unit, integration and acceptance testing. Write a test plan and document meaningful defects.",
    "communication": "Write a one-page project explanation and give a five-minute walkthrough. Ask for feedback and revise.",
    "autocad": "Practice dimensioned drawings, layers and layouts. Produce a clearly annotated design portfolio example.",
    "solidworks": "Practice part modeling, assemblies and drawings. Document design decisions and constraints.",
    "financial analysis": "Build a financial model with explicit assumptions and compare alternative scenarios.",
    "seo": "Audit a sample website and propose measurable improvements to page structure, content and performance.",
    "digital marketing": "Create a campaign plan with audience, goals, channels, budget assumptions and success measures.",
}


def build_career_pdf(profile, report, target_career=None, resume=None):
    regular, bold = "Helvetica", "Helvetica-Bold"
    for normal, heavy in [
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
    ]:
        if Path(normal).exists() and Path(heavy).exists():
            if "CareerReport" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("CareerReport", normal))
                pdfmetrics.registerFont(TTFont("CareerReportBold", heavy))
                pdfmetrics.registerFontFamily(
                    "CareerReport", normal="CareerReport", bold="CareerReportBold"
                )
            regular, bold = "CareerReport", "CareerReportBold"
            break
    purple = colors.HexColor("#6945CC")
    navy = colors.HexColor("#202547")
    muted = colors.HexColor("#666C83")
    pale = colors.HexColor("#F3EFFB")
    styles = getSampleStyleSheet()
    for name, size, leading, color, font in [
        ("Title", 27, 34, navy, bold),
        ("Heading1", 20, 27, navy, bold),
        ("Heading2", 13, 19, purple, bold),
        ("BodyText", 10, 16, navy, regular),
        ("Small", 8, 12, muted, regular),
        ("Label", 8, 13, purple, bold),
    ]:
        style = ParagraphStyle(
            name,
            fontName=font,
            fontSize=size,
            leading=leading,
            textColor=color,
            spaceAfter=9,
        )
        if name in styles:
            styles.byName[name] = style
        else:
            styles.add(style)

    def text(value):
        return escape(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value))).replace(
            "\n", "<br/>"
        )

    def p(value, style="BodyText"):
        return Paragraph(text(value), styles[style])

    def joined(items):
        return (
            ", ".join(items) if items else "None identified from the current profile."
        )

    careers = report["recommendations"]
    target = next((c for c in careers if c["career"] == target_career), careers[0])
    name = profile.get("name") or "Your profile"
    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=(210 * mm, 297 * mm),
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=24 * mm,
        bottomMargin=20 * mm,
        title="CareerCast - Personalized Career Development Report",
        author="CareerCast",
    )

    def frame(canvas, document):
        canvas.setFillColor(purple)
        canvas.rect(0, 289 * mm, 210 * mm, 8 * mm, fill=1, stroke=0)
        canvas.setFont(bold, 9)
        canvas.setFillColor(navy)
        canvas.drawString(20 * mm, 280 * mm, "CAREERCAST  /  YOUR NEXT CHAPTER")
        canvas.setStrokeColor(colors.HexColor("#E6E1F0"))
        canvas.line(20 * mm, 16 * mm, 190 * mm, 16 * mm)
        canvas.setFont(regular, 8)
        canvas.setFillColor(muted)
        canvas.drawString(20 * mm, 11 * mm, "Private career development report")
        canvas.drawRightString(190 * mm, 11 * mm, f"Page {document.page}")

    story = [
        p("YOUR CAREER, WITH CLARITY", "Label"),
        p("Your career development report", "Title"),
        p(name, "Heading2"),
        p(profile.get("email") or "", "Small"),
        p(
            "Generated "
            + datetime.now().strftime("%d %B %Y")
            + " | Based on your saved profile and current model",
            "Small",
        ),
        Spacer(1, 6 * mm),
        p("Your focus: " + target["career"], "Heading1"),
        p(
            f"Core skill alignment: {target['alignment']}% | Model confidence: {target['confidence']}%"
        ),
        p(
            "Start with your existing strengths, then build evidence for the missing core skills below. Suggested activities are a learning plan, not a guarantee of employment."
        ),
        p("Strengths to build on", "Heading2"),
        p(joined(target["matched_skills"])),
        p("Skills to develop next", "Heading2"),
        p(joined(target["missing_skills"])),
        Spacer(1, 3 * mm),
        p("Your recommended careers", "Heading2"),
    ]
    rows = [[p("Career", "Label"), p("Alignment", "Label"), p("Confidence", "Label")]]
    rows += [
        [p(c["career"]), p(f"{c['alignment']}%"), p(f"{c['confidence']}%")]
        for c in careers
    ]
    table = Table(
        rows, colWidths=[100 * mm, 34 * mm, 36 * mm], repeatRows=1, hAlign="LEFT"
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), pale),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#EAE5F2")),
            ]
        )
    )
    story += [
        table,
        p(
            "Alignment uses a curated core-skill checklist. Confidence is an uncalibrated model probability, not your chance of getting a job.",
            "Small",
        ),
        PageBreak(),
        p("What to get good at", "Heading1"),
        p("A practical plan for " + target["career"], "Heading2"),
        p(
            "Work through these priorities in order. Move on when you can explain the concept, complete a practical exercise without copying, and show your work."
        ),
    ]
    if not target["missing_skills"]:
        story += [
            p("Your profile covers all listed core skills.", "Heading2"),
            p(
                "Deepen your knowledge through an end-to-end project, tests, documentation and a walkthrough. Ask a mentor to review your decisions and identify gaps beyond this checklist."
            ),
        ]
    for i, skill in enumerate(target["missing_skills"], 1):
        exercise = PRACTICE.get(
            skill.lower(),
            f'Learn the foundations of {skill}, complete a focused exercise, and apply it in a small project relevant to {target["career"]}. Explain your choices and request feedback.',
        )
        story.append(
            KeepTogether(
                [
                    p(f"{i:02d}  {skill.title()}", "Heading2"),
                    p(exercise),
                    p(
                        "Evidence to keep: a working example, notes on your decisions, and feedback or test results.",
                        "Small",
                    ),
                    Spacer(1, 3 * mm),
                ]
            )
        )
    story += [
        p("Turn practice into proof", "Heading2"),
        p(
            "Combine two or three of these skills in one portfolio project. Include a clear README, screenshots or results, reproducible steps, and a short account of what you learned. Update your profile only after you can demonstrate the new skill."
        ),
        PageBreak(),
        p("Explore your other options", "Heading1"),
    ]
    for c in careers:
        if c["career"] == target["career"]:
            continue
        story.append(
            KeepTogether(
                [
                    p(c["career"], "Heading2"),
                    p("Already aligned: " + joined(c["matched_skills"]), "Small"),
                    p("Develop next: " + joined(c["missing_skills"])),
                    Spacer(1, 2 * mm),
                ]
            )
        )
    story += [p("Make your resume support your goal", "Heading2")]
    tips = (
        resume.get("suggestions", [])
        if resume
        else [
            "Upload your resume in Resume Analyzer to get document-specific completeness feedback.",
            "Show relevant projects, measurable outcomes and links to work you can demonstrate.",
        ]
    )
    if not tips:
        tips = [
            "All structural completeness checks passed. Tailor your project and experience descriptions to your target career."
        ]
    story += [p("- " + tip) for tip in tips]
    story += [
        p("How to use this report", "Heading2"),
        p(
            "Choose a target career, practice its missing skills, build evidence, update your profile, then run a fresh analysis. These recommendations come from a small public first-job survey; they support exploration and need independent judgment.",
            "Small",
        ),
        p(
            "Model: "
            + report["model_version"]
            + " | Vocabulary coverage: "
            + str(report["coverage"])
            + "%. See Model Evaluation in the app for measured quality and limitations.",
            "Small",
        ),
    ]
    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    return output.getvalue()
