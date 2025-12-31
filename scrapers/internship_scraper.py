import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from langchain.tools import tool

@tool
def scrape_sunbeam_full(url: str) -> dict:
    """
    Scrapes the Sunbeam internship page for:
    - Text sections
    - Benefits Of Program
    - Our Associates
    - Available Internship Programs table
    - Internship Table
    Returns structured JSON.
    """

    #  CHROME OPTIONS (CRITICAL)
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")

    #  prevent renderer timeout
    options.page_load_strategy = "none"

    # Disable images for faster load
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.set_page_load_timeout(120)
    wait = WebDriverWait(driver, 30)

    # SAFE PAGE LOAD
    driver.get(url)

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # DATA CONTAINER
    data = {
        "source": url,
        "scraped_at": datetime.now().isoformat()
    }

    # 1️ SCRAPE ALL TEXT SECTIONS
    try:
        left_container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".col-xs-12.col-sm-7.col-md-8")
            )
        )

        sections = left_container.find_elements(By.CSS_SELECTOR, ".main_info")
        structured_sections = {}

        for section in sections:
            try:
                heading = section.find_element(By.TAG_NAME, "h2").text.strip()
                content = section.text.replace(heading, "").strip()
                structured_sections[heading] = content
            except:
                continue

        data["sections"] = structured_sections
    except:
        data["sections"] = {}



    # 2.student industrial training and internship
    try:
        # Click accordion
        accordion = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(.,'Student Industrial Training')]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", accordion)
        accordion.click()

        # Get expanded panel
        panel = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'panel-collapse') and contains(@class,'in')]"
            ))
        )

        # Extract description text
        paragraphs = panel.find_elements(By.TAG_NAME, "p")
        description = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])

        #data["Student Industrial Training & Internship"] = description

        # Extract internship table
        table = panel.find_element(By.TAG_NAME, "table")

        headers = [
            th.text.strip()
            for th in table.find_elements(By.XPATH, ".//thead//th")
        ]
        rows = table.find_elements(By.XPATH, ".//tbody//tr")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) != len(headers):
                continue
            row_data = {
                headers[i]: cells[i].text.strip()
                for i in range(len(headers))
            }
        data["student industrial training and internship"] = row_data
    except Exception as e:
        print("Scraping failed:", e)
        data["student industrial training and internship"] = []

    
    # 3.Traning and industrial program feature
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    try:
        #Click accordion
        accordion_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(.,'Training And Industrial Program Features')]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", accordion_btn)
        accordion_btn.click()

        # Wait for expanded panel
        panel = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'panel-collapse') and contains(@class,'in')]"
            ))
        )

        # Each feature row 
        items = panel.find_elements(By.XPATH, ".//p | .//li")

        for item in items:
            text = item.text.strip()
            if " - " in text:
                title, description = text.split(" - ", 1)
                res = ({
                    "feature": title.strip(),
                    "description": description.strip()
                })
        data["Traning and industrial program feature"] = res

    except Exception as e:
        print("Scraping failed:", e)
        data["Traning and industrial program feature"] = []
    
    
    # 4.BENEFITS OF PROGRAM
    
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    try:
        #  Click "Benefits Of Program" accordion
        benefits_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(.,'Benefits Of Program')]"
            )))
        driver.execute_script("arguments[0].scrollIntoView(true);", benefits_btn)
        benefits_btn.click()
        # 2 Wait for expanded accordion panel
        benefits_panel = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'panel-collapse') and contains(@class,'in')]"
            )))
        #  Extract bullet points
        benefit_items = benefits_panel.find_elements(By.TAG_NAME, "li")
        benefits = [item.text.strip() for item in benefit_items if item.text.strip()]
        data["benefits_of_program"] = benefits
    except Exception as e:
        data["benefits_of_program"] = []

    # 5.OUR ASSOCIATES
    try:
        associates_section = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Our Associates')]")
            )
        )

        associates_container = associates_section.find_element(
            By.XPATH, "./ancestor::div[contains(@class,'main_info')]"
        )

        associates = [
            img.get_attribute("alt")
            for img in associates_container.find_elements(By.TAG_NAME, "img")
            if img.get_attribute("alt")
        ]

        data["our_associates"] = associates
    except:
        data["our_associates"] = []

    # 6.AVAILABLE INTERNSHIP PROGRAMS
    try:
        plus_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#collapseSix']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", plus_button)
        plus_button.click()

        t_div = driver.find_element(By.ID, "collapseSix")
        t_class = t_div.find_element(By.TAG_NAME, "table")
        t_body = t_class.find_element(By.TAG_NAME,"tbody")
        t_row = t_body.find_elements(By.TAG_NAME, "tr")

        internships = []

        for row in t_row:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 5:
                continue

            internship = {
                "Technology":cols[0].text.strip(),
                "Aim":cols[1].text.strip(),
                "Prerequisite":cols[2].text.strip(),
                "Learning":cols[3].text.strip(),
                "Location":cols[4].text.strip()
            }
            internships.append(internship)

        data["Available Internship"] = internships

    except Exception as e:
        print("Available Internship scraping failed:", e)
        data["Available Internship"] = []

    # 7.INTERNSHIP TABLE
    try:
        table_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".table-responsive"))
        )

        table = table_container.find_element(By.TAG_NAME, "table")

        headers = [
            th.text.strip()
            for th in table.find_elements(By.CSS_SELECTOR, "thead th")
        ]

        rows_data = []
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_dict = {
                headers[i]: cells[i].text.strip()
                for i in range(min(len(headers), len(cells)))
            }
            rows_data.append(row_dict)

        data["internship_table"] = rows_data
    except:
        data["internship_table"] = []
    driver.quit()
    return data
# ==================================================================================================================================================
from langchain_core.documents import Document



def sunbeam_json_to_documents(data: dict) -> list[Document]:
    """
    Converts scraped Sunbeam JSON into LangChain Documents
    with clean semantic chunking.
    """
    docs = []

    source = data.get("source", "sunbeam")

    # 🔹 1. Text Sections
    for title, content in data.get("sections", {}).items():
        docs.append(
            Document(
                page_content=f"{title}\n{content}",
                metadata={
                    "source": source,
                    "type": "section",
                    "title": title
                }
            )
        )

    # 🔹 2. Benefits of Program
    benefits = data.get("benefits_of_program")
    if benefits:
        docs.append(
            Document(
                page_content=f"Benefits Of Program\n{benefits}",
                metadata={
                    "source": source,
                    "type": "benefits"
                }
            )
        )

    # 🔹 3. Available Internship Programs (BEST chunking here)
    for internship in data.get("Available Internship", []):
        text = (
            f"Technology: {internship['Technology']}\n"
            f"Aim: {internship['Aim']}\n"
            f"Prerequisite: {internship['Prerequisite']}\n"
            f"Learning: {internship['Learning']}\n"
            f"Location: {internship['Location']}"
        )

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": source,
                    "type": "available_internship",
                    "technology": internship["Technology"],
                    "location": internship["Location"]
                }
            )
        )

    # 🔹 4. Internship Table
    for row in data.get("internship_table", []):
        text = "\n".join([f"{k}: {v}" for k, v in row.items()])

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": source,
                    "type": "internship_table"
                }
            )
        )

    return docs



# RUN
if __name__ == "__main__":
    URL = "https://www.sunbeaminfo.in/internship"
    result = scrape_sunbeam_full.invoke({"url": URL})
    print(json.dumps(result, indent=2, ensure_ascii=False))

    result_doc = sunbeam_json_to_documents(result)
    print(result_doc)