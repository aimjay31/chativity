from flask import Flask, render_template

app = Flask(__name__)

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/task")
def task():
    return render_template("task.html")

@app.route("/sidebar")
def sidebar():
    return render_template("sidebar.html")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
