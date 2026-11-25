from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, StudentProfile, ScoreHistory
from forms import LoginForm, RegisterForm
from services.scoring import evaluate_student_readiness

auth_bp = Blueprint('auth', __name__)

ADMIN_SECRET_PASSCODE = 'ADMIN2026'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            flash('Access restricted to Placement Officers / Administrators.', 'warning')
            return redirect(url_for('student.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_student:
            flash('This section is tailored for students. Redirected to Admin Console.', 'info')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username_or_email.data.strip()
        password = form.password.data
        
        # Look up by email or username
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard' if current_user.is_student else 'admin.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        role = form.role.data

        # If admin role requested, verify secret passcode
        if role == 'admin':
            entered_secret = form.admin_secret_key.data
            if entered_secret != ADMIN_SECRET_PASSCODE:
                flash(f'Invalid Admin Secret Key. (Hint: Use "{ADMIN_SECRET_PASSCODE}" for evaluation)', 'danger')
                return render_template('auth/register.html', form=form)

        # Create user
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            role=role
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # get user.id

        # If student, initialize profile
        if role == 'student':
            roll = form.roll_number.data.strip() if form.roll_number.data else f'REG{user.id:04d}'
            # Check unique roll number
            existing_roll = StudentProfile.query.filter_by(roll_number=roll).first()
            if existing_roll:
                roll = f'{roll}_{user.id}'

            student = StudentProfile(
                user_id=user.id,
                roll_number=roll,
                department=form.department.data,
                year=form.year.data,
                phone=form.phone.data.strip() if form.phone.data else None,
                cgpa=7.5,
                backlogs=0,
                tenth_percent=85.0,
                twelfth_percent=80.0,
                skills=['Python', 'SQL', 'DSA'],
                coding_problems_count=30,
                coding_platform='LeetCode',
                projects_count=1,
                project_links='https://github.com/example/sample-project',
                internships_count=0,
                certifications_count=1,
                communication_score=6.5,
                aptitude_score=65.0,
                mock_interview_score=60.0
            )

            # Compute initial score
            eval_res = evaluate_student_readiness(student)
            student.current_readiness_score = eval_res['total_score']
            student.current_status = eval_res['status']
            student.category_scores = eval_res['categories']
            
            db.session.add(student)
            db.session.flush()

            # Record initial score in history
            history = ScoreHistory(
                student_id=student.id,
                total_score=eval_res['total_score'],
                academic_score=eval_res['categories']['academics']['score'],
                technical_score=eval_res['categories']['technical']['score'],
                experience_score=eval_res['categories']['experience']['score'],
                aptitude_score=eval_res['categories']['aptitude']['score'],
                communication_score=eval_res['categories']['communication']['score'],
                status=eval_res['status']
            )
            db.session.add(history)

        db.session.commit()
        flash('Account created successfully! Please sign in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, admin_passcode=ADMIN_SECRET_PASSCODE)


@auth_bp.route('/logout')
@login_required
def logout():
    name = current_user.full_name
    logout_user()
    flash(f'Goodbye {name}, you have been safely logged out.', 'info')
    return redirect(url_for('auth.login'))
