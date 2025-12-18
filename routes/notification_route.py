# routes/notification_route.py
from flask import Blueprint, session, redirect, url_for, render_template
from database_connector import get_db_connection

notification_bp = Blueprint("notification_bp", __name__, template_folder="../templates")


# -----------------------------
# Create Notification
# -----------------------------
def create_notification(user_id, message):
    """
    Inserts a new notification for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
        (user_id, message)
    )
    conn.commit()
    cursor.close()
    conn.close()


# -----------------------------
# Notifications Page
# -----------------------------
@notification_bp.route("/notifications")
def notifications():
    """
    Displays all notifications for the logged-in user
    and updates unread count in the session for sidebar badge.
    """
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all notifications
    cursor.execute(
        "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    notifications_list = cursor.fetchall()

    # Calculate unread notifications
    unread_count = sum(1 for n in notifications_list if n["is_read"] == 0)
    session['unread_notifications'] = unread_count

    cursor.close()
    conn.close()

    return render_template("notifications.html", notifications=notifications_list, unread_count=unread_count)


# -----------------------------
# Mark Notification as Read
# -----------------------------
@notification_bp.route("/notifications/read/<int:notification_id>")
def read_notification(notification_id):
    """
    Marks a notification as read and updates the unread badge.
    """
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notifications SET is_read = 1 WHERE id=%s AND user_id=%s",
        (notification_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("notification_bp.notifications"))

@notification_bp.route("/notifications/toggle-read/<int:notification_id>", methods=["POST"])
def toggle_read(notification_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Toggle is_read
    cursor.execute("""
        UPDATE notifications
        SET is_read = IF(is_read=1, 0, 1)
        WHERE id=%s AND user_id=%s
    """, (notification_id, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("notification_bp.notifications"))
