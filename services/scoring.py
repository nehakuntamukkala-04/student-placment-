"""
Placement Readiness Scoring Engine
Calculates category breakdowns and the overall weighted Placement Readiness Score (0-100).
"""

def calculate_academic_score(cgpa: float, backlogs: int, tenth: float, twelfth: float) -> float:
    """Academics subscore out of 100 (Weight: 20%)."""
    # 70% CGPA, 15% 10th percentage, 15% 12th percentage
    cgpa_clamped = max(0.0, min(10.0, float(cgpa or 0.0)))
    tenth_clamped = max(0.0, min(100.0, float(tenth or 0.0)))
    twelfth_clamped = max(0.0, min(100.0, float(twelfth or 0.0)))
    
    base = (cgpa_clamped / 10.0) * 70.0 + (tenth_clamped / 100.0) * 15.0 + (twelfth_clamped / 100.0) * 15.0
    
    # Backlog penalty: 15 points per active backlog
    penalty = max(0, int(backlogs or 0)) * 15.0
    return round(max(0.0, min(100.0, base - penalty)), 1)


def calculate_technical_score(skills: list, coding_problems: int, coding_platform: str) -> float:
    """Technical skills & coding practice subscore out of 100 (Weight: 25%)."""
    # Skills contribution: up to 50 points (each valid skill worth ~7 points, max 7 skills for full points)
    skills_count = len(skills) if isinstance(skills, list) else 0
    skills_points = min(50.0, skills_count * 7.5)
    
    # Coding problems contribution: up to 42 points
    # 0 = 0 pts; 100 problems ~ 20 pts; 250 problems ~ 35 pts; 350+ problems = 42 pts
    problems = max(0, int(coding_problems or 0))
    problems_points = min(42.0, (problems / 350.0) * 42.0)
    
    # Platform bonus: 8 points if platform specified
    platform_bonus = 8.0 if coding_platform and len(coding_platform.strip()) > 0 else 0.0
    
    total = skills_points + problems_points + platform_bonus
    return round(max(0.0, min(100.0, total)), 1)


def calculate_experience_score(projects_count: int, project_links: str, internships_count: int, certifications_count: int) -> float:
    """Projects, internships, certifications subscore out of 100 (Weight: 20%)."""
    # Projects: up to 35 points (12 points per project up to 3)
    p_count = max(0, int(projects_count or 0))
    proj_points = min(35.0, p_count * 12.0)
    
    # Project links bonus: up to 10 points for live repo/demo
    link_bonus = 10.0 if project_links and len(project_links.strip()) > 5 else 0.0
    
    # Internships: up to 40 points (20 points per internship, up to 2)
    i_count = max(0, int(internships_count or 0))
    intern_points = min(40.0, i_count * 20.0)
    
    # Certifications: up to 15 points (5 points each, up to 3)
    c_count = max(0, int(certifications_count or 0))
    cert_points = min(15.0, c_count * 5.0)
    
    total = proj_points + link_bonus + intern_points + cert_points
    return round(max(0.0, min(100.0, total)), 1)


def calculate_aptitude_score(aptitude_raw: float) -> float:
    """Aptitude score out of 100 (Weight: 15%)."""
    return round(max(0.0, min(100.0, float(aptitude_raw or 0.0))), 1)


def calculate_communication_score(comm_rating: float, mock_interview: float) -> float:
    """Communication & mock interview subscore out of 100 (Weight: 20%)."""
    # comm_rating is 1-10 -> scaled to 100
    comm = max(1.0, min(10.0, float(comm_rating or 5.0))) * 10.0
    mock = max(0.0, min(100.0, float(mock_interview or 0.0)))
    
    # 40% communication rating + 60% mock interview score
    total = (comm * 0.40) + (mock * 0.60)
    return round(max(0.0, min(100.0, total)), 1)


