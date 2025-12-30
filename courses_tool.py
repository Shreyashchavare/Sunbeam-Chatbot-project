from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class course_tool:
    def __init__(self):
        self.__url = "https://www.sunbeaminfo.in/"
    
    def _hover_courses_menu(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        driver = webdriver.Chrome(
            service= Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(self.__url)


        wait = WebDriverWait(driver, 15)

        # wait for and click the "Available Internship Programs" toggle button
        course_menu = wait.until(
            EC.visibility_of_element_located((By.LINK_TEXT, "COURSES"))
        )
        # print("Hovered on COURSES")
        # print(course_menu.text)
        ActionChains(driver)\
        .move_to_element(course_menu)\
        .pause(2)\
        .perform()

        dropdown = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu"))
        )
        # print("Dropdown element found in DOM")

        
        # print("Dropdown is visible")
        # print(dropdown.get_attribute("class"))
        return driver
    
    def _extract_course_links(self,driver):
        courses_data = {}
        menu_boxes = driver.find_elements(By.CSS_SELECTOR, "div.inner_menu_box")
        # print("Number of menu boxes:", len(menu_boxes))
        
        # print("\nCategories found:\n")
        for box in menu_boxes:
            headings = box.find_elements(By.TAG_NAME, "h4")
            lists = box.find_elements(By.TAG_NAME, "ul")

            # Safety check
            if len(headings) != len(lists):
                # print("⚠️ Heading–list count mismatch, skipping this box")
                continue
            count = min(len(headings), len(lists))
            for i in range(count):
                category = headings[i].text.strip()
                # print(f"\nCategory: {category}")

                if not category:
                    continue

                if category not in courses_data:
                    courses_data[category] = {}

                links = lists[i].find_elements(By.TAG_NAME, "a")

                for link in links:
                    course_name = link.text.strip()
                    course_url = link.get_attribute("href")

                    if not course_name or not course_url:
                        continue

                    # Avoid accidental overwrites
                    if course_name in courses_data[category]:
                        continue

                    courses_data[category][course_name] = course_url       
                    
        return courses_data

    def scrape(self):
        """
        Public entry point.
        Returns all course categories with course links.
        """
        driver = None
        try:
            driver = self._hover_courses_menu()
            courses = self._extract_course_links(driver)
            return courses
        finally:
            if driver:
                driver.quit()


if __name__ == "__main__":
    tool = course_tool()
    data = tool.scrape()

    for category, courses in data.items():
        print(f"\n{category}")
        for name, url in courses.items():
            print(f"  - {name} → {url}")