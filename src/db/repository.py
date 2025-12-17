from dataclasses import dataclass
from datetime import date
from typing import Optional, List
from src.db.connection import Database


@dataclass
class Company:
    name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    company_id: Optional[int] = None


@dataclass
class Location:
    city: str
    state: str
    country: str = "USA"
    location_id: Optional[int] = None


@dataclass
class Skill:
    skill_name: str
    skill_id: Optional[int] = None


@dataclass
class Job:
    title: str
    company_id: int
    location_id: int
    description: Optional[str] = None
    post_date: Optional[date] = None
    job_id: Optional[int] = None


class CompanyRepository:
    @staticmethod
    def insert(company: Company) -> int:
        with Database.get_cursor() as cursor:
            id_var = cursor.var(int)
            cursor.execute(
                """
                INSERT INTO companies (name, industry, company_size)
                VALUES (:name, :industry, :company_size)
                RETURNING company_id INTO :id
                """,
                {
                    "name": company.name,
                    "industry": company.industry,
                    "company_size": company.company_size,
                    "id": id_var,
                },
            )
            return id_var.getvalue()[0]

    @staticmethod
    def find_by_name(name: str) -> Optional[Company]:
        with Database.get_cursor() as cursor:
            cursor.execute(
                "SELECT company_id, name, industry, company_size FROM companies WHERE name = :name",
                {"name": name},
            )
            row = cursor.fetchone()
            if row:
                return Company(company_id=row[0], name=row[1], industry=row[2], company_size=row[3])
            return None

    @staticmethod
    def get_or_create(company: Company) -> int:
        existing = CompanyRepository.find_by_name(company.name)
        if existing:
            return existing.company_id
        return CompanyRepository.insert(company)


class LocationRepository:
    @staticmethod
    def insert(location: Location) -> int:
        with Database.get_cursor() as cursor:
            id_var = cursor.var(int)
            cursor.execute(
                """
                INSERT INTO locations (city, state, country)
                VALUES (:city, :state, :country)
                RETURNING location_id INTO :id
                """,
                {
                    "city": location.city,
                    "state": location.state,
                    "country": location.country,
                    "id": id_var,
                },
            )
            return id_var.getvalue()[0]

    @staticmethod
    def find_by_location(city: str, state: str, country: str) -> Optional[Location]:
        with Database.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT location_id, city, state, country FROM locations
                WHERE city = :city AND state = :state AND country = :country
                """,
                {"city": city, "state": state, "country": country},
            )
            row = cursor.fetchone()
            if row:
                return Location(location_id=row[0], city=row[1], state=row[2], country=row[3])
            return None

    @staticmethod
    def get_or_create(location: Location) -> int:
        existing = LocationRepository.find_by_location(location.city, location.state, location.country)
        if existing:
            return existing.location_id
        return LocationRepository.insert(location)


class SkillRepository:
    @staticmethod
    def insert(skill: Skill) -> int:
        with Database.get_cursor() as cursor:
            id_var = cursor.var(int)
            cursor.execute(
                """
                INSERT INTO skills (skill_name)
                VALUES (:skill_name)
                RETURNING skill_id INTO :id
                """,
                {"skill_name": skill.skill_name, "id": id_var},
            )
            return id_var.getvalue()[0]

    @staticmethod
    def find_by_name(skill_name: str) -> Optional[Skill]:
        with Database.get_cursor() as cursor:
            cursor.execute(
                "SELECT skill_id, skill_name FROM skills WHERE skill_name = :skill_name",
                {"skill_name": skill_name},
            )
            row = cursor.fetchone()
            if row:
                return Skill(skill_id=row[0], skill_name=row[1])
            return None

    @staticmethod
    def get_or_create(skill: Skill) -> int:
        existing = SkillRepository.find_by_name(skill.skill_name)
        if existing:
            return existing.skill_id
        return SkillRepository.insert(skill)


class JobRepository:
    @staticmethod
    def insert(job: Job) -> int:
        with Database.get_cursor() as cursor:
            id_var = cursor.var(int)
            cursor.execute(
                """
                INSERT INTO jobs (title, company_id, location_id, description, post_date)
                VALUES (:title, :company_id, :location_id, :description, :post_date)
                RETURNING job_id INTO :id
                """,
                {
                    "title": job.title,
                    "company_id": job.company_id,
                    "location_id": job.location_id,
                    "description": job.description,
                    "post_date": job.post_date,
                    "id": id_var,
                },
            )
            return id_var.getvalue()[0]

    @staticmethod
    def add_skill(job_id: int, skill_id: int) -> None:
        with Database.get_cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO job_skills (job_id, skill_id) VALUES (:job_id, :skill_id)",
                    {"job_id": job_id, "skill_id": skill_id},
                )
            except Exception as e:
                if "ORA-00001" not in str(e):
                    raise

    @staticmethod
    def find_by_title(title: str) -> List[Job]:
        with Database.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT job_id, title, company_id, location_id, description, post_date
                FROM jobs WHERE LOWER(title) LIKE LOWER(:title)
                """,
                {"title": f"%{title}%"},
            )
            return [
                Job(
                    job_id=row[0],
                    title=row[1],
                    company_id=row[2],
                    location_id=row[3],
                    description=row[4],
                    post_date=row[5],
                )
                for row in cursor.fetchall()
            ]

    @staticmethod
    def get_all_with_details() -> List[dict]:
        with Database.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT j.job_id, j.title, c.name as company, 
                       l.city, l.state, l.country, j.post_date
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
                JOIN locations l ON j.location_id = l.location_id
                ORDER BY j.post_date DESC
                """
            )
            columns = ["job_id", "title", "company", "city", "state", "country", "post_date"]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]