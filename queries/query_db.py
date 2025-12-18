"""
Database query tool for LinkedIn job scraper.
Interactive CLI for querying the normalized database.
"""

import logging
from src.db.connection import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QueryTool:
    def __init__(self):
        """Initialize using shared database pool."""
        logger.info("Connected to Oracle database")

    def list_tables(self):
        """List all tables in the database."""
        with Database.get_cursor() as cursor:
            cursor.execute("SELECT table_name FROM user_tables")
            tables = cursor.fetchall()
            print("\nAvailable tables:")
            for table in tables:
                print(f"  - {table[0]}")
            return tables

    def describe_table(self, table_name):
        """Describe the structure of a specific table."""
        with Database.get_cursor() as cursor:
            cursor.execute(
                "SELECT column_name, data_type FROM user_tab_columns WHERE table_name = UPPER(:1)",
                (table_name,)
            )
            columns = cursor.fetchall()
            print(f"\nTable structure for '{table_name}':")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            return columns

    def count_records(self, table_name):
        """Count the number of records in a table."""
        with Database.get_cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nRecords in '{table_name}': {count}")
            return count

    def list_jobs(self):
        """List all jobs with company and location details."""
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT j.job_id, j.title, c.name AS company_name, 
                       l.city, l.state, l.country, j.post_date
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
                JOIN locations l ON j.location_id = l.location_id
                ORDER BY j.job_id DESC
            """)
            jobs = cursor.fetchall()
            
            print("\nJobs in Database:")
            print("=" * 80)
            for job in jobs:
                location = ', '.join(filter(None, [job[3], job[4], job[5]]))
                date_str = job[6].strftime('%Y-%m-%d') if job[6] else 'N/A'
                print(f"  [{job[0]}] {job[1]} at {job[2]} ({location}) - {date_str}")
            
            return jobs

    def job_details(self, job_id):
        """Get detailed information about a specific job."""
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT j.job_id, j.title, c.name AS company_name,
                       l.city, l.state, l.country, j.description, j.post_date
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
                JOIN locations l ON j.location_id = l.location_id
                WHERE j.job_id = :1
            """, (job_id,))
            job = cursor.fetchone()
            
            if not job:
                print(f"No job found with ID {job_id}")
                return None
            
            cursor.execute("""
                SELECT s.skill_name
                FROM job_skills js
                JOIN skills s ON js.skill_id = s.skill_id
                WHERE js.job_id = :1
            """, (job_id,))
            skills = [row[0] for row in cursor.fetchall()]
            
            print("\nJob Details:")
            print("=" * 80)
            print(f"Title: {job[1]}")
            print(f"Company: {job[2]}")
            location = ', '.join(filter(None, [job[3], job[4], job[5]]))
            print(f"Location: {location}")
            print(f"Posted: {job[7]}")
            print(f"\nSkills: {', '.join(skills) if skills else 'None listed'}")
            print(f"\nDescription:\n{'-' * 40}\n{job[6] or 'No description'}")
            
            return job

    def search_by_skill(self, skill):
        """Search for jobs requiring a specific skill."""
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT j.job_id, j.title, c.name AS company_name, 
                       l.city, l.state
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
                JOIN locations l ON j.location_id = l.location_id
                JOIN job_skills js ON j.job_id = js.job_id
                JOIN skills s ON js.skill_id = s.skill_id
                WHERE UPPER(s.skill_name) LIKE UPPER(:1)
            """, (f"%{skill}%",))
            jobs = cursor.fetchall()
            
            print(f"\nJobs requiring '{skill}':")
            print("=" * 60)
            if jobs:
                for job in jobs:
                    loc = ', '.join(filter(None, [job[3], job[4]]))
                    print(f"  [{job[0]}] {job[1]} at {job[2]} ({loc})")
            else:
                print(f"  No jobs found requiring '{skill}'")
            return jobs

    def search_by_location(self, location):
        """Search for jobs in a specific location."""
        with Database.get_cursor() as cursor:
            pattern = f"%{location}%"
            cursor.execute("""
                SELECT j.job_id, j.title, c.name AS company_name, 
                       l.city, l.state
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
                JOIN locations l ON j.location_id = l.location_id
                WHERE UPPER(l.city) LIKE UPPER(:1) 
                   OR UPPER(l.state) LIKE UPPER(:1)
            """, (pattern,))
            jobs = cursor.fetchall()
            
            print(f"\nJobs in '{location}':")
            print("=" * 60)
            if jobs:
                for job in jobs:
                    loc = ', '.join(filter(None, [job[3], job[4]]))
                    print(f"  [{job[0]}] {job[1]} at {job[2]} ({loc})")
            else:
                print(f"  No jobs found in '{location}'")
            return jobs

    def search_by_company(self, company):
        """Search for jobs at a specific company."""
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT j.job_id, j.title, c.name AS company_name, 
                       l.city, l.state
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
                JOIN locations l ON j.location_id = l.location_id
                WHERE UPPER(c.name) LIKE UPPER(:1)
            """, (f"%{company}%",))
            jobs = cursor.fetchall()
            
            print(f"\nJobs at '{company}':")
            print("=" * 60)
            if jobs:
                for job in jobs:
                    loc = ', '.join(filter(None, [job[3], job[4]]))
                    print(f"  [{job[0]}] {job[1]} at {job[2]} ({loc})")
            else:
                print(f"  No jobs found at '{company}'")
            return jobs

    def top_skills(self, limit=10):
        """List the most in-demand skills."""
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT s.skill_name, COUNT(js.job_id) as job_count
                FROM skills s
                JOIN job_skills js ON s.skill_id = js.skill_id
                GROUP BY s.skill_name
                ORDER BY job_count DESC
                FETCH FIRST :1 ROWS ONLY
            """, (limit,))
            skills = cursor.fetchall()
            
            print(f"\nTop {limit} In-Demand Skills:")
            print("=" * 40)
            for i, skill in enumerate(skills, 1):
                print(f"  {i}. {skill[0]} ({skill[1]} jobs)")
            return skills


def main():
    tool = QueryTool()
    
    print("\n" + "=" * 50)
    print("  LinkedIn Job Database Query Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("  1. List tables")
        print("  2. Describe table")
        print("  3. Count records")
        print("  4. List all jobs")
        print("  5. Job details")
        print("  6. Search by skill")
        print("  7. Search by location")
        print("  8. Search by company")
        print("  9. Top skills")
        print("  0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        try:
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                tool.list_tables()
            elif choice == '2':
                table = input("Table name: ").strip()
                tool.describe_table(table)
            elif choice == '3':
                table = input("Table name: ").strip()
                tool.count_records(table)
            elif choice == '4':
                tool.list_jobs()
            elif choice == '5':
                job_id = int(input("Job ID: ").strip())
                tool.job_details(job_id)
            elif choice == '6':
                skill = input("Skill: ").strip()
                tool.search_by_skill(skill)
            elif choice == '7':
                location = input("Location: ").strip()
                tool.search_by_location(location)
            elif choice == '8':
                company = input("Company: ").strip()
                tool.search_by_company(company)
            elif choice == '9':
                limit = input("How many? (default 10): ").strip()
                tool.top_skills(int(limit) if limit else 10)
            else:
                print("Invalid choice")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()