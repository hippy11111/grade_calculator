# webscraping.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------- Driver -------------------
def createDriver():
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

# ------------------- Login -------------------
def signIn(driver, username, password):
    driver.get("https://spprep.powerschool.com/public")
    uname = driver.find_element(By.NAME, value="account")
    pword = driver.find_element(By.NAME, value="pw")
    button = driver.find_element(By.ID, value="btn-enter-sign-in")

    uname.send_keys(username)
    pword.send_keys(password)
    button.click()

def checkSignIn(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "attByClass"))
        )
    except:
        return False
    return True

# ------------------- Courses -------------------
def getCourseList(driver):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='quickLookup']/table[1]"))
    )
    table = driver.find_element(By.XPATH, "//*[@id='quickLookup']/table[1]")
    courses = []
    skip = 0
    for row in table.find_elements(By.XPATH, ".//tr"):
        if skip < 2:  # skip header rows
            skip += 1
            continue
        try:
            text = row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower()
            if any(x in text for x in ["guidance", "physical education", "band"]):
                continue
            courses.append(text.split(" \n")[0])
        except:
            continue
    return courses

def getCorrectCourseLink(driver, course, mp):
    driver.get("https://spprep.powerschool.com/public")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='quickLookup']/table[1]"))
    )
    table = driver.find_element(By.XPATH, "//*[@id='quickLookup']/table[1]")

    for row in table.find_elements(By.XPATH, ".//tr")[2:]:  # skip headers
        try:
            row_text = row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower()
            if course in row_text:
                course_id = row.get_attribute("id")
                mp_column = {
                    "Q1": 13, "Q2": 14, "S1": 16, "Q3": 17, "Q4": 18, "S2": 20
                }.get(mp)
                if mp_column:
                    xpath = f"//*[@id='{course_id}']/td[{mp_column}]/a"
                    return driver.find_element(By.XPATH, xpath).get_attribute("href")
        except:
            continue
    return None

# ------------------- Assignments -------------------
def getQuarterAssignmentInfo(driver, link):
    driver.get(link)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='scoreTable']/tbody"))
    )
    table = driver.find_element(By.XPATH, "//*[@id='scoreTable']/tbody")

    categories, names, numerators, denominators = [], [], [], []

    for row in table.find_elements(By.XPATH, ".//tr"):
        row_id = row.get_attribute("id")
        try:
            category = row.find_element(By.XPATH, f"//*[@id='{row_id}']/td[2]/span[2]").text.lower()
            name = row.find_element(By.XPATH, f"//*[@id='{row_id}']/td[3]/span").text.lower()
            score = row.find_element(By.XPATH, f"//*[@id='{row_id}']/td[11]/span").text
            num, denom = score.split("/")
            categories.append(category)
            names.append(name)
            numerators.append(num.strip())
            denominators.append(denom.strip())
        except:
            continue

    return [categories, names, numerators, denominators]
