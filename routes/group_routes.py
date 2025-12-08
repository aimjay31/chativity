# routes/group_route.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from database_connector import get_db_connection

group_bp = Blueprint('group_bp', __name__, template_folder='../templates')

# Show all groups user is part of
@group_bp.route("/groups")
def groups_list():
    conn = get_db_connection()
    user_id = session.get('user_id')
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT g.id, g.name FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
    """, (user_id,))
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("groups.html", groups=groups)

# Create new group
@group_bp.route("/groups/new", methods=['GET', 'POST'])
def new_group():
    if request.method == 'POST':
        name = request.form['name']
        user_id = session.get('user_id')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO groups (name, created_by) VALUES (%s, %s)", (name, user_id))
        group_id = cursor.lastrowid
        cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)", (group_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('group_bp.groups_list'))
    return render_template("new_group.html")

# View group chat
@group_bp.route("/groups/<int:group_id>", methods=['GET', 'POST'])
def group_chat(group_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Send message
    if request.method == 'POST' and 'message' in request.form:
        message = request.form['message']
        sender_id = session.get('user_id')
        cursor.execute("INSERT INTO group_messages (group_id, sender_id, message) VALUES (%s,%s,%s)", (group_id, sender_id, message))
        conn.commit()

    # Get group info
    cursor.execute("SELECT * FROM groups WHERE id=%s", (group_id,))
    group = cursor.fetchone()

    # Get messages
    cursor.execute("""
        SELECT gm.*, u.name as sender_name FROM group_messages gm
        JOIN users u ON u.id = gm.sender_id
        WHERE gm.group_id=%s
        ORDER BY gm.created_at ASC
    """, (group_id,))
    messages = cursor.fetchall()

    # Get members
    cursor.execute("""
        SELECT u.id, u.name FROM group_members gm
        JOIN users u ON u.id = gm.user_id
        WHERE gm.group_id=%s
    """, (group_id,))
    members = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("group_chat.html", group=group, messages=messages, members=members)
