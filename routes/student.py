"""
routes/student.py – All student-facing views.
Blueprint prefix: /student
"""
import os
import uuid
from datetime import datetime, timezone

from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app, send_from_directory, abort)
from flask_login import login_required, current_user

from models import db, StudentProfile, ScoreHistory, Company, PlacementDrive, DriveApplication
from forms import StudentProfileForm
from services.scoring import evaluate_student_readiness
from services.recommendations import generate_recommendations
from routes.auth import student_required

student_bp = Blueprint('student', __name__)


# ---------------------------------------------------------------------------
# Helper: re-calculate and persist readiness score
# ---------------------------------------------------------------------------
def _refresh_score(student: StudentProfile):
    result = evaluate_student_readiness(student)
    student.current_readiness_score = result['total_score']
    student.current_status = result['status']
    student.category_scores = result['categories']

    history = ScoreHistory(
        student_id=student.id,
        total_score=result['total_score'],
        academic_score=result['categories']['academics']['score'],
        technical_score=result['categories']['technical']['score'],
        experience_score=result['categories']['experience']['score'],
        aptitude_score=result['categories']['aptitude']['score'],
        communication_score=result['categories']['communication']['score'],
        status=result['status']
    )
    db.session.add(history)
    return result


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = current_user.student_profile
    if not student:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student.edit_profile'))

    result = evaluate_student_readiness(student)
    recommendations = generate_recommendations(student, result)

    # Companies the student qualifies for
    all_companies = Company.query.all()
    eligible_companies = []
    for company in all_companies:
        is_eligible, details = company.check_eligibility(student)
        if is_eligible:
            eligible_companies.append({'company': company, 'details': details})

    # Upcoming drives
    today = datetime.now(timezone.utc).date()
    upcoming_drives = (PlacementDrive.query
                       .filter(PlacementDrive.drive_date >= today,
                               PlacementDrive.status == 'Upcoming')
                       .order_by(PlacementDrive.drive_date)
                       .limit(5)
                       .all())

    # Score history (last 10 entries for sparkline)
    history = (ScoreHistory.query
               .filter_by(student_id=student.id)
               .order_by(ScoreHistory.recorded_at.desc())
               .limit(10)
               .all())
    history_asc = list(reversed(history))

    # Dept average score
    dept_students = (StudentProfile.query
                     .filter_by(department=student.department)
                     .all())
    dept_avg = (sum(s.current_readiness_score for s in dept_students) /
                len(dept_students)) if dept_students else 0.0

    return render_template(
        'student/dashboard.html',
        student=student,
        result=result,
        recommendations=recommendations,
        eligible_companies=eligible_companies[:6],
        upcoming_drives=upcoming_drives,
        history=history_asc,
        dept_avg=round(dept_avg, 1),
        today=today
    )


