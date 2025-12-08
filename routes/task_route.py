from flask import Blueprint, render_template, request, redirect, url_for, session
from database_connector import get_db_connection

task_bp = Blueprint("task_bp", __name__, template_folder="../templates")

# -----------------------------
# View all tasks
# -----------------------------
@task_bp.route("/task")
def task_list():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    user_id = session["user_id"]
    cursor.execute("""
        SELECT t.*, u.name as assigned_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        WHERE t.assigned_to=%s OR t.created_by=%s
        ORDER BY t.due_date ASC
    """, (user_id, user_id))
    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("task.html", tasks=tasks)

# -----------------------------
# Create new task
# -----------------------------
@task_bp.route("/task/new", methods=["GET", "POST"])
def new_task():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all users for assign dropdown
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        due_date = request.form.get("due_date")
        priority = request.form.get("priority")
        assigned_to = request.form.get("assigned_to") or session["user_id"]

        cursor.execute(
            "INSERT INTO tasks (title, description, due_date, priority, assigned_to, created_by, status) "
            "VALUES (%s,%s,%s,%s,%s,%s,'pending')",
            (title, description, due_date, priority, assigned_to, session["user_id"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("task_bp.task_list"))

    cursor.close()
    conn.close()
    return render_template("task_new.html", users=users)

# -----------------------------
# Complete task
# -----------------------------
@task_bp.route("/task/complete/<int:task_id>")
def complete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status='completed' WHERE id=%s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("task_bp.task_list"))

# -----------------------------
# Delete task
# -----------------------------
@task_bp.route("/task/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s AND created_by=%s", (task_id, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("task_bp.task_list"))

# View task detail
@task_bp.route("/task/<int:task_id>")
def task_detail(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT t.*, u.name as assigned_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        WHERE t.id=%s
    """, (task_id,))
    task = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not task:
        return "Task not found", 404
    
    return render_template("task_detail.html", task=task)
