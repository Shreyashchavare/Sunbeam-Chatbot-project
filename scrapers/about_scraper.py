import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class AboutTools:
    def __init__(self):
        self.about_url = "https://www.sunbeaminfo.in/about-us"

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def scrape_sunbeam_about(self, driver):
        driver.get(self.about_url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page_title = driver.title

        about_paragraphs = []
        paragraphs = driver.find_elements(
            By.CSS_SELECTOR,
            "div.container div.row div[class*='col'] p"
        )

        for p in paragraphs:
            text = p.text.strip()

            if (
                len(text) < 60
                or "©" in text
                or "MH-INDIA" in text
                or "Pune -" in text
                or "Sunbeam Chambers" in text
                or "Sunbeam IT Park" in text
            ):
                continue

            about_paragraphs.append(text)

        sub_sections = []
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")

        for h in headings:
            txt = h.text.strip()
            if txt and txt.upper() not in [
                "REGISTRATION",
                "ONLINE ADMISSION",
                "CONTACT US",
                "&"
            ]:
                sub_sections.append(txt)

        return {
            "page_title": page_title,
            "heading": "ABOUT US",
            "about_paragraphs": about_paragraphs,
            "sub_sections": list(dict.fromkeys(sub_sections))
        }


if __name__ == "__main__":
    tool = AboutTools()
    driver = tool.setup_driver()

    about_data = tool.scrape_sunbeam_about(driver)
    driver.quit()

    final_result = {
        "source": "Sunbeam Institute",
        "about_sunbeam": about_data
    }

    print(json.dumps(final_result, indent=4, ensure_ascii=False))