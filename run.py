from app import create_app
from flask import Flask, render_template
app = create_app()


@app.route('/')
def home():
    return render_template('index.html')

@app.route("/auth/register")
def register():
    return render_template("signup.html")


@app.route("/auth/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
