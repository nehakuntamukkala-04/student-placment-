"""
Reporting Service: Generates high-quality CSV and PDF exports for administrators.
"""
import io
import csv
from datetime import datetime, timezone

def generate_students_csv(students) -> io.BytesIO:
    """
    Generates an RFC 4180 compliant CSV stream containing complete student placement profiles.
    Tries pandas first, falls back gracefully to Python's built-in csv module.
    """
    rows = []
    headers = [
        'Roll Number', 'Full Name', 'Email', 'Department', 'Year', 'Phone',
        'CGPA', 'Active Backlogs', '10th %', '12th %',
        'Skills', 'Coding Problems Solved', 'Coding Platform',
        'Projects Count', 'Internships Count', 'Certifications Count',
        'Communication Score (1-10)', 'Aptitude Score (100)', 'Mock Interview Score (100)',
        'Readiness Score', 'Readiness Status', 'GitHub URL', 'LinkedIn URL', 'Resume Uploaded'
    ]

    for s in students:
        user = s.user
        rows.append({
            'Roll Number': s.roll_number,
            'Full Name': user.full_name if user else '',
            'Email': user.email if user else '',
            'Department': s.department,
            'Year': s.year,
            'Phone': s.phone or '',
            'CGPA': s.cgpa,
            'Active Backlogs': s.backlogs,
            '10th %': s.tenth_percent,
            '12th %': s.twelfth_percent,
            'Skills': '; '.join(s.skills) if s.skills else '',
            'Coding Problems Solved': s.coding_problems_count,
            'Coding Platform': s.coding_platform,
            'Projects Count': s.projects_count,
            'Internships Count': s.internships_count,
            'Certifications Count': s.certifications_count,
            'Communication Score (1-10)': s.communication_score,
            'Aptitude Score (100)': s.aptitude_score,
            'Mock Interview Score (100)': s.mock_interview_score,
            'Readiness Score': s.current_readiness_score,
            'Readiness Status': s.current_status,
            'GitHub URL': s.github_url or '',
            'LinkedIn URL': s.linkedin_url or '',
            'Resume Uploaded': 'Yes' if s.resume_filename else 'No'
        })

    # Try pandas if available, else csv
    try:
        import pandas as pd
        df = pd.DataFrame(rows, columns=headers)
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        return output
    except Exception:
        # Pure Python fallback
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        bytes_io = io.BytesIO(output.getvalue().encode('utf-8'))
        bytes_io.seek(0)
        return bytes_io


