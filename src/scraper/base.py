import time
from typing import Optional
import undetected_chromedriver as uc

from src.config.settings import scraper_config


class BaseScraper:
    """Base class for all job scrapers."""
    
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None

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