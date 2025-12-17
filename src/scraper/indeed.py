import time
from typing import List, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from src.config.settings import scraper_config
from src.scraper.parser import ParsedJob, parse_location, parse_post_date, extract_skills


class IndeedScraper:
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None
        self.base_url = "https://www.indeed.com/jobs"

    def _init_driver(self) -> None:
        options = uc.ChromeOptions()
        if scraper_config.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        self.driver = uc.Chrome(options=options)
        self.driver.set_page_load_timeout(scraper_config.page_load_timeout)

    def _close_driver(self) -> None:
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_jobs(self, keywords: str, location: str = "United States") -> List[ParsedJob]:
        """Scrape Indeed job listings."""
        jobs = []
        
        try:
            self._init_driver()
            
            url = f"{self.base_url}?q={keywords.replace(' ', '+')}&l={location.replace(' ', '+')}"
            self.driver.get(url)
            time.sleep(3)
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
            
            for i, card in enumerate(job_cards[:scraper_config.max_jobs]):
                try:
                    job = self._parse_job_card(card, i)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
                    
        except Exception as e:
            print(f"Scraping error: {e}")
        finally:
            self._close_driver()
        
        return jobs

    def _parse_job_card(self, card, index: int) -> Optional[ParsedJob]:
        """Parse a single Indeed job card."""
        try:
            # Title
            title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
            title = title_elem.text.strip()
            
            # Company
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
                company = company_elem.text.strip()
            except NoSuchElementException:
                company = "Unknown"
            
            # Location
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']")
                location_str = location_elem.text.strip()
            except NoSuchElementException:
                location_str = "Unknown"
            
            # Click to get description
            description = self._get_description(card)
            
            city, state, country = parse_location(location_str)
            post_date = None  # Indeed doesn't show date reliably on cards
            skills = extract_skills(description)
            
            return ParsedJob(
                title=title,
                company=company,
                city=city,
                state=state,
                country=country,
                description=description,
                skills=skills,
                post_date=post_date
            )
        except Exception as e:
            print(f"Parse error: {e}")
            return None

    def _get_description(self, card) -> str:
        """Click job card and extract description from side panel."""
        try:
            # Click the job title link
            title_link = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
            title_link.click()
            time.sleep(1.5)
            
            # Wait for side panel description
            try:
                desc_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#jobDescriptionText"))
                )
                return desc_elem.text.strip()
            except TimeoutException:
                return ""
                
        except Exception as e:
            print(f"Error getting description: {e}")
            return ""