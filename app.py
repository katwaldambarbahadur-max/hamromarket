from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hamromarket_secret_key"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Initialization
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        image TEXT,
        seller TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# Home Page
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template("index.html", products=products)

# Register Seller
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username,password)
            )
            conn.commit()
            return redirect("/login")

        except:
            return "Username already exists"

    return render_template("register.html")

# Login Seller
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect("/")

        return "Login Failed"

    return render_template("login.html")

# Add Product
@app.route("/add", methods=["GET","POST"])
def add_product():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]
        seller = session["user"]

        image = request.files["image"]
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO products(name,price,image,seller) VALUES(?,?,?,?)",
            (name, price, image.filename, seller)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_product.html")

# Delete Product
@app.route("/delete/<int:product_id>")
def delete_product(product_id):

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id=? AND seller=?",
        (product_id, session["user"])
    )

    conn.commit()
    conn.close()

    return redirect("/")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# Run Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)