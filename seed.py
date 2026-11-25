"""
seed.py – Populates the database with realistic demo data.
Run once: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, date, timedelta, timezone
import random
import json

from app import create_app
from models import db, User, StudentProfile, ScoreHistory, Company, PlacementDrive
from services.scoring import evaluate_student_readiness

app = create_app()

# ── seed constants ────────────────────────────────────────────────────────────
DEPARTMENTS = [
    'Computer Science',
    'Information Technology',
    'Artificial Intelligence & DS',
    'Electronics & Communication',
    'Electrical & Electronics',
    'Mechanical Engineering',
]
YEARS = ['1st Year', '2nd Year', '3rd Year', '4th Year']
PLATFORMS = ['LeetCode', 'HackerRank', 'CodeChef', 'Codeforces', 'GeeksforGeeks', 'Multiple']
ALL_SKILLS = [
    'Python', 'Java', 'C++', 'JavaScript', 'SQL', 'DSA',
    'Web Dev', 'React', 'Node.js', 'Machine Learning', 'Deep Learning',
    'Cloud Computing', 'AWS', 'Docker', 'Kubernetes', 'Git',
    'Data Analysis', 'Pandas', 'TensorFlow', 'REST APIs',
    'System Design', 'Linux', 'TypeScript', 'Spring Boot',
]

FIRST_NAMES = [
    'Aarav','Sai','Riya','Priya','Aditya','Sneha','Rahul','Deepika','Kiran','Arjun',
    'Meera','Vikram','Anjali','Nikhil','Pooja','Siddharth','Kavya','Rohit','Tanvi','Amit',
    'Nisha','Suresh','Divya','Rajesh','Swathi','Lokesh','Bhavana','Chetan','Harini','Arun',
    'Revathi','Mahesh','Sindhu','Vignesh','Bhavya','Surya','Lavanya','Pranav','Sowmya','Vinay',
    'Pavithra','Dinesh','Ramya','Ajay','Nandini','Suraj','Keerthi','Vishal','Shruthi','Girish',
]
LAST_NAMES = [
    'Kumar','Sharma','Reddy','Patel','Singh','Nair','Verma','Rao','Gupta','Joshi',
    'Pillai','Mehta','Iyer','Bhat','Murthy','Chandra','Das','Krishnan','Pandey','Sinha',
]

COMPANIES = [
    {
        'name': 'TCS',
        'industry': 'IT Services',
        'role_offered': 'Systems Engineer',
        'package_lpa': 7.0,
        'min_cgpa': 6.0,
        'max_backlogs': 0,
        'required_skills': ['Python', 'SQL', 'Java'],
        'location': 'Chennai / Hyderabad / Pune',
        'website': 'https://www.tcs.com',
        'description': 'Flagship IT service company hiring for large enterprise projects.'
    },
    {
        'name': 'Infosys',
        'industry': 'IT Services',
        'role_offered': 'Systems Engineer',
        'package_lpa': 6.5,
        'min_cgpa': 6.5,
        'max_backlogs': 0,
        'required_skills': ['Python', 'Java', 'SQL'],
        'location': 'Mysore / Bangalore',
        'website': 'https://www.infosys.com',
        'description': 'Digital transformation leader with structured training programs.'
    },
    {
        'name': 'Wipro',
        'industry': 'IT Services',
        'role_offered': 'Project Engineer',
        'package_lpa': 6.5,
        'min_cgpa': 6.0,
        'max_backlogs': 0,
        'required_skills': ['Java', 'SQL', 'DSA'],
        'location': 'Bangalore / Hyderabad',
        'website': 'https://www.wipro.com',
        'description': 'Full-stack delivery for global Fortune 500 clients.'
    },
    {
        'name': 'Cognizant',
        'industry': 'IT Services',
        'role_offered': 'Programmer Analyst',
        'package_lpa': 7.5,
        'min_cgpa': 6.5,
        'max_backlogs': 0,
        'required_skills': ['Python', 'Java', 'SQL', 'Web Dev'],
        'location': 'Chennai / Bangalore / Kolkata',
        'website': 'https://www.cognizant.com',
        'description': 'Digital engineering and cloud transformation services.'
    },
    {
        'name': 'Capgemini',
        'industry': 'IT Services',
        'role_offered': 'Analyst',
        'package_lpa': 7.0,
        'min_cgpa': 6.0,
        'max_backlogs': 0,
        'required_skills': ['Python', 'SQL', 'DSA'],
        'location': 'Mumbai / Pune / Bangalore',
        'website': 'https://www.capgemini.com',
        'description': 'European tech giant with strong consulting practice.'
    },
    {
        'name': 'Accenture',
        'industry': 'IT Consulting',
        'role_offered': 'Application Development Associate',
        'package_lpa': 8.0,
        'min_cgpa': 6.5,
        'max_backlogs': 0,
        'required_skills': ['Java', 'SQL', 'React', 'DSA'],
        'location': 'Hyderabad / Bangalore / Pune',
        'website': 'https://www.accenture.com',
        'description': 'Global consulting & IT strategy for 40+ industries.'
    },
    {
        'name': 'Amazon',
        'industry': 'Product / Cloud',
        'role_offered': 'SDE-1',
        'package_lpa': 32.0,
        'min_cgpa': 7.5,
        'max_backlogs': 0,
        'required_skills': ['DSA', 'Python', 'Java', 'System Design', 'SQL'],
        'location': 'Bangalore / Hyderabad / Chennai',
        'website': 'https://www.amazon.jobs',
        'description': 'Dream company for SDE roles. Requires strong DSA and OOPs fundamentals.'
    },
    {
        'name': 'Microsoft',
        'industry': 'Product / Cloud',
        'role_offered': 'Software Engineer',
        'package_lpa': 40.0,
        'min_cgpa': 8.0,
        'max_backlogs': 0,
        'required_skills': ['DSA', 'C++', 'Python', 'System Design', 'Git'],
        'location': 'Hyderabad / Bangalore (Remote Option)',
        'website': 'https://careers.microsoft.com',
        'description': 'Top-tier product company – 4 technical rounds including system design.'
    },
    {
        'name': 'Google',
        'industry': 'Product / Cloud',
        'role_offered': 'Software Engineer L3',
        'package_lpa': 55.0,
        'min_cgpa': 8.5,
        'max_backlogs': 0,
        'required_skills': ['DSA', 'Python', 'C++', 'System Design', 'Machine Learning'],
        'location': 'Bangalore / Hyderabad',
        'website': 'https://careers.google.com',
        'description': 'Ultra-competitive – requires top-tier competitive programming scores.'
    },
    {
        'name': 'Goldman Sachs',
        'industry': 'Financial Technology',
        'role_offered': 'Technology Analyst',
        'package_lpa': 20.0,
        'min_cgpa': 7.0,
        'max_backlogs': 0,
        'required_skills': ['DSA', 'Python', 'Java', 'SQL', 'Data Analysis'],
        'location': 'Bangalore / Mumbai',
        'website': 'https://www.goldmansachs.com/careers',
        'description': 'FinTech division focused on trading platforms and risk systems.'
    },
    {
        'name': 'Oracle',
        'industry': 'Product / Cloud',
        'role_offered': 'Applications Engineer',
        'package_lpa': 18.0,
        'min_cgpa': 7.0,
        'max_backlogs': 0,
        'required_skills': ['Java', 'SQL', 'DSA', 'Spring Boot'],
        'location': 'Bangalore / Hyderabad',
        'website': 'https://www.oracle.com/careers',
        'description': 'Enterprise cloud, DB and middleware engineering team.'
    },
    {
        'name': 'Zoho',
        'industry': 'SaaS Product',
        'role_offered': 'Member Technical Staff',
        'package_lpa': 10.0,
        'min_cgpa': 6.0,
        'max_backlogs': 0,
        'required_skills': ['Java', 'C++', 'DSA', 'SQL', 'Web Dev'],
        'location': 'Chennai / Coimbatore',
        'website': 'https://www.zoho.com/careers',
        'description': 'Indian SaaS giant with 100+ B2B products. Product engineering roles.'
    },
    {
        'name': 'Flipkart',
        'industry': 'E-Commerce / Product',
        'role_offered': 'SDE-1',
        'package_lpa': 28.0,
        'min_cgpa': 7.5,
        'max_backlogs': 0,
        'required_skills': ['DSA', 'Python', 'Java', 'System Design', 'REST APIs'],
        'location': 'Bangalore',
        'website': 'https://www.flipkartcareers.com',
        'description': 'Leading e-commerce platform. Strong focus on scalability problems.'
    },
]

DRIVE_TEMPLATES = [
    {'title': 'Campus Placement Drive 2026 – TCS', 'days_offset': 15},
    {'title': 'Infosys InfyTQ Super Coders 2026', 'days_offset': 22},
    {'title': 'Accenture ASE Campus 2026', 'days_offset': 30},
    {'title': 'Amazon SDE Hiring Challenge', 'days_offset': 45},
    {'title': 'Wipro WILP – Weekend Hiring', 'days_offset': 20},
    {'title': 'Zoho Developer – On-Campus 2026', 'days_offset': 35},
    {'title': 'Cognizant GenC Tech 2026', 'days_offset': 12},
    {'title': 'Flipkart SDE Scholarship Drive', 'days_offset': 60},
]


def make_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def make_roll(dept, idx):
    code = ''.join(c for c in dept if c.isupper())[:2] or dept[:2].upper()
    return f"2026{code}{idx:03d}"


def random_skills(n=None):
    n = n or random.randint(3, 8)
    return random.sample(ALL_SKILLS, min(n, len(ALL_SKILLS)))


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Tables created.")

        # ── Admin account ────────────────────────────────────────────────────
        admin = User(
            username='admin',
            email='admin@placement.edu',
            full_name='Dr. Placement Officer',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        print("✓ Admin account created  (username: admin / password: admin123)")

        # ── Demo student account ─────────────────────────────────────────────
        demo_user = User(
            username='student',
            email='student@placement.edu',
            full_name='Demo Student',
            role='student'
        )
        demo_user.set_password('student123')
        db.session.add(demo_user)
        db.session.flush()

        demo_profile = StudentProfile(
            user_id=demo_user.id,
            roll_number='2026CS001',
            department='Computer Science',
            year='4th Year',
            phone='9876543210',
            cgpa=8.4,
            backlogs=0,
            tenth_percent=92.0,
            twelfth_percent=88.0,
            skills=['Python', 'DSA', 'SQL', 'React', 'Machine Learning', 'Git'],
            coding_problems_count=215,
            coding_platform='LeetCode',
            projects_count=3,
            project_links='https://github.com/demo/projects, https://demo-app.vercel.app',
            internships_count=1,
            certifications_count=3,
            communication_score=8.0,
            aptitude_score=78.0,
            mock_interview_score=74.0,
            github_url='https://github.com/demostudent',
            linkedin_url='https://linkedin.com/in/demostudent'
        )
        result = evaluate_student_readiness(demo_profile)
        demo_profile.current_readiness_score = result['total_score']
        demo_profile.current_status = result['status']
        demo_profile.category_scores = result['categories']
        db.session.add(demo_profile)
        db.session.flush()
        _add_history(demo_profile, result)
        print(f"✓ Demo student created   (username: student / password: student123) | Score: {result['total_score']}")

        # ── 50 realistic students ────────────────────────────────────────────
        idx = 2  # start after demo student
        for dept in DEPARTMENTS:
            count = random.randint(8, 10)
            for i in range(count):
                # Vary profiles: some weak, some strong
                tier = random.choices(['high', 'mid', 'low'], weights=[30, 50, 20])[0]

                if tier == 'high':
                    cgpa = round(random.uniform(8.0, 9.5), 2)
                    backlogs = 0
                    problems = random.randint(200, 450)
                    projects = random.randint(2, 5)
                    internships = random.randint(1, 2)
                    certs = random.randint(2, 5)
                    comm = round(random.uniform(7.5, 10.0), 1)
                    apt = round(random.uniform(72.0, 95.0), 1)
                    mock = round(random.uniform(70.0, 92.0), 1)
                    n_skills = random.randint(6, 10)
                elif tier == 'mid':
                    cgpa = round(random.uniform(6.5, 8.0), 2)
                    backlogs = random.randint(0, 1)
                    problems = random.randint(60, 220)
                    projects = random.randint(1, 3)
                    internships = random.randint(0, 1)
                    certs = random.randint(1, 3)
                    comm = round(random.uniform(5.5, 8.0), 1)
                    apt = round(random.uniform(50.0, 80.0), 1)
                    mock = round(random.uniform(50.0, 75.0), 1)
                    n_skills = random.randint(3, 7)
                else:  # low
                    cgpa = round(random.uniform(5.0, 6.5), 2)
                    backlogs = random.randint(1, 4)
                    problems = random.randint(0, 60)
                    projects = random.randint(0, 2)
                    internships = 0
                    certs = random.randint(0, 2)
                    comm = round(random.uniform(3.0, 6.0), 1)
                    apt = round(random.uniform(25.0, 55.0), 1)
                    mock = round(random.uniform(25.0, 55.0), 1)
                    n_skills = random.randint(1, 4)

                name = make_name()
                uname = f"{''.join(name.lower().split())}{random.randint(10,99)}"
                email = f"{uname}@college.edu"
                year = random.choice(YEARS) if dept not in ['Mechanical Engineering', 'Electrical & Electronics'] else random.choice(['3rd Year', '4th Year'])

                user = User(
                    username=uname,
                    email=email,
                    full_name=name,
                    role='student'
                )
                user.set_password('student123')
                db.session.add(user)
                db.session.flush()

                roll = make_roll(dept, idx)
                idx += 1

                profile = StudentProfile(
                    user_id=user.id,
                    roll_number=roll,
                    department=dept,
                    year=year,
                    phone=f"9{random.randint(100000000,999999999)}",
                    cgpa=cgpa,
                    backlogs=backlogs,
                    tenth_percent=round(random.uniform(60.0, 97.0), 1),
                    twelfth_percent=round(random.uniform(55.0, 95.0), 1),
                    skills=random_skills(n_skills),
                    coding_problems_count=problems,
                    coding_platform=random.choice(PLATFORMS),
                    projects_count=projects,
                    project_links='https://github.com/sample/project' if projects > 0 else None,
                    internships_count=internships,
                    certifications_count=certs,
                    communication_score=comm,
                    aptitude_score=apt,
                    mock_interview_score=mock,
                    github_url=f'https://github.com/{uname}',
                    linkedin_url=f'https://linkedin.com/in/{uname}'
                )

                result = evaluate_student_readiness(profile)
                profile.current_readiness_score = result['total_score']
                profile.current_status = result['status']
                profile.category_scores = result['categories']
                db.session.add(profile)
                db.session.flush()
                _add_history(profile, result)

        db.session.commit()
        total = StudentProfile.query.count()
        print(f"✓ {total} student profiles seeded.")

        # ── Companies ────────────────────────────────────────────────────────
        for cdata in COMPANIES:
            c = Company(
                name=cdata['name'],
                industry=cdata['industry'],
                role_offered=cdata['role_offered'],
                package_lpa=cdata['package_lpa'],
                min_cgpa=cdata['min_cgpa'],
                max_backlogs=cdata['max_backlogs'],
                location=cdata['location'],
                website=cdata['website'],
                description=cdata['description']
            )
            c.required_skills = cdata['required_skills']
            db.session.add(c)
        db.session.commit()
        print(f"✓ {len(COMPANIES)} companies seeded.")

        # ── Drives ───────────────────────────────────────────────────────────
        companies = Company.query.all()
        today = date.today()
        for tmpl in DRIVE_TEMPLATES:
            company = next((c for c in companies if c.name in tmpl['title']), random.choice(companies))
            drive_date = today + timedelta(days=tmpl['days_offset'])
            reg_deadline = drive_date - timedelta(days=5)
            drive = PlacementDrive(
                company_id=company.id,
                title=tmpl['title'],
                drive_date=drive_date,
                registration_deadline=reg_deadline,
                status='Upcoming',
                venue='Campus Placement Cell – Seminar Hall A',
                instructions='Bring college ID, 2 passport photos, resume (10 copies), all original certificates.'
            )
            db.session.add(drive)

        # Also add 2 completed drives
        for i in range(2):
            company = random.choice(companies)
            past_date = today - timedelta(days=random.randint(10, 60))
            d = PlacementDrive(
                company_id=company.id,
                title=f'{company.name} Campus Drive – {today.year - 1}',
                drive_date=past_date,
                registration_deadline=past_date - timedelta(days=5),
                status='Completed',
                venue='Online – Virtual Hiring Portal',
                instructions='This drive has been completed successfully.'
            )
            db.session.add(d)

        db.session.commit()
        drive_count = PlacementDrive.query.count()
        print(f"✓ {drive_count} placement drives seeded.")
        print("\n🎉 Seed complete! Run:  python app.py")


def _add_history(profile, current_result):
    """Add 6 months of synthetic score history for realistic charts."""
    today = datetime.now(timezone.utc)
    final_score = current_result['total_score']
    cats = current_result['categories']

    for months_back in range(5, -1, -1):
        # Simulate gradual improvement (older = lower score by up to 25%)
        factor = 1.0 - (months_back * random.uniform(0.03, 0.055))
        factor = max(0.5, factor)

        h = ScoreHistory(
            student_id=profile.id,
            total_score=round(final_score * factor, 1),
            academic_score=round(cats['academics']['score'] * factor, 1),
            technical_score=round(cats['technical']['score'] * factor, 1),
            experience_score=round(cats['experience']['score'] * factor, 1),
            aptitude_score=round(cats['aptitude']['score'] * factor, 1),
            communication_score=round(cats['communication']['score'] * factor, 1),
            status=current_result['status'],
            recorded_at=today - timedelta(days=months_back * 30 + random.randint(0, 5))
        )
        db.session.add(h)


if __name__ == '__main__':
    seed()
