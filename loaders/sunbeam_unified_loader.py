from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from utils.chunking import manual_chunk_text
from utils.driver_factory import get_driver

from scrapers.about_scraper import AboutTools
from scrapers.internship_scraper import scrape_sunbeam_full
from scrapers.courses_scraper import course_tool


class SunbeamUnifiedLazyLoader(BaseLoader):
    """
    About → Internship → Courses
    """

    def lazy_load(self):

        # -------- ABOUT --------
        driver = get_driver()
        about = AboutTools().scrape_sunbeam_about(driver)
        driver.quit()

        text = "\n".join(about.get("about_paragraphs", []))
        for i, chunk in enumerate(manual_chunk_text(text), 1):
            yield Document(
                page_content=chunk,
                metadata={
                    "source": "sunbeam",
                    "page": "about",
                    "chunk": i
                }
            )

        # -------- INTERNSHIP --------
        internship = scrape_sunbeam_full.invoke(
            {"url": "https://www.sunbeaminfo.in/internship"}
        )

        for title, content in internship.get("sections", {}).items():
            for i, chunk in enumerate(manual_chunk_text(content), 1):
                yield Document(
                    page_content=f"{title}\n{chunk}",
                    metadata={
                        "source": "sunbeam",
                        "page": "internship",
                        "section": title,
                        "chunk": i
                    }
                )

        for row in internship.get("Available Internship", []):
            yield Document(
                page_content="\n".join(f"{k}: {v}" for k, v in row.items()),
                metadata={
                    "source": "sunbeam",
                    "page": "internship",
                    "type": "available"
                }
            )

        # -------- COURSES --------
        driver = get_driver()
        tool = course_tool()
        courses = tool.scrape_courses(
            driver,
            "https://www.sunbeaminfo.in/modular-courses-home"
        )["courses"]
        driver.quit()

        for course in courses:
            driver = get_driver()
            data = tool.scrape_modular_courses(driver, course)
            driver.quit()

            for sec, content in data.get("course_context", {}).items():
                if isinstance(content, list):
                    content = "\n".join(content)

                for i, chunk in enumerate(manual_chunk_text(content), 1):
                    yield Document(
                        page_content=chunk,
                        metadata={
                            "source": "sunbeam",
                            "page": "course",
                            "course": data["course_name"],
                            "section": sec,
                            "chunk": i
                        }
                    )