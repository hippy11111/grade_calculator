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
        
        # Use webscraping.signIn to get a driver instance
        driver = webscraping.signIn(username, password)
        
        if not webscraping.checkSignIn(driver):
            driver.quit()  # Close the driver if login failed
            return render_template("login.html", error="Invalid username or password")
        
        # Get course list using the same driver
        courselist = webscraping.getCourseList(driver)
        session['courselist'] = courselist
        session['driver'] = True  # just a flag to indicate driver exists (cannot store driver object in session)
        # keep driver alive for scraping later by passing it to functions via a global dict
        app.config['DRIVER'] = driver
        
        return redirect(url_for("main"))
    return render_template("login.html")


@app.route("/main", methods=["POST", "GET"])
def main():
    courselist = session.get('courselist')
    if not courselist:
        return redirect(url_for("login"))
    
    driver = app.config.get('DRIVER')
    if not driver:
        return redirect(url_for("login"))

    selected_course = courselist[0]
    selected_quarter = "Q2"
    assignments = []

    if request.method == "POST":
        selected_course = request.form.get('course_selection')
        selected_quarter = request.form.get('mp_selection')
        try:
            course_link = webscraping.getCorrectCourseLink(driver, selected_course, selected_quarter)
            if course_link:
                assignments = webscraping.getQuarterAssignmentInfo(driver, course_link)
        except Exception as e:
            print("Error while scraping:", e)
            return render_template("main.html", courselist=courselist)

    return render_template("main.html",
                           courselist=courselist,
                           selected_course=selected_course,
                           selected_quarter=selected_quarter,
                           assignments=assignments)


@app.teardown_appcontext
def close_driver(exception):
    driver = app.config.get('DRIVER')
    if driver:
        driver.quit()  # ensure Chrome closes when app stops


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
