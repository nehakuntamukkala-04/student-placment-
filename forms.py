from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, SelectField,
    FloatField, IntegerField, TextAreaField, DateField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError
from models import User

DEPARTMENTS = [
    ('Computer Science', 'Computer Science & Engineering'),
    ('Information Technology', 'Information Technology'),
    ('Artificial Intelligence & DS', 'Artificial Intelligence & Data Science'),
    ('Electronics & Communication', 'Electronics & Communication Engineering'),
    ('Electrical & Electronics', 'Electrical & Electronics Engineering'),
    ('Mechanical Engineering', 'Mechanical Engineering')
]

YEARS = [
    ('1st Year', '1st Year'),
    ('2nd Year', '2nd Year'),
    ('3rd Year', '3rd Year'),
    ('4th Year', '4th Year')
]

CODING_PLATFORMS = [
    ('LeetCode', 'LeetCode'),
    ('HackerRank', 'HackerRank'),
    ('CodeChef', 'CodeChef'),
    ('Codeforces', 'Codeforces'),
    ('GeeksforGeeks', 'GeeksforGeeks'),
    ('Multiple', 'Multiple Platforms')
]

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=40)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Account Role', choices=[('student', 'Student'), ('admin', 'Placement Officer / Admin')], default='student')
    admin_secret_key = PasswordField('Admin Secret Key (Required only for Admin accounts)', validators=[Optional()])
    
    # Student-specific fields (optional on form, required if role=='student')
    roll_number = StringField('Roll Number', validators=[Optional(), Length(max=30)])
    department = SelectField('Department', choices=DEPARTMENTS, default='Computer Science')
    year = SelectField('Academic Year', choices=YEARS, default='4th Year')
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Create Account')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('Username is already taken. Please choose another.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError('Email is already registered. Please sign in or use another email.')


class StudentProfileForm(FlaskForm):
    # Academic & Personal
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = SelectField('Department', choices=DEPARTMENTS, validators=[DataRequired()])
    year = SelectField('Year of Study', choices=YEARS, validators=[DataRequired()])
    cgpa = FloatField('Current CGPA (0 - 10)', validators=[DataRequired(), NumberRange(min=0.0, max=10.0, message='CGPA must be between 0.0 and 10.0')])
    backlogs = IntegerField('Active Backlogs', validators=[DataRequired(), NumberRange(min=0, max=30, message='Backlogs cannot be negative')])
    tenth_percent = FloatField('10th Grade Marks (%)', validators=[DataRequired(), NumberRange(min=0.0, max=100.0)])
    twelfth_percent = FloatField('12th / Diploma Marks (%)', validators=[DataRequired(), NumberRange(min=0.0, max=100.0)])

    # Technical & Coding
    skills = StringField('Technical Skills (Comma separated tags, e.g. Python, SQL, DSA, React, Machine Learning)', validators=[Optional()])
    coding_problems_count = IntegerField('Coding Problems Solved', validators=[DataRequired(), NumberRange(min=0, max=5000)])
    coding_platform = SelectField('Primary Coding Platform', choices=CODING_PLATFORMS, default='LeetCode')

    # Projects & Experience
    projects_count = IntegerField('Projects Completed', validators=[DataRequired(), NumberRange(min=0, max=50)])
    project_links = TextAreaField('Project Links & Descriptions (GitHub repos, live demos)', validators=[Optional()])
    internships_count = IntegerField('Internships Completed', validators=[DataRequired(), NumberRange(min=0, max=20)])
    certifications_count = IntegerField('Certifications Earned', validators=[DataRequired(), NumberRange(min=0, max=30)])

    # Assessments
    communication_score = FloatField('Communication Skill Rating (1 - 10)', validators=[DataRequired(), NumberRange(min=1.0, max=10.0)])
    aptitude_score = FloatField('Aptitude Test Score (0 - 100)', validators=[DataRequired(), NumberRange(min=0.0, max=100.0)])
    mock_interview_score = FloatField('Mock Interview Score (0 - 100)', validators=[DataRequired(), NumberRange(min=0.0, max=100.0)])

    # Online Links & Resume
    github_url = StringField('GitHub Profile URL', validators=[Optional(), Length(max=255)])
    linkedin_url = StringField('LinkedIn Profile URL', validators=[Optional(), Length(max=255)])
    resume_file = FileField('Upload Resume (PDF, max 10MB)', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'PDF or Word documents only')])

    submit = SubmitField('Save Profile & Re-calculate Score')


class CompanyForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired(), Length(max=120)])
    industry = StringField('Industry / Sector', validators=[DataRequired(), Length(max=80)])
    role_offered = StringField('Role Offered', validators=[DataRequired(), Length(max=120)])
    package_lpa = FloatField('CTC Package (in LPA)', validators=[DataRequired(), NumberRange(min=1.0, max=150.0)])
    min_cgpa = FloatField('Minimum CGPA Cutoff', validators=[DataRequired(), NumberRange(min=0.0, max=10.0)])
    max_backlogs = IntegerField('Maximum Allowed Backlogs', validators=[DataRequired(), NumberRange(min=0, max=10)])
    required_skills = StringField('Required Skills (Comma separated, e.g. Python, SQL, DSA)', validators=[Optional()])
    location = StringField('Job Location', validators=[DataRequired(), Length(max=120)])
    website = StringField('Company Website', validators=[Optional(), Length(max=255)])
    description = TextAreaField('Role Description & Requirements', validators=[Optional()])
    submit = SubmitField('Save Company')


class PlacementDriveForm(FlaskForm):
    company_id = SelectField('Company', coerce=int, validators=[DataRequired()])
    title = StringField('Drive Title (e.g. Campus Recruitment 2026)', validators=[DataRequired(), Length(max=150)])
    drive_date = DateField('Drive Date', validators=[DataRequired()])
    registration_deadline = DateField('Registration Deadline', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Upcoming', 'Upcoming'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Upcoming')
    venue = StringField('Venue / Mode', validators=[DataRequired(), Length(max=120)])
    instructions = TextAreaField('Drive Instructions & Process Notes', validators=[Optional()])
    submit = SubmitField('Save Drive')
