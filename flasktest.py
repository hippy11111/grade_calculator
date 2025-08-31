from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
from dotenv import load_dotenv
import os
import webscraping

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET")


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        driver = webscraping.createDriver()
        try:
            webscraping.signIn(driver, username, password)
            if not webscraping.checkSignIn(driver):
                return render_template("login.html", error="Invalid username or password")
            
            courselist = webscraping.getCourseList(driver)
            session['courselist'] = courselist
            session['username'] = username
            session['password'] = password  # store credentials temporarily for scraping
            return redirect(url_for("main"))
        finally:
            driver.quit()

    return render_template("login.html")


@app.route("/main", methods=["POST", "GET"])
def main():
    courselist = session.get('courselist')
    if not courselist:
        return redirect(url_for("login"))

    username = session.get('username')
    password = session.get('password')

    selected_course = courselist[0]
    selected_quarter = "Q2"
    assignments = []

    if request.method == "POST":
        selected_course = request.form.get('course_selection')
        selected_quarter = request.form.get('mp_selection')

        driver = webscraping.createDriver()
        try:
            webscraping.signIn(driver, username, password)
            course_link = webscraping.getCorrectCourseLink(driver, selected_course, selected_quarter)
            if course_link:
                assignments = webscraping.getQuarterAssignmentInfo(driver, course_link)
        except Exception as e:
            print("Error while scraping:", e)
        finally:
            driver.quit()

    return render_template(
        "main.html",
        courselist=courselist,
        selected_course=selected_course,
        selected_quarter=selected_quarter,
        assignments=assignments
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
