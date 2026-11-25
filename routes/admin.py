"""
routes/admin.py – All admin/placement-officer views.
Blueprint prefix: /admin
"""
from datetime import datetime, timezone
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, send_file, abort)
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db, User, StudentProfile, ScoreHistory, Company, PlacementDrive, DriveApplication
from forms import CompanyForm, PlacementDriveForm
from services.scoring import evaluate_student_readiness
from services.reports import generate_students_csv, generate_placement_pdf
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__)

STUDENTS_PER_PAGE = 15


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = StudentProfile.query.count()
    all_students = StudentProfile.query.all()

    scores = [s.current_readiness_score for s in all_students]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    status_counts = {
        'ready': sum(1 for s in all_students if s.current_readiness_score >= 80),
        'almost': sum(1 for s in all_students if 60 <= s.current_readiness_score < 80),
        'developing': sum(1 for s in all_students if 40 <= s.current_readiness_score < 60),
        'not_ready': sum(1 for s in all_students if s.current_readiness_score < 40),
    }
    at_risk = [s for s in all_students if s.current_readiness_score < 40]

    # Dept breakdown
    depts = db.session.query(
        StudentProfile.department,
        func.count(StudentProfile.id).label('count'),
        func.avg(StudentProfile.current_readiness_score).label('avg_score'),
        func.avg(StudentProfile.cgpa).label('avg_cgpa')
    ).group_by(StudentProfile.department).all()

    dept_stats = []
    for d in depts:
        dept_students = [s for s in all_students if s.department == d.department]
        ready_count = sum(1 for s in dept_students if s.current_readiness_score >= 80)
        dept_stats.append({
            'name': d.department,
            'count': d.count,
            'avg_score': round(float(d.avg_score or 0), 1),
            'avg_cgpa': round(float(d.avg_cgpa or 0), 2),
            'ready_count': ready_count,
            'ready_rate': round((ready_count / d.count * 100) if d.count else 0, 1)
        })

    # Top performers
    top_students = (StudentProfile.query
                    .order_by(StudentProfile.current_readiness_score.desc())
                    .limit(5).all())

    # Recent drives
    today = datetime.now(timezone.utc).date()
    upcoming_drives = (PlacementDrive.query
                       .filter(PlacementDrive.drive_date >= today)
                       .order_by(PlacementDrive.drive_date)
                       .limit(5).all())

    # Skill popularity
    all_skills = []
    for s in all_students:
        all_skills.extend(s.skills)
    skill_freq = {}
    for sk in all_skills:
        skill_freq[sk] = skill_freq.get(sk, 0) + 1
    top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    stats = {
        'total_students': total_students,
        'avg_score': avg_score,
        'ready_count': status_counts['ready'],
        'ready_pct': round(status_counts['ready'] / total_students * 100, 1) if total_students else 0,
        'at_risk_count': len(at_risk),
        'at_risk_pct': round(len(at_risk) / total_students * 100, 1) if total_students else 0,
        'eligible_top': sum(1 for s in all_students if s.current_readiness_score >= 75)
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        status_counts=status_counts,
        dept_stats=dept_stats,
        top_students=top_students,
        at_risk=at_risk[:5],
        upcoming_drives=upcoming_drives,
        top_skills=top_skills,
        today=today
    )


