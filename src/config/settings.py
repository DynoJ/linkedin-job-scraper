import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OracleConfig:
    host: str = os.getenv("ORACLE_HOST", "localhost")
    port: int = int(os.getenv("ORACLE_PORT", "1521"))
    service: str = os.getenv("ORACLE_SERVICE", "ORCLPDB1")
    user: str = os.getenv("ORACLE_USER", "system")
    password: str = os.getenv("ORACLE_PWD", "")

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service}"


@dataclass
class ScraperConfig:
    base_url: str = "https://www.linkedin.com/jobs/search"
    headless: bool = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
    page_load_timeout: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    max_jobs: int = int(os.getenv("MAX_JOBS", "50"))


oracle_config = OracleConfig()
scraper_config = ScraperConfig()