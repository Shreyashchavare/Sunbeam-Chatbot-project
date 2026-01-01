from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from utils.chunking import manual_chunk_text
from utils.driver_factory import get_driver

from scrapers.about_tools import AboutTools
from scrapers.internship_tool import scrape_sunbeam_full
from scrapers.courses_tool import course_tool


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

        # [CRITICAL] Index an explicit "About Summary" for "Tell me about Sunbeam" queries
        if about.get("about_paragraphs"):
            # Join ALL paragraphs to provide the full "About Us" text the user expects
            summary_text = "About Sunbeam Institute (Main Description):\n" + "\n\n".join(about["about_paragraphs"])
            yield Document(
                page_content=summary_text,
                metadata={
                    "source": "sunbeam",
                    "page": "about",
                    "section": "summary"  # Precise tag for retrieval
                }
            )

        # -------- INTERNSHIP --------
        internship = scrape_sunbeam_full(
            "https://www.sunbeaminfo.in/internship"
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

        # Helper to extract technologies for summary
        internship_list = []
        for row in internship.get("Available Internship", []):
            internship_list.append(row)
            yield Document(
                page_content="\n".join(f"{k}: {v}" for k, v in row.items()),
                metadata={
                    "source": "sunbeam",
                    "page": "internship",
                    "type": "available"
                }
            )
            
        # [CRITICAL] Index the list of internship technologies for "list" queries
        if internship_list:
            tech_names = [i.get("Technology", "Unknown") for i in internship_list]
            yield Document(
                page_content="Sunbeam Institute offers Internship Programs in the following Technologies:\n" + "\n".join(f"- {name}" for name in tech_names),
                metadata={
                    "source": "sunbeam",
                    "page": "internship",
                    "section": "internship_list"
                }
            )

        # -------- COURSES --------
        tool = course_tool()
        
        # Get list of courses
        driver = get_driver()
        try:
            courses = tool.scrape_courses(
                driver,
                "https://www.sunbeaminfo.in/modular-courses-home"
            )["courses"]
        finally:
            driver.quit()

        # [CRITICAL] Index the list of course names so the agent can "list courses"
        if courses:
            course_names = [c["course_name"] for c in courses]
            yield Document(
                page_content="Sunbeam Institute offers the following Modular Courses:\n" + "\n".join(f"- {name}" for name in course_names),
                metadata={
                    "source": "sunbeam",
                    "page": "courses",
                    "section": "course_list"
                }
            )

        # Iterate courses with a NEW single persistent driver
        # We restart the driver once to ensure a clean state before the loop
        driver = get_driver()
        
        try:
            for course in courses:
                try:
                    data = tool.scrape_modular_courses(driver, course)
                    
                    if not data:
                        continue

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
                except Exception as e:
                    print(f"Failed to scrape specific course {course.get('course_name', 'Unknown')}: {e}")
                    # Allow loop to continue
                    continue
        finally:
            # Ensure driver closes at the end of the generator
            driver.quit()

