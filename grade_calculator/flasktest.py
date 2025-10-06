from flask import Flask, render_template, request, redirect, url_for, session
import webscraping
from markupsafe import escape
from dotenv import load_dotenv
import os

app = Flask(__name__)
#load_dotenv()
app.secret_key = os.environ["SECRET_KEY"]


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        webscraping.signIn(username, password)
        if not webscraping.checkSignIn():
            return render_template("login.html",
                                   error="Invalid username or password")
        courselist = webscraping.getCourseList()
        session['courselist'] = courselist
        return redirect(url_for("main"))
    return render_template("login.html")


@app.route("/main", methods=["POST", "GET"])
def main():
    courselist = session.get('courselist')
    if not courselist:
        return redirect(url_for("/"))
    selected_course = courselist[0]
    selected_quarter = "Q2"
    assignments = []

    if request.method == "POST":

        selected_course = request.form.get('course_selection')
        selected_quarter = request.form.get('mp_selection')
        try:
            course_link = webscraping.getCorrectCourseLink(
                selected_course, selected_quarter)
            if course_link:
                assignments = webscraping.getQuarterAssignmentInfo(course_link)
        except:
            print("Error while scraping.")
    return render_template("main.html",
                           courselist=courselist,
                           selected_course=selected_course,
                           selected_quarter=selected_quarter,
                           assignments=assignments)


if __name__ == "__main__":
    app.run()
