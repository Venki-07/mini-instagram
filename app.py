from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import bcrypt
from datetime import datetime

app = Flask(__name__)

app.secret_key = "my-secret-key"

# MongoDB connection
client = MongoClient("YOUR_MONGODB_CONNECTION_STRING")

db = client["mini_instagram"]

users = db["users"]
posts = db["posts"]


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check existing user
        existing_user = users.find_one({"email": email})

        if existing_user:
            return "User already exists!"

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # Save user
        users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users.find_one({"email": email})

        if user:

            password_correct = bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"]
            )

            if password_correct:

                # Save user in session
                session["username"] = user["username"]

                return redirect("/home")

        return "Invalid email or password"

    return render_template("login.html")


# ---------------- HOME ----------------

@app.route("/home")
def home():

    if "username" not in session:
        return redirect("/login")

    all_posts = posts.find().sort("created_at", -1)

    return render_template(
        "home.html",
        username=session["username"],
        posts=all_posts
    )


# ---------------- CREATE POST ----------------

@app.route("/post", methods=["POST"])
def create_post():

    if "username" not in session:
        return redirect("/login")

    caption = request.form["caption"]

    posts.insert_one({
        "username": session["username"],
        "caption": caption,
        "created_at": datetime.now()
    })

    return redirect("/home")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- START ----------------

if __name__ == "__main__":
    app.run(debug=True)
