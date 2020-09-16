from urllib import request
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import os

if os.path.exists("asu_database.csv"):
    db = pd.read_csv("asu_database.csv")
else:
    db = pd.DataFrame(columns=["name", "email", "job", "department", "majors", "careers", "programs"])

driver = webdriver.Chrome()

html = driver.page_source

alphabet = "abcdefghijklmnopqrstuvwxyz"

start = "a,a,0"

if os.path.exists("last_search.txt"):
    with open("last_search.txt", "r") as last_search:
        start = last_search.readline()

start = start.split(",")
first = True


url = "https://isearch.asu.edu/asu-students/q=aa&fq=affiliations:Student"
driver.get(url)
driver.find_element_by_name("username").send_keys("XXXX")
driver.find_element_by_id("password").send_keys('XXXX')
driver.find_element_by_name("submit").click()

for c1 in alphabet[alphabet.index(start[0]):]:
    c2_alpha = alphabet[alphabet.index(start[1]):] if first else alphabet
    for c2 in c2_alpha:
        page_index = int(start[2]) if first else 0
        first=False
        while True:
            url = "https://isearch.asu.edu/asu-students/q=" + c1 + c2 + "&start=" + str(page_index) + "&fq=affiliations:Student"
            try:
                driver.get(url)
                connected = True
            except:
                print("Failed to connect")
                print("Running new instance")
                os.system("C:/Users/srspo/AppData/Local/Programs/Python/Python35/python.exe c:/Users/srspo/Dropbox/PogramingProjects/asu_scraper/asu_scraper.py")
                exit()

            soup = BeautifulSoup(driver.page_source, features="html.parser")

            results = soup.find_all("div", class_="row row-header asu_directory_people_row asu_people_row_even")
            results.extend(soup.find_all("div", class_="row row-header asu_directory_people_row asu_people_row_odd"))
            if len(results) == 0:
                break

            for result in results:
                row = {}

                name_tags = result.find_all("a", class_="displayName viewDetails")
                row["name"] = ", ".join([tag.text for tag in name_tags])

                job_tags = result.find_all("div", class_="job-title")
                row["job"] = ", ".join([tag.text for tag in job_tags])

                dept_tags = result.find_all("div", class_="dept")
                row["department"] = ", ".join([tag.text for tag in dept_tags])

                careers_tags = result.find_all("span", class_="careers")
                row["careers"] = ", ".join([tag.text for tag in careers_tags])

                majors_tags = result.find_all("span", class_="majors")
                row["majors"] = ", ".join([tag.text for tag in majors_tags])

                programs_tags = result.find_all("span", class_="programs")
                row["programs"] = ",".join([tag.text for tag in programs_tags])

                email_tags = result.find_all("a", class_="emailAddress")
                row["email"] = ", ".join([tag.text for tag in email_tags])

                db = db.append(row, ignore_index=True)
            page_index += 10
            db.to_csv("asu_database.csv", index=False)
            with open("last_search.txt", "w") as last_search:
                last_search.write(",".join([c1, c2, str(page_index)]))
            print("Collected", len(db), "profiles")
    driver.quit()


