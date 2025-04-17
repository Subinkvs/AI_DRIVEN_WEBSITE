from app import create_app
from flask import Flask, render_template
from flask import send_from_directory

# Create the Flask application using the factory function
app = create_app()


@app.route("/")
def home():
    """
    Route handler for the homepage.

    This route serves the main page of the website (index.html).
    It renders the homepage when the user navigates to the root URL.
    """
    return render_template("index.html")



@app.route("/auth/register")
def register():
    """
    Route handler for the registration page.

    This route serves the registration page (signup.html) where users can
    sign up for an account.
    """
    return render_template("signup.html")


@app.route("/auth/login")
def login():
    """
    Route handler for the login page.

    This route serves the login page (login.html) where users can log in
    to their accounts.
    """
    return render_template("login.html")

@app.route('/contact')
def content():
    return render_template("contact.html")


@app.route("/staticfiles/<path:filename>")
def serve_staticfiles(filename):
    """
    Route handler for serving static files.

    This route allows serving static files from the 'staticfiles' directory.
    It retrieves and sends the requested file based on the given filename.
    """
    return send_from_directory("staticfiles", filename)


if __name__ == "__main__":
    app.run(debug=True)
