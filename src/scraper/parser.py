import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, List


@dataclass
class ParsedJob:
    title: str
    company: str
    city: str
    state: str
    country: str
    description: str
    skills: List[str]
    post_date: Optional[date] = None


def parse_location(location_str: str) -> tuple[str, str, str]:
    """Parse location string into (city, state, country)."""
    if not location_str:
        return "Unknown", "Unknown", "USA"
    
    parts = [p.strip() for p in location_str.split(",")]
    
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        return parts[0], parts[1], "USA"
    else:
        return parts[0], "Unknown", "USA"


def parse_post_date(date_str: str) -> Optional[date]:
    """Parse relative date strings like '2 days ago' into actual dates."""
    if not date_str:
        return None
    
    date_str = date_str.lower().strip()
    today = date.today()
    
    if "just now" in date_str or "today" in date_str:
        return today
    elif "yesterday" in date_str:
        return today - timedelta(days=1)
    elif "ago" in date_str:
        match = re.search(r"(\d+)\s*(day|week|month|hour|minute)", date_str)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if "day" in unit:
                return today - timedelta(days=num)
            elif "week" in unit:
                return today - timedelta(weeks=num)
            elif "month" in unit:
                return today - timedelta(days=num * 30)
            elif "hour" in unit or "minute" in unit:
                return today
    return None


def extract_skills(description: str) -> List[str]:
    """Extract common tech skills from job description."""
    known_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle",
        "Git", "CI/CD", "Jenkins", "GitHub Actions",
        "REST", "GraphQL", "Microservices", "Agile", "Scrum"
    ]
    
    found = []
    desc_lower = description.lower()
    
    for skill in known_skills:
        if skill.lower() in desc_lower:
            found.append(skill)
    
    return found