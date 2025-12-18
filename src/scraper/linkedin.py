import time
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.config.settings import scraper_config
from src.scraper.base import BaseScraper
from src.scraper.parser import ParsedJob, parse_location, parse_post_date


class LinkedInScraper(BaseScraper):
    
    def scrape_jobs(self, keywords: str, location: str = "United States") -> List[ParsedJob]:
        """Scrape LinkedIn job listings."""
        jobs = []
        
        try:
            self._init_driver()
            
            url = f"{scraper_config.base_url}?keywords={keywords}&location={location}"
            self.driver.get(url)
            time.sleep(3)
            
            self._scroll_page()
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".base-card")
            
            for card in job_cards[:scraper_config.max_jobs]:
                try:
                    job = self._parse_job_card(card)
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

    def _scroll_page(self, scrolls: int = 3) -> None:
        """Scroll page to load more jobs."""
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    def _parse_job_card(self, card) -> Optional[ParsedJob]:
        """Parse a single job card element."""
        try:
            title = card.find_element(By.CSS_SELECTOR, ".base-search-card__title").text.strip()
            company = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle").text.strip()
            location_str = card.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
            
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, "time")
                date_str = date_elem.get_attribute("datetime") or date_elem.text
            except NoSuchElementException:
                date_str = ""
            
            city, state, country = parse_location(location_str)
            post_date = parse_post_date(date_str)
            
            return ParsedJob(
                title=title,
                company=company,
                city=city,
                state=state,
                country=country,
                description="",
                skills=[],
                post_date=post_date
            )
        except Exception as e:
            print(f"Parse error: {e}")
            return None