def determine_status(total_score: float) -> tuple[str, str, str]:
    """
    Returns (status_label, badge_class, color_hex) based on overall score.
    - Not Ready (<40)
    - Developing (40-59)
    - Almost Ready (60-79)
    - Placement Ready (80+)
    """
    if total_score >= 80.0:
        return 'Placement Ready', 'status-ready', '#10B981'
    elif total_score >= 60.0:
        return 'Almost Ready', 'status-almost', '#3B82F6'
    elif total_score >= 40.0:
        return 'Developing', 'status-developing', '#F59E0B'
    else:
        return 'Not Ready', 'status-not-ready', '#EF4444'


def evaluate_student_readiness(student) -> dict:
    """
    Full readiness evaluation for a StudentProfile instance or dict.
    Returns dictionary with breakdown, overall score, weights, and status.
    """
    if hasattr(student, 'cgpa'):
        cgpa = student.cgpa
        backlogs = student.backlogs
        tenth = student.tenth_percent
        twelfth = student.twelfth_percent
        skills = student.skills
        coding_problems = student.coding_problems_count
        coding_platform = student.coding_platform
        projects_count = student.projects_count
        project_links = student.project_links
        internships_count = student.internships_count
        certifications_count = student.certifications_count
        comm_rating = student.communication_score
        aptitude_raw = student.aptitude_score
        mock_interview = student.mock_interview_score
    else:
        cgpa = student.get('cgpa', 7.0)
        backlogs = student.get('backlogs', 0)
        tenth = student.get('tenth_percent', 80.0)
        twelfth = student.get('twelfth_percent', 75.0)
        skills = student.get('skills', [])
        coding_problems = student.get('coding_problems_count', 0)
        coding_platform = student.get('coding_platform', 'LeetCode')
        projects_count = student.get('projects_count', 0)
        project_links = student.get('project_links', '')
        internships_count = student.get('internships_count', 0)
        certifications_count = student.get('certifications_count', 0)
        comm_rating = student.get('communication_score', 6.0)
        aptitude_raw = student.get('aptitude_score', 60.0)
        mock_interview = student.get('mock_interview_score', 60.0)

    acad_score = calculate_academic_score(cgpa, backlogs, tenth, twelfth)
    tech_score = calculate_technical_score(skills, coding_problems, coding_platform)
    exp_score = calculate_experience_score(projects_count, project_links, internships_count, certifications_count)
    apt_score = calculate_aptitude_score(aptitude_raw)
    comm_score = calculate_communication_score(comm_rating, mock_interview)

    # Weighted calculation
    # Academics: 20%, Technical: 25%, Experience: 20%, Aptitude: 15%, Communication: 20%
    weights = {
        'academics': 0.20,
        'technical': 0.25,
        'experience': 0.20,
        'aptitude': 0.15,
        'communication': 0.20
    }

    weighted_total = (
        (acad_score * weights['academics']) +
        (tech_score * weights['technical']) +
        (exp_score * weights['experience']) +
        (apt_score * weights['aptitude']) +
        (comm_score * weights['communication'])
    )
    total_score = round(max(0.0, min(100.0, weighted_total)), 1)
    status_label, badge_class, color_hex = determine_status(total_score)

    return {
        'total_score': total_score,
        'status': status_label,
        'badge_class': badge_class,
        'color': color_hex,
        'categories': {
            'academics': {
                'score': acad_score,
                'weight': 20,
                'weighted_points': round(acad_score * 0.20, 1),
                'label': 'Academics & Eligibility'
            },
            'technical': {
                'score': tech_score,
                'weight': 25,
                'weighted_points': round(tech_score * 0.25, 1),
                'label': 'Technical & Coding'
            },
            'experience': {
                'score': exp_score,
                'weight': 20,
                'weighted_points': round(exp_score * 0.20, 1),
                'label': 'Projects & Experience'
            },
            'aptitude': {
                'score': apt_score,
                'weight': 15,
                'weighted_points': round(apt_score * 0.15, 1),
                'label': 'Aptitude & Reasoning'
            },
            'communication': {
                'score': comm_score,
                'weight': 20,
                'weighted_points': round(comm_score * 0.20, 1),
                'label': 'Communication & Interview'
            }
        }
    }
