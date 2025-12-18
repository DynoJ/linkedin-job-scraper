from src.db.repository import (
    Company, Location, Skill, Job,
    CompanyRepository, LocationRepository, SkillRepository, JobRepository
)
from src.scraper.linkedin import LinkedInScraper
from src.scraper.indeed import IndeedScraper
from src.scraper.glassdoor import GlassdoorScraper


SCRAPERS = {
    'linkedin': LinkedInScraper,
    'indeed': IndeedScraper,
    'glassdoor': GlassdoorScraper,
    'all': None  # Special case
}


def save_job(parsed_job) -> bool:
    """Save a parsed job to the database. Returns True if successful."""
    if not parsed_job.title or not parsed_job.company:
        print(f"  Skipped: missing title or company")
        return False
    
    try:
        company = Company(name=parsed_job.company)
        company_id = CompanyRepository.get_or_create(company)
        
        loc = Location(
            city=parsed_job.city,
            state=parsed_job.state,
            country=parsed_job.country
        )
        location_id = LocationRepository.get_or_create(loc)
        
        job = Job(
            title=parsed_job.title,
            company_id=company_id,
            location_id=location_id,
            description=parsed_job.description,
            post_date=parsed_job.post_date
        )
        job_id = JobRepository.insert(job)
        
        for skill_name in parsed_job.skills:
            skill = Skill(skill_name=skill_name)
            skill_id = SkillRepository.get_or_create(skill)
            JobRepository.add_skill(job_id, skill_id)
        
        print(f"  Saved: {parsed_job.title} at {parsed_job.company}")
        return True
    except Exception as e:
        print(f"  Error saving job: {e}")
        return False


def run_scraper(source: str = "all", keywords: str = "software engineer", location: str = "United States"):
    """Main entry point - scrape jobs and save to database."""
    
    if source == "all":
        sources = ['linkedin', 'indeed', 'glassdoor']
    else:
        sources = [source]
    
    total_saved = 0
    
    for src in sources:
        print(f"\n{'='*50}")
        print(f"Scraping {src.upper()} for: {keywords} in {location}")
        print('='*50)
        
        scraper_class = SCRAPERS[src]
        scraper = scraper_class()
        jobs = scraper.scrape_jobs(keywords, location)
        
        print(f"Found {len(jobs)} jobs")
        
        saved = sum(1 for job in jobs if save_job(job))
        total_saved += saved
        
        print(f"Saved {saved} jobs from {src}")
    
    print(f"\n{'='*50}")
    print(f"TOTAL: Saved {total_saved} jobs to database.")
    print('='*50)


def view_jobs():
    """Display all saved jobs."""
    jobs = JobRepository.get_all_with_details()
    for job in jobs:
        skills = job.get('skills', [])
        desc_len = len(job.get('description', '') or '')
        print(f"{job['title']} | {job['company']} | {job['city']}, {job['state']}")
        print(f"  Description: {desc_len} chars | Skills: {skills}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        view_jobs()
    elif len(sys.argv) > 1 and sys.argv[1] in SCRAPERS:
        source = sys.argv[1]
        keywords = sys.argv[2] if len(sys.argv) > 2 else "software engineer"
        run_scraper(source, keywords)
    else:
        keywords = sys.argv[1] if len(sys.argv) > 1 else "software engineer"
        run_scraper("all", keywords)