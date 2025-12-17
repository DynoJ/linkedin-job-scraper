import time
from typing import List, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from src.config.settings import scraper_config
from src.scraper.parser import ParsedJob, parse_location, extract_skills


class GlassdoorScraper:
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None
        self.base_url = "https://www.glassdoor.com/Job"

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
        """Scrape Glassdoor job listings."""
        jobs = []
        
        try:
            self._init_driver()
            
            keyword_slug = keywords.lower().replace(' ', '-')
            url = f"{self.base_url}/{keyword_slug}-jobs-SRCH_KO0,{len(keywords)}.htm"
            self.driver.get(url)
            time.sleep(3)
            
            self._close_modals()
            time.sleep(1)
            self._close_modals()
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="jobListing"]')
            
            for card in job_cards[:scraper_config.max_jobs]:
                try:
                    self._close_modals()
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

    def _close_modals(self) -> None:
        """Close any popup modals."""
        try:
            close_selectors = [
                '[aria-label="Close"]',
                'button[class*="CloseButton"]',
                '[data-test="close-button"]',
                '.modal-close',
                'dialog button'
            ]
            
            for selector in close_selectors:
                try:
                    btns = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in btns:
                        try:
                            btn.click()
                            time.sleep(0.3)
                        except:
                            pass
                except:
                    pass
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(0.3)
            except:
                pass
            
            self.driver.execute_script("""
                document.querySelectorAll('dialog, [class*="Modal"]').forEach(el => el.remove());
                document.querySelectorAll('[class*="Overlay"]').forEach(el => el.remove());
            """)
            time.sleep(0.3)
            
        except:
            pass

    def _parse_job_card(self, card) -> Optional[ParsedJob]:
        """Parse a single Glassdoor job card."""
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, '[data-test="job-title"]')
            title = title_elem.text.strip()
            
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, '[class*="EmployerProfile_compactEmployerName"]')
                company = company_elem.text.strip()
            except NoSuchElementException:
                company = "Unknown"
            
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, '[data-test="emp-location"]')
                location_str = location_elem.text.strip()
            except NoSuchElementException:
                location_str = "Unknown"
            
            description = self._get_description(card)
            
            city, state, country = parse_location(location_str)
            skills = extract_skills(description)
            
            return ParsedJob(
                title=title,
                company=company,
                city=city,
                state=state,
                country=country,
                description=description,
                skills=skills,
                post_date=None
            )
        except Exception as e:
            print(f"Parse error: {e}")
            return None

    def _get_description(self, card) -> str:
        """Click job card and extract description."""
        try:
            # Scroll card into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            time.sleep(0.5)
            
            # Use JavaScript click
            self.driver.execute_script("arguments[0].click();", card)
            time.sleep(1.5)
            
            self._close_modals()
            
            try:
                desc_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="JobDetails_jobDescription"]'))
                )
                return desc_elem.text.strip()
            except TimeoutException:
                return ""
                
        except Exception as e:
            print(f"Error getting description: {e}")
            return ""