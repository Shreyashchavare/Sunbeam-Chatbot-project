# loaders/sunbeam_unified_loader.py

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from utils.chunking import manual_chunk_text
from utils.driver_factory import get_driver

from scrapers.about_scraper import AboutTools
from scrapers.internship_scraper import scrape_sunbeam_full
from scrapers.courses_scraper import course_tool


class SunbeamUnifiedLazyLoader(BaseLoader):
    """
    ONE lazy loader:
    About → Internship → Courses
    """

    def __init__(self):
        self.about_url = "https://www.sunbeaminfo.in/about-us"
        self.internship_url = "https://www.sunbeaminfo.in/internship"
        self.courses_url = "https://www.sunbeaminfo.in/modular-courses-home"

    def lazy_load(self):
        # -----------------------------
        # 1️⃣ ABOUT PAGE
        # -----------------------------
        driver = get_driver()
        about_tool = AboutTools()
        about_data = about_tool.scrape_sunbeam_about(driver)
        driver.quit()

        text = "\n".join(about_data.get("about_paragraphs", []))
        for i, chunk in enumerate(manual_chunk_text(text), start=1):
            yield Document(
                page_content=chunk,
                metadata={
                    "source": "sunbeam",
                    "page": "about",
                    "chunk_id": i
                }
            )

        # -----------------------------
        # 2️⃣ INTERNSHIP PAGE
        # -----------------------------
        internship_data = scrape_sunbeam_full.invoke(
            {"url": self.internship_url}
        )

        for title, content in internship_data.get("sections", {}).items():
            for i, chunk in enumerate(manual_chunk_text(content), start=1):
                yield Document(
                    page_content=f"{title}\n{chunk}",
                    metadata={
                        "source": "sunbeam",
                        "page": "internship",
                        "section": title,
                        "chunk_id": i
                    }
                )

        for internship in internship_data.get("Available Internship", []):
            text = "\n".join([f"{k}: {v}" for k, v in internship.items()])
            yield Document(
                page_content=text,
                metadata={
                    "source": "sunbeam",
                    "page": "internship",
                    "type": "available_internship",
                    "technology": internship.get("Technology")
                }
            )

        # -----------------------------
        # 3️⃣ COURSES
        # -----------------------------
        driver = get_driver()
        course_scraper = course_tool()

        course_list = course_scraper.scrape_courses(
            driver,
            self.courses_url
        )["courses"]
        driver.quit()

        for course in course_list:
            driver = get_driver()
            course_data = course_scraper.scrape_modular_courses(
                driver,
                course
            )
            driver.quit()

            course_name = course_data.get("course_name")

            for section, content in course_data.get("course_context", {}).items():
                if isinstance(content, list):
                    content = "\n".join(content)

                for i, chunk in enumerate(manual_chunk_text(content), start=1):
                    yield Document(
                        page_content=chunk,
                        metadata={
                            "source": "sunbeam",
                            "page": "course",
                            "course": course_name,
                            "section": section,
                            "chunk_id": i
                        }
                    )