# ---------------------------------------------------------------------------
# Profile edit
# ---------------------------------------------------------------------------
@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def edit_profile():
    student = current_user.student_profile
    if not student:
        # Create a minimal profile if somehow missing
        student = StudentProfile(
            user_id=current_user.id,
            roll_number=f'REG{current_user.id:04d}',
            department='Computer Science',
            year='4th Year',
            skills_json='[]'
        )
        db.session.add(student)
        db.session.flush()

    form = StudentProfileForm(obj=None)

    if request.method == 'GET':
        # Pre-populate form
        form.full_name.data = current_user.full_name
        form.phone.data = student.phone
        form.department.data = student.department
        form.year.data = student.year
        form.cgpa.data = student.cgpa
        form.backlogs.data = student.backlogs
        form.tenth_percent.data = student.tenth_percent
        form.twelfth_percent.data = student.twelfth_percent
        form.skills.data = ', '.join(student.skills)
        form.coding_problems_count.data = student.coding_problems_count
        form.coding_platform.data = student.coding_platform
        form.projects_count.data = student.projects_count
        form.project_links.data = student.project_links
        form.internships_count.data = student.internships_count
        form.certifications_count.data = student.certifications_count
        form.communication_score.data = student.communication_score
        form.aptitude_score.data = student.aptitude_score
        form.mock_interview_score.data = student.mock_interview_score
        form.github_url.data = student.github_url
        form.linkedin_url.data = student.linkedin_url

    if form.validate_on_submit():
        # Update user full name
        current_user.full_name = form.full_name.data.strip()

        # Update profile fields
        student.phone = form.phone.data.strip() if form.phone.data else None
        student.department = form.department.data
        student.year = form.year.data
        student.cgpa = form.cgpa.data
        student.backlogs = form.backlogs.data
        student.tenth_percent = form.tenth_percent.data
        student.twelfth_percent = form.twelfth_percent.data
        student.skills = form.skills.data  # setter handles CSV → JSON
        student.coding_problems_count = form.coding_problems_count.data
        student.coding_platform = form.coding_platform.data
        student.projects_count = form.projects_count.data
        student.project_links = form.project_links.data
        student.internships_count = form.internships_count.data
        student.certifications_count = form.certifications_count.data
        student.communication_score = form.communication_score.data
        student.aptitude_score = form.aptitude_score.data
        student.mock_interview_score = form.mock_interview_score.data
        student.github_url = form.github_url.data.strip() if form.github_url.data else None
        student.linkedin_url = form.linkedin_url.data.strip() if form.linkedin_url.data else None

        # Handle resume upload
        resume_file = form.resume_file.data
        if resume_file and resume_file.filename:
            filename = f"{uuid.uuid4().hex}_{resume_file.filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            resume_file.save(filepath)
            # Delete old file if exists
            if student.resume_filename:
                old = os.path.join(current_app.config['UPLOAD_FOLDER'], student.resume_filename)
                if os.path.exists(old):
                    os.remove(old)
            student.resume_filename = filename

        # Recalculate score
        result = _refresh_score(student)
        db.session.commit()

        flash(
            f'Profile updated! New Readiness Score: {result["total_score"]} – {result["status"]}',
            'success'
        )
        return redirect(url_for('student.dashboard'))

    return render_template('student/profile.html', form=form, student=student)


# ---------------------------------------------------------------------------
# Placement drives for students
# ---------------------------------------------------------------------------
@student_bp.route('/drives')
@login_required
@student_required
def drives():
    student = current_user.student_profile
    today = datetime.now(timezone.utc).date()
    all_drives = (PlacementDrive.query
                  .order_by(PlacementDrive.drive_date)
                  .all())

    # Annotate with eligibility and application status
    drives_info = []
    applied_ids = set()
    if student:
        apps = DriveApplication.query.filter_by(student_id=student.id).all()
        applied_ids = {a.drive_id for a in apps}
        app_status = {a.drive_id: a.status for a in apps}
    else:
        app_status = {}

    for drive in all_drives:
        is_eligible = False
        if student:
            is_eligible, _ = drive.company.check_eligibility(student)
        drives_info.append({
            'drive': drive,
            'is_eligible': is_eligible,
            'applied': drive.id in applied_ids,
            'app_status': app_status.get(drive.id),
            'is_open': drive.is_registration_open()
        })

    return render_template('student/drives.html',
                           drives_info=drives_info,
                           student=student,
                           today=today)


# ---------------------------------------------------------------------------
# Apply to a drive
# ---------------------------------------------------------------------------
@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@login_required
@student_required
def apply_drive(drive_id):
    student = current_user.student_profile
    if not student:
        flash('Complete your profile before applying.', 'warning')
        return redirect(url_for('student.drives'))

    drive = PlacementDrive.query.get_or_404(drive_id)

    if not drive.is_registration_open():
        flash('Registration is closed for this drive.', 'warning')
        return redirect(url_for('student.drives'))

    existing = DriveApplication.query.filter_by(
        drive_id=drive_id, student_id=student.id
    ).first()
    if existing:
        flash('You have already applied to this drive.', 'info')
        return redirect(url_for('student.drives'))

    application = DriveApplication(drive_id=drive_id, student_id=student.id)
    db.session.add(application)
    db.session.commit()
    flash(f'Successfully applied to {drive.title}!', 'success')
    return redirect(url_for('student.drives'))


# ---------------------------------------------------------------------------
# Resume download
# ---------------------------------------------------------------------------
@student_bp.route('/resume/download')
@login_required
@student_required
def download_resume():
    student = current_user.student_profile
    if not student or not student.resume_filename:
        flash('No resume uploaded.', 'info')
        return redirect(url_for('student.edit_profile'))
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               student.resume_filename,
                               as_attachment=True)
