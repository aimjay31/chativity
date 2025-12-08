# db.py
import mysql.connector
from mysql.connector import Error

# ---------------------------
# MySQL DATABASE CONNECTION
# ---------------------------

def get_db_connection():
    """
    Returns a MySQL connection object.
    Import and use this in all Flask routes.
    """

    try:
        connection = mysql.connector.connect(
            host="localhost",         # Change to your host or IP
            user="root",              # Change to your MySQL user
            password="",              # Change to your MySQL password
            database="chativity_db",   # Change to your database name
            auth_plugin=''  # Avoids auth issues
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print("❌ Database connection failed:", e)
        return None
