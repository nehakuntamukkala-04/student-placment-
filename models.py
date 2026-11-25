import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    full_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # One-to-one relationship with StudentProfile
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Academic & Basic Information
    roll_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    department = db.Column(db.String(80), nullable=False, default='Computer Science')
    year = db.Column(db.String(20), nullable=False, default='4th Year')
    phone = db.Column(db.String(20), nullable=True)
    cgpa = db.Column(db.Float, nullable=False, default=7.5)
    backlogs = db.Column(db.Integer, nullable=False, default=0)
    tenth_percent = db.Column(db.Float, nullable=False, default=85.0)
    twelfth_percent = db.Column(db.Float, nullable=False, default=80.0)

    # Technical & Coding
    skills_json = db.Column(db.Text, nullable=False, default='[]')  # JSON array of strings
    coding_problems_count = db.Column(db.Integer, nullable=False, default=0)
    coding_platform = db.Column(db.String(80), nullable=False, default='LeetCode')

    # Projects, Internships, Certifications
    projects_count = db.Column(db.Integer, nullable=False, default=0)
    project_links = db.Column(db.Text, nullable=True)
    internships_count = db.Column(db.Integer, nullable=False, default=0)
    certifications_count = db.Column(db.Integer, nullable=False, default=0)

    # Assessments & Interviews
    communication_score = db.Column(db.Float, nullable=False, default=6.0)  # 1-10
    aptitude_score = db.Column(db.Float, nullable=False, default=60.0)       # 0-100
    mock_interview_score = db.Column(db.Float, nullable=False, default=60.0)  # 0-100

    # Links & Uploads
    resume_filename = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)

    # Computed Readiness
    current_readiness_score = db.Column(db.Float, nullable=False, default=0.0)
    current_status = db.Column(db.String(30), nullable=False, default='Developing')
    category_scores_json = db.Column(db.Text, nullable=True, default='{}')

    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    score_history = db.relationship('ScoreHistory', backref='student', cascade='all, delete-orphan', lazy=True, order_by='ScoreHistory.recorded_at')
    applications = db.relationship('DriveApplication', backref='student', cascade='all, delete-orphan', lazy=True)

    @property
    def skills(self):
        try:
            return json.loads(self.skills_json) if self.skills_json else []
        except Exception:
            return [s.strip() for s in self.skills_json.split(',') if s.strip()]

    @skills.setter
    def skills(self, skills_list):
        if isinstance(skills_list, list):
            self.skills_json = json.dumps(skills_list)
        elif isinstance(skills_list, str):
            clean = [s.strip() for s in skills_list.split(',') if s.strip()]
            self.skills_json = json.dumps(clean)

    @property
    def category_scores(self):
        try:
            return json.loads(self.category_scores_json) if self.category_scores_json else {}
        except Exception:
            return {}

    @category_scores.setter
    def category_scores(self, scores_dict):
        self.category_scores_json = json.dumps(scores_dict)

    def __repr__(self):
        return f'<StudentProfile {self.roll_number} - Score: {self.current_readiness_score}>'


class ScoreHistory(db.Model):
    __tablename__ = 'score_histories'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    total_score = db.Column(db.Float, nullable=False)
    academic_score = db.Column(db.Float, nullable=False)
    technical_score = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, nullable=False)
    aptitude_score = db.Column(db.Float, nullable=False)
    communication_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Developing')
    recorded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'total_score': round(self.total_score, 1),
            'academic_score': round(self.academic_score, 1),
            'technical_score': round(self.technical_score, 1),
            'experience_score': round(self.experience_score, 1),
            'aptitude_score': round(self.aptitude_score, 1),
            'communication_score': round(self.communication_score, 1),
            'status': self.status,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d %H:%M') if self.recorded_at else ''
        }


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    industry = db.Column(db.String(80), nullable=False, default='Information Technology')
    role_offered = db.Column(db.String(120), nullable=False)
    package_lpa = db.Column(db.Float, nullable=False)  # in LPA, e.g. 14.5
    min_cgpa = db.Column(db.Float, nullable=False, default=6.5)
    max_backlogs = db.Column(db.Integer, nullable=False, default=0)
    required_skills_json = db.Column(db.Text, nullable=False, default='[]')
    location = db.Column(db.String(120), nullable=False, default='Bangalore / Remote')
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    drives = db.relationship('PlacementDrive', backref='company', cascade='all, delete-orphan', lazy=True)

    @property
    def required_skills(self):
        try:
            return json.loads(self.required_skills_json) if self.required_skills_json else []
        except Exception:
            return [s.strip() for s in self.required_skills_json.split(',') if s.strip()]

    @required_skills.setter
    def required_skills(self, skills_list):
        if isinstance(skills_list, list):
            self.required_skills_json = json.dumps(skills_list)
        elif isinstance(skills_list, str):
            clean = [s.strip() for s in skills_list.split(',') if s.strip()]
            self.required_skills_json = json.dumps(clean)

    def check_eligibility(self, student):
        """Returns tuple (is_eligible, reasons_dict)"""
        reasons = []
        eligible = True

        if student.cgpa < self.min_cgpa:
            eligible = False
            reasons.append(f'CGPA {student.cgpa} is below minimum requirement of {self.min_cgpa}')

        if student.backlogs > self.max_backlogs:
            eligible = False
            reasons.append(f'Active backlogs ({student.backlogs}) exceeds maximum allowed ({self.max_backlogs})')

        student_skills = [s.lower() for s in student.skills]
        req_skills = self.required_skills
        matched_skills = [s for s in req_skills if s.lower() in student_skills]
        missing_skills = [s for s in req_skills if s.lower() not in student_skills]

        # Require at least 50% match of core skills if skills specified
        if req_skills:
            match_pct = (len(matched_skills) / len(req_skills)) * 100
            if match_pct < 40:
                eligible = False
                reasons.append(f'Missing essential skills: {", ".join(missing_skills[:3])}')

        return eligible, {
            'is_eligible': eligible,
            'cgpa_ok': student.cgpa >= self.min_cgpa,
            'backlogs_ok': student.backlogs <= self.max_backlogs,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'reasons': reasons
        }

    def __repr__(self):
        return f'<Company {self.name} - {self.package_lpa} LPA>'


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    drive_date = db.Column(db.Date, nullable=False)
    registration_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Upcoming')  # 'Upcoming', 'Ongoing', 'Completed'
    venue = db.Column(db.String(120), nullable=False, default='Campus Placement Cell')
    instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship('DriveApplication', backref='drive', cascade='all, delete-orphan', lazy=True)

    def is_registration_open(self):
        today = datetime.now(timezone.utc).date()
        return self.registration_deadline >= today and self.status == 'Upcoming'

    def __repr__(self):
        return f'<PlacementDrive {self.title} on {self.drive_date}>'


class DriveApplication(db.Model):
    __tablename__ = 'drive_applications'

    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(30), nullable=False, default='Applied')  # 'Applied', 'Shortlisted', 'Interviewing', 'Selected', 'Rejected'
    remarks = db.Column(db.String(255), nullable=True)

    __table_args__ = (db.UniqueConstraint('drive_id', 'student_id', name='unique_student_drive_app'),)

    def __repr__(self):
        return f'<DriveApplication drive={self.drive_id} student={self.student_id}>'
