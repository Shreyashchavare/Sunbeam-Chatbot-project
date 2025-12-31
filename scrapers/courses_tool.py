from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import json
import time
class course_tool:
    def scrape_courses(self, driver, URL):
        try:
            
            # driver = webdriver.Chrome()
            driver.get(URL)

            if driver.current_url.startswith(URL):
                print("✅ Page opened successfully")
            else:
                print("❌ Failed to open page")

            course_boxes = driver.find_elements(
                By.CSS_SELECTOR, "div.c_cat_box.gr_box"
            )
             
            courses = []

            for box in course_boxes:
                try:
                    name = box.find_element(
                        By.CSS_SELECTOR, "div.c_info h4"
                    ).text.strip()

                    link = box.find_element(
                        By.CSS_SELECTOR, "a.c_cat_more_btn"
                    ).get_attribute("href")

                    if name and link:
                        courses.append({
                            "course_name": name,
                            "course_url": link
                        })

                except Exception:
                    continue

            return {
                "total_courses": len(courses),
                "courses": courses
            }
        except Exception as e:
            print(e)

    def scrape_modular_courses(self, driver, course):
     
        wait = WebDriverWait(driver, 20)

        course_name = course["course_name"]
        course_url = course["course_url"]

        driver.get(course_url)

        if not driver.current_url.startswith(course_url):
            print(f"❌ Failed to open page: {course_name}")
            return None

        print(f"✅ Page opened successfully: {course_name}")

        # ===============================
        # COURSE INFO
        # ===============================
        course_info_div = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.course_info"))
        )

        course_info = {}

        title = course_info_div.find_element(
            By.TAG_NAME, "h3"
        ).get_attribute("innerText")

        course_info["course_name"] = title.split(":", 1)[1].strip()

        paragraphs = course_info_div.find_elements(By.TAG_NAME, "p")
        for p in paragraphs:
            text = p.get_attribute("innerText").strip()
            if ":" in text:
                key, value = text.split(":", 1)
                course_info[key.strip().lower().replace(" ", "_")] = value.strip()

        # ===============================
        # ACCORDIONS (STRUCTURE BASED)
        # ===============================
        accordions = {}
        tables = {}

        # IMPORTANT: wait for panel bodies, not accordion container
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.course_info h3")
            )
        )


        panels = driver.find_elements(
            By.CSS_SELECTOR, "div.panel.panel-default"
        )
        for panel in panels:
            try:
                # ----------------------------
                # SECTION TITLE
                # ----------------------------
                title_el = panel.find_element(By.CSS_SELECTOR, "h4.panel-title")
                section_title = (
                    title_el.text.replace(":", "")
                    .strip()
                    .lower()
                    .replace(" ", "_")
                )

                # # ----------------------------
                # # TOGGLE (OPEN IF CLOSED)
                # # ----------------------------
                toggle = title_el.find_element(By.TAG_NAME, "a")
                
                if toggle.get_attribute("aria-expanded") == "false":
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", toggle)
                    toggle.click()

                    
                    wait.until(
                        EC.visibility_of(
                            panel.find_element(By.CSS_SELECTOR, "div.panel-body")
                        )
                    )
                # ----------------------------
                # PANEL BODY
                # ----------------------------
                collapse_div = panel.find_element(By.CSS_SELECTOR, "div.panel-collapse")
                body = collapse_div.find_element(By.CSS_SELECTOR, "div.panel-body")


                # ----------------------------
                # TABLE OR TEXT
                # ----------------------------
                # ---------- TABLE ----------
                table_elements = body.find_elements(By.TAG_NAME, "table")

                if table_elements:
                    table = table_elements[0]

                    headers = [
                        th.text.strip().lower().replace(" ", "_")
                        for th in table.find_elements(By.TAG_NAME, "th")
                        if th.text.strip()
                    ]

                    rows_data = []
                    rows = table.find_elements(By.TAG_NAME, "tr")[1:]

                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if len(cols) == len(headers):
                            rows_data.append({
                                headers[i]: cols[i].text.strip()
                                for i in range(len(headers))
                            })

                    if rows_data:
                        tables[section_title] = rows_data

                # ---------- LIST ITEMS ----------
                else:
                    list_items = body.find_elements(By.CSS_SELECTOR, "ul li")

                    if list_items:
                        accordions[section_title] = [
                            li.get_attribute("innerText").strip()
                            for li in list_items
                            if li.get_attribute("innerText").strip()
                        ]


                    else:
                        text = body.get_attribute("innerText").strip()
                        if text:
                            accordions[section_title] = text

            except Exception as e:
                print(f"⚠️ Skipped section due to error: {e}")
                continue

        return {
            "course_name": course_name,
            "course_info": course_info,
            "course_context": accordions,
            "tables": tables
        } 


if __name__ == "__main__":

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2
    }
    options.add_experimental_option("prefs", prefs)

    SERVICE = Service(ChromeDriverManager().install())

    # ---- 1. Get course list ----
    driver = webdriver.Chrome(service=SERVICE, options=options)
    tool = course_tool()
    data = tool.scrape_courses(
        driver,
        "https://www.sunbeaminfo.in/modular-courses-home"
    )
    driver.quit()

    courses = data["courses"]

    # ---- 2. Scrape courses one-by-one ----
    results = []

    for course in courses:
        driver = webdriver.Chrome(service=SERVICE, options=options)
        try:
            result = tool.scrape_modular_courses(driver, course)
            results.append(result)
        finally:
            driver.quit()
    for result in results:
        print(result)
        print("\n\n\n\n")