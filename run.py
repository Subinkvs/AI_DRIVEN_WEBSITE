from app import create_app
from flask import Flask, render_template
from flask import send_from_directory

app = create_app()


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/auth/register")
def register():
    return render_template("signup.html")


@app.route("/auth/login")
def login():
    return render_template("login.html")


@app.route("/staticfiles/<path:filename>")
def serve_staticfiles(filename):
    return send_from_directory("staticfiles", filename)


if __name__ == "__main__":
    app.run(debug=True)
