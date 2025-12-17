from flask import Blueprint, render_template, request, redirect, url_for, session
from database_connector import get_db_connection
from werkzeug.security import generate_password_hash
profile_bp = Blueprint("profile_bp", __name__, template_folder="../templates")

# Profile page

@profile_bp.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    # calculate stats
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS tasks_completed,
            CONCAT(ROUND(SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END)/COUNT(*)*100,0),'%') AS success_rate
        FROM tasks
        WHERE assigned_to=%s OR created_by=%s
    """, (user_id, user_id))
    stats = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("profile.html", user=user, stats=stats)





import os
from flask import current_app, request, redirect, url_for, flash

@profile_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    if request.method == "POST":
        name = request.form.get("name")
        organization = request.form.get("organization")
        position = request.form.get("position")
        bio = request.form.get("bio")
        age = request.form.get("age")
        year = request.form.get("year")

        # Handle profile picture
        profile_pic = user["profile_pic"]
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and file.filename:
                filename = f"user_{user_id}{os.path.splitext(file.filename)[1]}"
                upload_path = os.path.join(current_app.root_path, "static/uploads/profile_pics", filename)
                file.save(upload_path)
                profile_pic = filename

        # Update user
        cursor.execute("""
            UPDATE users SET name=%s, organization=%s, position=%s, bio=%s, age=%s, year=%s, profile_pic=%s
            WHERE id=%s
        """, (name, organization, position, bio, age, year, profile_pic, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile_bp.profile"))

    cursor.close()
    conn.close()
    return render_template("edit_profile.html", user=user)



# Notifications page
@profile_bp.route("/profile/notifications")
def notifications():
    return render_template("notifications.html")

# Privacy page
@profile_bp.route("/profile/privacy")
def privacy():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("privacy.html", user=user)  # Pass user object


# Change password
@profile_bp.route("/profile/change-password", methods=["POST"])
def change_password():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    current = request.form.get("current_password")
    new = request.form.get("new_password")
    confirm = request.form.get("confirm_password")

    if new != confirm:
        return "New passwords do not match!", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT password FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user or user["password"] != current:
        cursor.close()
        conn.close()
        return "Current password is incorrect!", 400

    cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("profile_bp.profile"))

# Update privacy preferences
@profile_bp.route("/profile/update-privacy", methods=["POST"])
def update_privacy():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    email_notifications = 1 if request.form.get("email_notifications") else 0
    show_profile = 1 if request.form.get("show_profile") else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET email_notifications=%s, show_profile=%s
        WHERE id=%s
    """, (email_notifications, show_profile, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("profile_bp.profile"))


@profile_bp.context_processor
def load_user_profile():
    """
    Make user profile info available in all templates (sidebar, etc.)
    """

    user_id = session.get('user_id')
    
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, role, position, profile_pic FROM users WHERE id=%s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return dict(user_profile={
                'id': user['id'],
                'name': user['name'],
                'role': user['role'],
                'position': user['position'],
                'profile_pic': user['profile_pic']
            })

    # Default values if not logged in
    return dict(user_profile={
        'id': None,
        'name': 'User',
        'role': 'User',
        'position': '',
        'profile_pic': None
    })

