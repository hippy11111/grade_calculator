# webscraping.py
# pip install selenium beautifulsoup4

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver():
    """Creates a headless Chrome driver for Linux (Render)."""
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    return driver

def signIn(username, password):
    driver = create_driver()
    driver.get("https://spprep.powerschool.com/public")

    uname = driver.find_element(By.NAME, "account")
    pword = driver.find_element(By.NAME, "pw")
    button = driver.find_element(By.ID, "btn-enter-sign-in")

    uname.send_keys(username)
    pword.send_keys(password)
    button.click()
    return driver  # return the driver for further use

def checkSignIn(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "attByClass"))
        )
        return True
    except:
        return False

def getCorrectCourseLink(driver, course, mp):
    driver.get("https://spprep.powerschool.com/public")
    WebDriverWait(driver, 4).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='quickLookup']/table[1]"))
    )
    table = driver.find_element(By.XPATH, "//*[@id='quickLookup']/table[1]")
    for idx, row in enumerate(table.find_elements(By.XPATH, ".//tr")):
        if idx < 2:  # skip header rows
            continue
        try:
            course_name = row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower()
            if course.lower() in course_name:
                course_id = row.get_attribute("id")
                # map quarter to table column
                mp_map = {"Q1": 13, "Q2": 14, "S1": 16, "Q3": 17, "Q4": 18, "S2": 20}
                col = mp_map.get(mp)
                if col:
                    xpath = f"//*[@id='{course_id}']/td[{col}]/a"
                    link = driver.find_element(By.XPATH, xpath).get_attribute("href")
                    return link
        except:
            continue
    return None

def getCourseList(driver):
    table = driver.find_element(By.XPATH, "//*[@id='quickLookup']/table[1]")
    courselist = []
    for idx, row in enumerate(table.find_elements(By.XPATH, ".//tr")):
        if idx < 2:
            continue
        try:
            course_name = row.find_element(By.CLASS_NAME, "table-element-text-align-start").text.lower()
            if any(skip in course_name for skip in ["guidance", "physical education", "band"]):
                continue
            courselist.append(course_name.split(" \n")[0])
        except:
            continue
    return courselist

def getQuarterAssignmentInfo(driver, link):
    driver.get(link)
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='scoreTable']/tbody"))
    )
    table = driver.find_element(By.XPATH, "//*[@id='scoreTable']/tbody")
    categories, names, score_numers, score_denoms = [], [], [], []

    for row in table.find_elements(By.XPATH, ".//tr"):
        try:
            row_id = row.get_attribute("id")
            category = row.find_element(By.XPATH, f"//*[@id='{row_id}']/td[2]/span[2]").text.lower()
            name = row.find_element(By.XPATH, f"//*[@id='{row_id}']/td[3]/span").text.lower()
            score = row.find_element(By.XPATH, f"//*[@id='{row_id}']/td[11]/span").text.lower()
            numer, denom = score.split("/")
            categories.append(category)
            names.append(name)
            score_numers.append(numer)
            score_denoms.append(denom)
        except:
            continue

    return [categories, names, score_numers, score_denoms]
