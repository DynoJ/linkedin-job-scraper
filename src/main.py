from src.db.models import init_schema
from src.db.repository import (
    Company, Location, Skill, Job,
    CompanyRepository, LocationRepository, SkillRepository, JobRepository
)
from src.scraper.linkedin import LinkedInScraper


def run_scraper(keywords: str = "software engineer", location: str = "United States"):
    """Main entry point - scrape jobs and save to database."""
    print(f"Scraping jobs for: {keywords} in {location}")
    
    scraper = LinkedInScraper()
    jobs = scraper.scrape_jobs(keywords, location)
    
    print(f"Found {len(jobs)} jobs")
    
    saved = 0
    for parsed_job in jobs:
        # Skip jobs with missing required fields
        if not parsed_job.title or not parsed_job.company:
            print(f"  Skipped: missing title or company")
            continue
        
        try:
            # Get or create company
            company = Company(name=parsed_job.company)
            company_id = CompanyRepository.get_or_create(company)
            
            # Get or create location
            loc = Location(
                city=parsed_job.city,
                state=parsed_job.state,
                country=parsed_job.country
            )
            location_id = LocationRepository.get_or_create(loc)
            
            # Insert job
            job = Job(
                title=parsed_job.title,
                company_id=company_id,
                location_id=location_id,
                description=parsed_job.description,
                post_date=parsed_job.post_date
            )
            job_id = JobRepository.insert(job)
            
            # Add skills
            for skill_name in parsed_job.skills:
                skill = Skill(skill_name=skill_name)
                skill_id = SkillRepository.get_or_create(skill)
                JobRepository.add_skill(job_id, skill_id)
            
            print(f"  Saved: {parsed_job.title} at {parsed_job.company}")
            saved += 1
        except Exception as e:
            print(f"  Error saving job: {e}")
            continue
    
    print(f"\nDone! Saved {saved} jobs to database.")

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
    else:
        keywords = sys.argv[1] if len(sys.argv) > 1 else "software engineer"
        run_scraper(keywords)