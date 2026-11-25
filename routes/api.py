"""
routes/api.py – JSON API endpoints consumed by Chart.js dashboards.
Blueprint prefix: /api
"""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db, StudentProfile, ScoreHistory, Company
from routes.auth import admin_required
from services.scoring import evaluate_student_readiness

api_bp = Blueprint('api', __name__)


# ---------------------------------------------------------------------------
# Student APIs
# ---------------------------------------------------------------------------

@api_bp.route('/student/score')
@login_required
def student_score():
    """Current category breakdown for the logged-in student."""
    if not current_user.is_student or not current_user.student_profile:
        return jsonify({'error': 'No student profile found'}), 404

    student = current_user.student_profile
    result = evaluate_student_readiness(student)

    cats = result['categories']
    return jsonify({
        'total_score': result['total_score'],
        'status': result['status'],
        'categories': {
            'labels': [c['label'] for c in cats.values()],
            'scores': [c['score'] for c in cats.values()],
            'weights': [c['weight'] for c in cats.values()],
            'weighted_points': [c['weighted_points'] for c in cats.values()]
        }
    })


@api_bp.route('/student/history')
@login_required
def student_history():
    """Score progression over time for the logged-in student."""
    if not current_user.is_student or not current_user.student_profile:
        return jsonify({'error': 'No student profile found'}), 404

    student = current_user.student_profile
    history = (ScoreHistory.query
               .filter_by(student_id=student.id)
               .order_by(ScoreHistory.recorded_at.asc())
               .all())

    return jsonify({
        'labels': [h.recorded_at.strftime('%d %b') for h in history],
        'total_scores': [h.total_score for h in history],
        'academic': [h.academic_score for h in history],
        'technical': [h.technical_score for h in history],
        'experience': [h.experience_score for h in history],
        'aptitude': [h.aptitude_score for h in history],
        'communication': [h.communication_score for h in history]
    })


# ---------------------------------------------------------------------------
# Admin APIs
# ---------------------------------------------------------------------------

@api_bp.route('/admin/stats')
@login_required
@admin_required
def admin_stats():
    """High-level KPI numbers for admin dashboard."""
    all_students = StudentProfile.query.all()
    total = len(all_students)
    scores = [s.current_readiness_score for s in all_students]
    avg = round(sum(scores) / total, 1) if total else 0

    return jsonify({
        'total_students': total,
        'avg_score': avg,
        'ready_count': sum(1 for s in all_students if s.current_readiness_score >= 80),
        'almost_count': sum(1 for s in all_students if 60 <= s.current_readiness_score < 80),
        'developing_count': sum(1 for s in all_students if 40 <= s.current_readiness_score < 60),
        'not_ready_count': sum(1 for s in all_students if s.current_readiness_score < 40),
        'eligible_top': sum(1 for s in all_students if s.current_readiness_score >= 75),
        'at_risk': sum(1 for s in all_students if s.current_readiness_score < 40)
    })


@api_bp.route('/admin/department-analysis')
@login_required
@admin_required
def department_analysis():
    """Department-wise readiness breakdown."""
    rows = db.session.query(
        StudentProfile.department,
        func.count(StudentProfile.id).label('count'),
        func.avg(StudentProfile.current_readiness_score).label('avg_score'),
        func.avg(StudentProfile.cgpa).label('avg_cgpa')
    ).group_by(StudentProfile.department).all()

    all_students = StudentProfile.query.all()
    result = []
    for row in rows:
        dept_students = [s for s in all_students if s.department == row.department]
        ready = sum(1 for s in dept_students if s.current_readiness_score >= 80)
        result.append({
            'department': row.department,
            'count': row.count,
            'avg_score': round(float(row.avg_score or 0), 1),
            'avg_cgpa': round(float(row.avg_cgpa or 0), 2),
            'ready_count': ready,
            'ready_rate': round((ready / row.count * 100) if row.count else 0, 1)
        })

    return jsonify(result)


@api_bp.route('/admin/skills-distribution')
@login_required
@admin_required
def skills_distribution():
    """Skill popularity across all students."""
    all_students = StudentProfile.query.all()
    skill_freq = {}
    for s in all_students:
        for skill in s.skills:
            skill_freq[skill] = skill_freq.get(skill, 0) + 1

    sorted_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:12]
    return jsonify({
        'labels': [s[0] for s in sorted_skills],
        'counts': [s[1] for s in sorted_skills]
    })
