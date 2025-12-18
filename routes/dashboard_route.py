from flask import Blueprint, session, redirect, url_for, render_template
from database_connector import get_db_connection
from datetime import datetime

dashboard_bp = Blueprint("dashboard_bp", __name__, template_folder="../templates")

def get_task_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE assigned_to=%s", (user_id,))
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS completed FROM tasks WHERE assigned_to=%s AND status='completed'", (user_id,))
    completed = cursor.fetchone()["completed"]

    cursor.execute("SELECT COUNT(*) AS overdue FROM tasks WHERE assigned_to=%s AND status!='completed' AND due_date < NOW()", (user_id,))
    overdue = cursor.fetchone()["overdue"]

    cursor.execute("SELECT COUNT(*) AS in_progress FROM tasks WHERE assigned_to=%s AND status='in_progress'", (user_id,))
    in_progress = cursor.fetchone()["in_progress"]

    cursor.close()
    conn.close()

    return {
        "total": total,
        "completed": completed,
        "overdue": overdue,
        "in_progress": in_progress
    }

def get_recent_tasks(user_id, limit=5):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, title, due_date, status 
        FROM tasks 
        WHERE assigned_to=%s 
        ORDER BY due_date DESC 
        LIMIT %s
    """, (user_id, limit))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

def get_calendar_tasks(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, title, due_date, status
        FROM tasks
        WHERE assigned_to=%s
    """, (user_id,))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]
    user_name = session.get("user_name", "User")

    stats = get_task_stats(user_id)
    recent_tasks = get_recent_tasks(user_id, limit=5)
    calendar_tasks = get_calendar_tasks(user_id)

    # Prepare task data for calendar JS
    calendar_data = [
        {
            "id": t["id"],
            "title": t["title"],
            "date": t["due_date"].strftime("%Y-%m-%d"),
            "status": t["status"]
        } for t in calendar_tasks
    ]

    return render_template(
        "dashboard.html",
        user_name=user_name,
        stats=stats,
        recent_tasks=recent_tasks,
        calendar_tasks=calendar_data
    )
