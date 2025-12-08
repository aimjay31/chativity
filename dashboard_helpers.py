from database_connector import get_db_connection

def get_task_stats(user_id):
    """
    Returns a dictionary with task stats for a user:
    total, completed, overdue, in_progress
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total FROM tasks WHERE assigned_to = %s
    """, (user_id,))
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) AS completed FROM tasks 
        WHERE assigned_to = %s AND status = 'completed'
    """, (user_id,))
    completed = cursor.fetchone()['completed']

    cursor.execute("""
        SELECT COUNT(*) AS overdue FROM tasks 
        WHERE assigned_to = %s AND status != 'completed' AND due_date < CURDATE()
    """, (user_id,))
    overdue = cursor.fetchone()['overdue']

    cursor.execute("""
        SELECT COUNT(*) AS in_progress FROM tasks 
        WHERE assigned_to = %s AND status = 'in_progress'
    """, (user_id,))
    in_progress = cursor.fetchone()['in_progress']

    cursor.close()
    conn.close()

    return {
        'total': total,
        'completed': completed,
        'overdue': overdue,
        'in_progress': in_progress
    }

def get_recent_tasks(user_id, limit=5):
    """
    Returns a list of recent tasks for a user
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, title, due_date, status FROM tasks 
        WHERE assigned_to = %s 
        ORDER BY due_date ASC LIMIT %s
    """, (user_id, limit))

    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks
