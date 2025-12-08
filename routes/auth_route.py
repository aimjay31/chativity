from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

auth_bp = Blueprint('auth_bp', __name__)

# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chativity_db",
            auth_plugin='mysql_native_password'
        )
        return connection
    except Error as e:
        print("❌ Database connection error:", e)
        return None

# -------------------------
# REGISTER ROUTE
# -------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn is None:
            return "Database connection error"

        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )
            conn.commit()
            flash("✅ Registration successful. Please login.", "success")
            return redirect(url_for("auth_bp.login"))
        except mysql.connector.IntegrityError:
            flash("❌ Email already exists.", "danger")
            return redirect(url_for("auth_bp.register"))
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# -------------------------
# LOGIN ROUTE
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if conn is None:
            return "Database connection error"

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"✅ Welcome {user['name']}!", "success")
            return redirect(url_for("dashboard_bp.dashboard"))
        else:
            flash("❌ Invalid email or password.", "danger")
            return redirect(url_for("auth_bp.login"))

    return render_template("login.html")

# -------------------------
# LOGOUT ROUTE
# -------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("✅ You have been logged out.", "success")
    return redirect(url_for("auth_bp.login"))
