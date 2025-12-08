import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",        # Or your MySQL server IP
            user="root",             # Your MySQL username
            password="",             # Your MySQL password
            database="chativity_db" # Replace with your database name
        )

        if connection.is_connected():
            print("✅ Successfully connected to MySQL Database")
            db_info = connection.get_server_info()
            print("MySQL Server Version:", db_info)

    except Error as e:
        print("❌ Error while connecting to MySQL:", e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔌 MySQL connection closed")

if __name__ == "__main__":
    test_connection()
