from flask import Flask, redirect, url_for, session
from database_connector import get_db_connection

# Import all route blueprints
from routes.index_route import index_bp
from routes.auth_route import auth_bp
from routes.dashboard_route import dashboard_bp
from routes.profile_route import profile_bp
from routes.task_route import task_bp
from routes.notification_route import notification_bp
from routes.group_route import group_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management

# -----------------------------
# REGISTER BLUEPRINTS
# -----------------------------
app.register_blueprint(index_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(task_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(group_bp)

# -----------------------------
# REDIRECT ROOT TO INDEX
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("index_bp.index"))


@app.context_processor
def load_user_profile():
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
# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
