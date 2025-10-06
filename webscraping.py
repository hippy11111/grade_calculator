# pip3 install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup
#import undetected_chromedriver as uc
import sys
import time

#from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service

options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.binary_location = "/nix/store/n6m949x5r35yf75yfaw504cb37n0fxcw-chromium-114.0.5735.106/bin/chromium"

service = Service(executable_path="/nix/store/n4qcnqy0isnvxcpcgv6i2z9ql9wsxksw-chromedriver-114.0.5735.90/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

def signIn(username, password):    
    driver.get("https://spprep.powerschool.com/public")
     # Find Username, password, and button
    uname = driver.find_element(By.NAME, value="account")
    pword = driver.find_element(By.NAME, value="pw")
    button = driver.find_element(By.ID, value="btn-enter-sign-in")

    # Substitite with Username and Password
    uname.send_keys(username)
    pword.send_keys(password)
    # Submit
    button.click()

def checkSignIn():
    try:
        attByClass = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "attByClass"))
        )
    except:
        print("login failed")
        return False
    return True    

def getCorrectCourseLink(course, mp):
    driver.get("https://spprep.powerschool.com/public")
    WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//*[@id='quickLookup']/table[1]")))
    balls = 0
    table = driver.find_element(By.XPATH, "//*[@id='quickLookup']/table[1]")
    for row in table.find_elements(By.XPATH, ".//tr"):
        if(balls == 0 or balls == 1):
            balls += 1
            continue
        print(row.id)
        if(course in row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower()):
            print("found it!")
            course_id = row.get_attribute("id")
            if(mp == "Q1"):
                xpath = "//*[@id='" + course_id + "']/td[13]/a"
                quarter_link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                return quarter_link
            if(mp == "Q2"):
                xpath = "//*[@id='" + course_id + "']/td[14]/a"
                quarter_link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                return quarter_link
            if(mp == "S1"):
                xpath = "//*[@id='" + course_id + "']/td[16]/a"
                quarter_link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                return quarter_link
            if(mp == "Q3"):
                xpath = "//*[@id='" + course_id + "']/td[17]/a"
                quarter_link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                return quarter_link
            if(mp == "Q4"):
                xpath = "//*[@id='" + course_id + "']/td[18]/a"
                quarter_link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                return quarter_link
            if(mp == "S2"):
                xpath = "//*[@id='" + course_id + "']/td[20]/a"
                quarter_link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                return quarter_link
            break
    return balls

def getCourseList():
    ogcourses = []
    courselist = []
    skip = 0
    table = driver.find_element(By.XPATH, "//*[@id='quickLookup']/table[1]")
    for row in table.find_elements(By.XPATH, ".//tr"):
        if(skip == 0 or skip == 1):
            skip += 1
            continue
        #print(row.id)
        try:
            if (row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower().__contains__("guidance")
                 or row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower().__contains__("physical education")
                 or row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower().__contains__("band")):
                continue
            else:
                ogcourses.append(row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower())
        except:
            continue
    for course in ogcourses:
        course = course[:course.find(" \n")]
        courselist.append(course)
        print(course)
    return courselist

def getQuarterAssignmentInfo(link):
    categories = []
    names = []
    score_numers = []
    score_denoms = []
    current = 0

    driver.get(link)
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[@id='scoreTable']/tbody")))
    table = driver.find_element(By.XPATH, "//*[@id='scoreTable']/tbody")
    for row in table.find_elements(By.XPATH, ".//tr"):
        row_id = row.get_attribute("id")
        category_location = "//*[@id='" + row_id + "']/td[2]/span[2]"
        name_location = "//*[@id='" + row_id + "']/td[3]/span"
        score_location = "//*[@id='" + row_id + "']/td[11]/span"
        try:
            category = row.find_element(By.XPATH, category_location).text.lower()
            name = row.find_element(By.XPATH, name_location).text.lower()
            score = row.find_element(By.XPATH, score_location).text.lower()
            score_numer = score[:score.find("/")]
            score_denom = score[score.find("/")+1:]
            categories.insert(current, category)
            names.insert(current, name)
            score_numers.insert(current, score_numer)
            score_denoms.insert(current, score_denom)
        except:
            continue
    assignmentInfoList = [categories, names, score_numers, score_denoms]
    return assignmentInfoList


# login_url = "https://spprep.powerschool.com/public/"
# username = input("username: ")
# password = input("password: ")
# course = input("course: ")
# quarter = input("quarter: ")



# signIn(username, password)
# iterateForCourse(course)