# ---------------------------------------------------------------------------
# Students list (search, filter, paginate)
# ---------------------------------------------------------------------------
@admin_bp.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('dept', '')
    year_filter = request.args.get('year', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'score_desc')

    query = StudentProfile.query.join(User)

    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (StudentProfile.roll_number.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    if dept_filter:
        query = query.filter(StudentProfile.department == dept_filter)
    if year_filter:
        query = query.filter(StudentProfile.year == year_filter)
    if status_filter:
        query = query.filter(StudentProfile.current_status == status_filter)

    # Sorting
    if sort_by == 'score_asc':
        query = query.order_by(StudentProfile.current_readiness_score.asc())
    elif sort_by == 'cgpa_desc':
        query = query.order_by(StudentProfile.cgpa.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(User.full_name.asc())
    else:
        query = query.order_by(StudentProfile.current_readiness_score.desc())

    pagination = query.paginate(page=page, per_page=STUDENTS_PER_PAGE, error_out=False)

    # Department list for filter dropdown
    departments = [r[0] for r in db.session.query(StudentProfile.department).distinct().all()]
    years = ['1st Year', '2nd Year', '3rd Year', '4th Year']
    statuses = ['Placement Ready', 'Almost Ready', 'Developing', 'Not Ready']

    return render_template(
        'admin/students.html',
        pagination=pagination,
        students=pagination.items,
        search=search,
        dept_filter=dept_filter,
        year_filter=year_filter,
        status_filter=status_filter,
        sort_by=sort_by,
        departments=departments,
        years=years,
        statuses=statuses
    )


# ---------------------------------------------------------------------------
# Student detail view
# ---------------------------------------------------------------------------
@admin_bp.route('/students/<int:student_id>')
@login_required
@admin_required
def student_detail(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    result = evaluate_student_readiness(student)

    history = (ScoreHistory.query
               .filter_by(student_id=student.id)
               .order_by(ScoreHistory.recorded_at.asc())
               .all())

    all_companies = Company.query.all()
    eligibility = []
    for company in all_companies:
        is_eligible, details = company.check_eligibility(student)
        eligibility.append({'company': company, 'is_eligible': is_eligible, 'details': details})

    return render_template(
        'admin/student_detail.html',
        student=student,
        result=result,
        history=history,
        eligibility=eligibility
    )


# ---------------------------------------------------------------------------
# Companies CRUD
# ---------------------------------------------------------------------------
@admin_bp.route('/companies')
@login_required
@admin_required
def companies():
    all_companies = Company.query.order_by(Company.package_lpa.desc()).all()
    return render_template('admin/companies.html', companies=all_companies)


@admin_bp.route('/companies/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_company():
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data.strip(),
            industry=form.industry.data.strip(),
            role_offered=form.role_offered.data.strip(),
            package_lpa=form.package_lpa.data,
            min_cgpa=form.min_cgpa.data,
            max_backlogs=form.max_backlogs.data,
            location=form.location.data.strip(),
            website=form.website.data.strip() if form.website.data else None,
            description=form.description.data
        )
        company.required_skills = form.required_skills.data
        db.session.add(company)
        db.session.commit()
        flash(f'Company "{company.name}" added successfully!', 'success')
        return redirect(url_for('admin.companies'))
    return render_template('admin/company_form.html', form=form, action='Add')


@admin_bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    form = CompanyForm(obj=company)

    if request.method == 'GET':
        form.required_skills.data = ', '.join(company.required_skills)

    if form.validate_on_submit():
        company.name = form.name.data.strip()
        company.industry = form.industry.data.strip()
        company.role_offered = form.role_offered.data.strip()
        company.package_lpa = form.package_lpa.data
        company.min_cgpa = form.min_cgpa.data
        company.max_backlogs = form.max_backlogs.data
        company.location = form.location.data.strip()
        company.website = form.website.data.strip() if form.website.data else None
        company.description = form.description.data
        company.required_skills = form.required_skills.data
        db.session.commit()
        flash(f'Company "{company.name}" updated.', 'success')
        return redirect(url_for('admin.companies'))

    return render_template('admin/company_form.html', form=form, company=company, action='Edit')


@admin_bp.route('/companies/<int:company_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    name = company.name
    db.session.delete(company)
    db.session.commit()
    flash(f'Company "{name}" deleted.', 'info')
    return redirect(url_for('admin.companies'))


# ---------------------------------------------------------------------------
# Placement Drives CRUD
# ---------------------------------------------------------------------------
@admin_bp.route('/drives')
@login_required
@admin_required
def drives():
    all_drives = (PlacementDrive.query
                  .order_by(PlacementDrive.drive_date.desc())
                  .all())
    return render_template('admin/drives.html', drives=all_drives)


@admin_bp.route('/drives/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_drive():
    form = PlacementDriveForm()
    form.company_id.choices = [(c.id, c.name) for c in Company.query.order_by(Company.name).all()]
    if form.validate_on_submit():
        drive = PlacementDrive(
            company_id=form.company_id.data,
            title=form.title.data.strip(),
            drive_date=form.drive_date.data,
            registration_deadline=form.registration_deadline.data,
            status=form.status.data,
            venue=form.venue.data.strip(),
            instructions=form.instructions.data
        )
        db.session.add(drive)
        db.session.commit()
        flash(f'Drive "{drive.title}" created!', 'success')
        return redirect(url_for('admin.drives'))
    return render_template('admin/drive_form.html', form=form, action='Add')


@admin_bp.route('/drives/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    form = PlacementDriveForm(obj=drive)
    form.company_id.choices = [(c.id, c.name) for c in Company.query.order_by(Company.name).all()]

    if form.validate_on_submit():
        drive.company_id = form.company_id.data
        drive.title = form.title.data.strip()
        drive.drive_date = form.drive_date.data
        drive.registration_deadline = form.registration_deadline.data
        drive.status = form.status.data
        drive.venue = form.venue.data.strip()
        drive.instructions = form.instructions.data
        db.session.commit()
        flash(f'Drive "{drive.title}" updated.', 'success')
        return redirect(url_for('admin.drives'))

    return render_template('admin/drive_form.html', form=form, drive=drive, action='Edit')


@admin_bp.route('/drives/<int:drive_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    title = drive.title
    db.session.delete(drive)
    db.session.commit()
    flash(f'Drive "{title}" deleted.', 'info')
    return redirect(url_for('admin.drives'))


# ---------------------------------------------------------------------------
# Export endpoints
# ---------------------------------------------------------------------------
@admin_bp.route('/export/csv')
@login_required
@admin_required
def export_csv():
    all_students = (StudentProfile.query
                    .join(User)
                    .order_by(StudentProfile.current_readiness_score.desc())
                    .all())
    csv_buffer = generate_students_csv(all_students)
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'placement_report_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")}.csv'
    )


@admin_bp.route('/export/pdf')
@login_required
@admin_required
def export_pdf():
    all_students = (StudentProfile.query
                    .join(User)
                    .order_by(StudentProfile.current_readiness_score.desc())
                    .all())
    scores = [s.current_readiness_score for s in all_students]
    total = len(all_students)
    avg_score = round(sum(scores) / total, 1) if total else 0
    ready_count = sum(1 for s in all_students if s.current_readiness_score >= 80)
    at_risk_count = sum(1 for s in all_students if s.current_readiness_score < 40)

    # Build dept stats
    dept_map = {}
    for s in all_students:
        d = s.department
        if d not in dept_map:
            dept_map[d] = []
        dept_map[d].append(s)

    dept_stats = []
    for d, students in dept_map.items():
        ready = sum(1 for s in students if s.current_readiness_score >= 80)
        dept_stats.append({
            'name': d,
            'count': len(students),
            'avg_cgpa': round(sum(s.cgpa for s in students) / len(students), 2),
            'avg_score': round(sum(s.current_readiness_score for s in students) / len(students), 1),
            'ready_count': ready,
            'ready_rate': round((ready / len(students)) * 100, 1) if students else 0
        })

    stats = {
        'total_students': total,
        'avg_score': avg_score,
        'ready_count': ready_count,
        'ready_pct': round(ready_count / total * 100, 1) if total else 0,
        'at_risk_count': at_risk_count,
        'at_risk_pct': round(at_risk_count / total * 100, 1) if total else 0
    }

    top_students = all_students[:10]
    pdf_buffer = generate_placement_pdf(stats, top_students, dept_stats)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'placement_report_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")}.pdf'
    )
