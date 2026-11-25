"""
Personalized Recommendations Engine
Generates targeted, actionable advice based on student profile gaps and scoring breakdown.
"""

def generate_recommendations(student, breakdown: dict = None) -> list[dict]:
    """
    Analyzes student strengths and weak spots to return prioritized recommendation cards.
    Each item contains:
    - id: str
    - title: str
    - category: str (academics, technical, experience, aptitude, communication)
    - priority: str ('high', 'medium', 'low')
    - priority_badge: str
    - impact: str (e.g. '+8 pts')
    - description: str
    - action_label: str
    - action_url: str
    - icon: str (Lucide / Bootstrap icon name)
    """
    recommendations = []
    
    # 1. Backlogs (Critical)
    if student.backlogs > 0:
        recommendations.append({
            'id': 'clear-backlogs',
            'title': f'Clear {student.backlogs} Pending Backlog{"s" if student.backlogs > 1 else ""}',
            'category': 'Academics',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': f'+{student.backlogs * 15} pts',
            'description': 'Over 85% of tier-1 recruiters enforce a strict 0-backlog policy. Clearing pending papers is your fastest route to eligibility.',
            'action_label': 'Consult Academic Cell',
            'action_url': '#',
            'icon': 'exclamation-triangle-fill'
        })
    
    # 2. CGPA improvement
    if student.cgpa < 7.0:
        recommendations.append({
            'id': 'boost-cgpa',
            'title': 'Aim for Minimum 7.0 CGPA Cutoff',
            'category': 'Academics',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': '+6 to +12 pts',
            'description': f'Your current CGPA is {student.cgpa}. Pushing above 7.0 or 7.5 unlocks over 60% more on-campus placement opportunities.',
            'action_label': 'View Syllabus & Grades',
            'action_url': '#',
            'icon': 'mortarboard-fill'
        })
    elif student.cgpa < 8.0:
        recommendations.append({
            'id': 'boost-cgpa-target',
            'title': 'Target 8.0+ CGPA for Product Companies',
            'category': 'Academics',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+4 to +7 pts',
            'description': 'Targeting 8.0+ CGPA qualifies you for premier dream-tier companies (Microsoft, Amazon, Cisco, Qualcomm).',
            'action_label': 'Track Sem Exam Goals',
            'action_url': '#',
            'icon': 'award-fill'
        })

    # 3. Coding Practice & DSA
    problems = student.coding_problems_count or 0
    if problems < 50:
        recommendations.append({
            'id': 'dsa-kickstart',
            'title': 'Solve 50+ DSA Problems on LeetCode / HackerRank',
            'category': 'Technical',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': '+10 to +15 pts',
            'description': f'You have logged {problems} solved problems. Product companies assess Data Structures (Arrays, Strings, HashMaps, Trees) in initial coding rounds.',
            'action_label': 'Start Striver SDE Sheet',
            'action_url': 'https://leetcode.com',
            'icon': 'code-slash'
        })
    elif problems < 150:
        recommendations.append({
            'id': 'dsa-intermediate',
            'title': f'Level up to 200+ Solved Problems (Current: {problems})',
            'category': 'Technical',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+8 to +12 pts',
            'description': 'Focus on Medium-difficulty Dynamic Programming, Graphs, and Greedy patterns to pass online assessments consistently.',
            'action_label': 'Practice Daily LeetCode',
            'action_url': 'https://leetcode.com',
            'icon': 'terminal'
        })
    elif problems < 300:
        recommendations.append({
            'id': 'dsa-advanced',
            'title': 'Sharpen Speed with Weekly Timed Contests',
            'category': 'Technical',
            'priority': 'low',
            'priority_badge': 'badge-info',
            'impact': '+4 to +6 pts',
            'description': 'Great coding consistency! Participate in LeetCode Biweekly and Codeforces contests to build speed under time pressure.',
            'action_label': 'View Contest Schedule',
            'action_url': 'https://leetcode.com/contest',
            'icon': 'trophy-fill'
        })

    # 4. Technical Skills Gaps
    student_skills = [s.lower() for s in student.skills]
    has_dsa = any('dsa' in s or 'data structures' in s for s in student_skills)
    has_sql = any('sql' in s or 'database' in s or 'mysql' in s or 'postgres' in s for s in student_skills)
    has_git = any('git' in s or 'version control' in s for s in student_skills)

    if not has_dsa:
        recommendations.append({
            'id': 'add-dsa-skill',
            'title': 'Add Data Structures & Algorithms to Profile',
            'category': 'Technical',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': '+5 pts',
            'description': 'DSA is mandatory for technical interviews across all software engineering roles.',
            'action_label': 'Update Skills',
            'action_url': '/profile',
            'icon': 'diagram-3-fill'
        })
    if not has_sql:
        recommendations.append({
            'id': 'learn-sql',
            'title': 'Master SQL Queries and Relational DB Basics',
            'category': 'Technical',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+4 to +6 pts',
            'description': 'Database queries (JOINs, GROUP BY, Indexing) appear in almost 90% of technical and system design rounds.',
            'action_label': 'Explore SQL Exercises',
            'action_url': 'https://sqlzoo.net',
            'icon': 'database-fill'
        })
    if not has_git:
        recommendations.append({
            'id': 'learn-git',
            'title': 'Learn Git & GitHub Collaboration Workflows',
            'category': 'Technical',
            'priority': 'low',
            'priority_badge': 'badge-info',
            'impact': '+3 pts',
            'description': 'Recruiters check your GitHub commit streak and ability to use Git branches and pull requests.',
            'action_label': 'Upload GitHub Profile',
            'action_url': '/profile',
            'icon': 'github'
        })

    # 5. Projects & Links
    if student.projects_count < 2:
        recommendations.append({
            'id': 'build-capstone',
            'title': 'Build at least 2 Production-Grade Projects',
            'category': 'Experience',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': '+10 to +15 pts',
            'description': 'Develop a full-stack web or AI application with live deployment (Vercel, Render) and well-documented README.',
            'action_label': 'Browse Project Ideas',
            'action_url': 'https://github.com',
            'icon': 'folder-fill'
        })
    elif not student.project_links or len(student.project_links.strip()) < 5:
        recommendations.append({
            'id': 'add-project-links',
            'title': 'Add Live Demo & GitHub Links to Your Projects',
            'category': 'Experience',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+5 pts',
            'description': 'Interviewers value clickable live demo links and clean GitHub repositories with tests and documentation.',
            'action_label': 'Update Links',
            'action_url': '/profile',
            'icon': 'link-45deg'
        })

    # 6. Internships & Certifications
    if student.internships_count == 0:
        recommendations.append({
            'id': 'secure-internship',
            'title': 'Target a Summer / Winter Internship or Open Source',
            'category': 'Experience',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+12 to +20 pts',
            'description': 'Prior industrial or open-source experience directly sets you apart during resume shortlisting.',
            'action_label': 'Explore Opportunities',
            'action_url': '/drives',
            'icon': 'briefcase-fill'
        })

    # 7. Aptitude
    if student.aptitude_score < 60:
        recommendations.append({
            'id': 'practice-aptitude',
            'title': 'Boost Aptitude Test Score Above 70%',
            'category': 'Aptitude',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': '+8 to +12 pts',
            'description': f'Your current aptitude score is {student.aptitude_score}%. Daily practice in Quant (Time & Work, Speed, P&C) and Logical Reasoning ensures clearing Day-1 screening.',
            'action_label': 'Take Mock Aptitude Test',
            'action_url': '#',
            'icon': 'calculator-fill'
        })
    elif student.aptitude_score < 75:
        recommendations.append({
            'id': 'speed-aptitude',
            'title': 'Refine Verbal & Data Interpretation Speed',
            'category': 'Aptitude',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+4 to +6 pts',
            'description': 'Focus on accuracy under tight sectional time limits for TCS NQT, Capgemini, and Infosys assessments.',
            'action_label': 'Practice Timed Sets',
            'action_url': '#',
            'icon': 'stopwatch-fill'
        })

    # 8. Communication & Mock Interviews
    if student.mock_interview_score < 65:
        recommendations.append({
            'id': 'schedule-mock-interview',
            'title': 'Complete 2 Structured Mock Technical Interviews',
            'category': 'Communication',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': '+10 to +15 pts',
            'description': f'Mock interview score is currently {student.mock_interview_score}%. Practice explaining code complexity aloud and articulating architectural trade-offs.',
            'action_label': 'Book Peer Mock',
            'action_url': '#',
            'icon': 'people-fill'
        })
    elif student.communication_score < 7.0:
        recommendations.append({
            'id': 'improve-soft-skills',
            'title': 'Polish Behavioral Answers (STAR Methodology)',
            'category': 'Communication',
            'priority': 'medium',
            'priority_badge': 'badge-warning',
            'impact': '+5 to +8 pts',
            'description': 'Prepare concise stories for common HR questions: handling conflict, overcoming failures, and leadership scenarios.',
            'action_label': 'Review STAR Guide',
            'action_url': '#',
            'icon': 'chat-quote-fill'
        })

    # 9. Resume & Profiles
    if not student.resume_filename:
        recommendations.append({
            'id': 'upload-resume',
            'title': 'Upload Your ATS-Formatted Resume (PDF)',
            'category': 'Experience',
            'priority': 'high',
            'priority_badge': 'badge-danger',
            'impact': 'Direct Placement Eligibility',
            'description': 'You have not uploaded a resume yet. Placement cell requires a single-page PDF with clear quantifiable achievements.',
            'action_label': 'Upload Resume Now',
            'action_url': '/profile',
            'icon': 'file-earmark-pdf-fill'
        })

    # Sort recommendations by priority (high first, then medium, then low)
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda r: priority_order.get(r['priority'], 3))

    return recommendations[:6]  # Return top 6 actionable items
