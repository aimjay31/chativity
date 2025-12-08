from flask import Blueprint, render_template, session, redirect, url_for
from dashboard_helpers import get_task_stats, get_recent_tasks

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]
    user_name = session.get("user_name", "User")

    # Fetch dynamic data
    stats = get_task_stats(user_id)
    recent_tasks = get_recent_tasks(user_id, limit=5)

    return render_template(
        "dashboard.html",
        user_name=user_name,
        stats=stats,
        recent_tasks=recent_tasks
    )
