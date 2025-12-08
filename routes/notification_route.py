from flask import Blueprint, render_template, session
from database_connector import get_db_connection

notification_bp = Blueprint('notification_bp', __name__)

@notification_bp.route("/notifications")
def notifications():
    # Ensure user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return "Please log in to view notifications", 401

    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch notifications for this user
    cursor.execute("""
        SELECT id, type, title, message, link, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        """, (user_id,))
    notifications_list = cursor.fetchall()

    # Count unread notifications for sidebar badge
    unread_count = sum(1 for n in notifications_list if n['is_read'] == 0)
    session['unread_notifications'] = unread_count

    cursor.close()
    conn.close()

    return render_template("notifications.html", notifications=notifications_list)