def generate_placement_pdf(stats: dict, top_students: list, dept_stats: list) -> io.BytesIO:
    """
    Generates a PDF executive placement readiness report using ReportLab.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Brand Colors
    PRIMARY = colors.HexColor('#4F46E5')      # Deep Indigo
    SECONDARY = colors.HexColor('#0F172A')    # Slate 900
    ACCENT = colors.HexColor('#14B8A6')       # Teal
    MUTED = colors.HexColor('#64748B')        # Slate 500
    LIGHT_BG = colors.HexColor('#F8FAFC')     # Slate 50
    BORDER = colors.HexColor('#E2E8F0')       # Slate 200

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=MUTED
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=SECONDARY
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=SECONDARY
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=SECONDARY
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    # 1. Header & Title
    story.append(Paragraph('STUDENT PLACEMENT READINESS DASHBOARD', title_style))
    story.append(Paragraph(
        f'Executive Analytics & Campus Placement Preparedness Audit | Generated on {datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")}',
        subtitle_style
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=4, spaceAfter=14))

    # 2. Executive KPI Highlights Grid
    kpi_data = [
        [
            Paragraph('<b>Total Students</b>', subtitle_style),
            Paragraph('<b>Average Readiness</b>', subtitle_style),
            Paragraph('<b>Placement Ready</b>', subtitle_style),
            Paragraph('<b>At-Risk Count</b>', subtitle_style)
        ],
        [
            Paragraph(f'<b><font size="16" color="#4F46E5">{stats.get("total_students", 0)}</font></b>', body_style),
            Paragraph(f'<b><font size="16" color="#10B981">{stats.get("avg_score", 0)}%</font></b>', body_style),
            Paragraph(f'<b><font size="16" color="#14B8A6">{stats.get("ready_count", 0)}</font></b> ({stats.get("ready_pct", 0)}%)', body_style),
            Paragraph(f'<b><font size="16" color="#EF4444">{stats.get("at_risk_count", 0)}</font></b> ({stats.get("at_risk_pct", 0)}%)', body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[135, 135, 135, 135])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 3. Department Performance Breakdown
    story.append(Paragraph('Department-wise Performance Breakdown', section_heading))
    dept_table_data = [[
        Paragraph('Department', table_header),
        Paragraph('Students', table_header),
        Paragraph('Avg CGPA', table_header),
        Paragraph('Avg Readiness', table_header),
        Paragraph('Ready Count', table_header),
        Paragraph('Readiness Rate', table_header)
    ]]

    for d in dept_stats:
        dept_table_data.append([
            Paragraph(d.get('name', ''), table_cell_bold),
            Paragraph(str(d.get('count', 0)), table_cell),
            Paragraph(f"{d.get('avg_cgpa', 0):.2f}", table_cell),
            Paragraph(f"{d.get('avg_score', 0):.1f}%", table_cell),
            Paragraph(str(d.get('ready_count', 0)), table_cell),
            Paragraph(f"{d.get('ready_rate', 0):.1f}%", table_cell)
        ])

    dept_table = Table(dept_table_data, colWidths=[170, 60, 70, 80, 75, 85])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(dept_table)
    story.append(Spacer(1, 14))

    # 4. Top Placement Ready Performers
    story.append(Paragraph('Top Placement Performers (Leaderboard Highlights)', section_heading))
    lead_table_data = [[
        Paragraph('Rank', table_header),
        Paragraph('Roll Number', table_header),
        Paragraph('Student Name', table_header),
        Paragraph('Department', table_header),
        Paragraph('CGPA', table_header),
        Paragraph('Problems', table_header),
        Paragraph('Score', table_header),
        Paragraph('Status', table_header)
    ]]

    for rank, s in enumerate(top_students[:10], start=1):
        lead_table_data.append([
            Paragraph(f'#{rank}', table_cell_bold),
            Paragraph(s.roll_number, table_cell),
            Paragraph(s.user.full_name if s.user else '', table_cell),
            Paragraph(s.department[:20], table_cell),
            Paragraph(f'{s.cgpa:.2f}', table_cell),
            Paragraph(str(s.coding_problems_count), table_cell),
            Paragraph(f'<b>{s.current_readiness_score:.1f}%</b>', table_cell_bold),
            Paragraph(s.current_status, table_cell)
        ])

    lead_table = Table(lead_table_data, colWidths=[40, 75, 110, 120, 45, 55, 50, 45])
    lead_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(lead_table)
    story.append(Spacer(1, 16))

    # 5. Methodology and Notes
    story.append(Paragraph('Methodology & Weightage Breakdown', section_heading))
    method_text = (
        'Readiness Score is computed via standardized multi-factor evaluation: '
        '<b>Academics & CGPA (20%)</b> [with active backlog penalties], '
        '<b>Technical Skills & Coding Practice (25%)</b> [LeetCode/HackerRank counts & skill tags], '
        '<b>Projects, Internships & Certifications (20%)</b> [live deployments & verified experience], '
        '<b>Aptitude & Quantitative Reasoning (15%)</b>, and '
        '<b>Communication & Mock Interview Performance (20%)</b>. '
        'Status benchmarks: Placement Ready (≥80%), Almost Ready (60-79%), Developing (40-59%), and Not Ready (&lt;40%).'
    )
    story.append(Paragraph(method_text, subtitle_style))

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer
