# LinkedIn Job Scraper

Multi-source job scraper with Oracle database backend. Scrapes LinkedIn, Indeed, and Glassdoor.

## Project Evolution(Base Foundation)

| Phase | Database | Key Features | Report |
|-------|----------|--------------|--------|
| **1** | SQLite | 2-table design, basic scraper | [PDF](docs/PhaseI.pdf) |
| **2** | MySQL | 5-table 3NF schema, 10 queries | [PDF](docs/PhaseII.pdf) |
| **3** | Oracle | Docker, sequences/triggers, multi-source | [PDF](docs/PhaseIII.pdf) |

## Tech Stack

- **Python 3.9** - Core language
- **Selenium + undetected-chromedriver** - Web scraping
- **Oracle 19c** - Database (Docker)
- **oracledb** - Python Oracle driver

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.9+
- Chrome browser

### Installation
```bash
# Clone repo
git clone https://github.com/DynoJ/linkedin-job-scraper
cd linkedin-job-scraper

# Start Oracle
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Oracle password
```

### Usage
```bash
# Scrape from all sources
python -m src.main

# Scrape from specific source
python -m src.main linkedin
python -m src.main indeed
python -m src.main glassdoor

# Custom keywords
python -m src.main indeed "python developer"

# View saved jobs
python -m src.main view

# Interactive query tool
python queries/query_db.py
```

## Database Schema
```
┌─────────────┐      ┌──────────┐      ┌───────────┐
│  Companies  │◄─────┤   Jobs   │─────►│ Locations │
└─────────────┘      └──────────┘      └───────────┘
                           │
                           ▼
                     ┌───────────┐
                     │ Job_Skills│
                     └─────┬─────┘
                           │
                           ▼
                     ┌───────────┐
                     │   Skills  │
                     └───────────┘
```

**5 Tables (3NF Normalized):**
- `companies` - Company info
- `locations` - City, state, country
- `jobs` - Job listings (FK to companies, locations)
- `skills` - Skill names
- `job_skills` - Many-to-many join table

## Project Structure
```
linkedin-job-scraper/
├── src/
│   ├── config/
│   │   └── settings.py      # Environment config
│   ├── db/
│   │   ├── connection.py    # Oracle connection pool
│   │   ├── models.py        # Schema definitions
│   │   └── repository.py    # Data access layer
│   ├── scraper/
│   │   ├── base.py          # BaseScraper class
│   │   ├── linkedin.py      # LinkedIn scraper
│   │   ├── indeed.py        # Indeed scraper
│   │   ├── glassdoor.py     # Glassdoor scraper
│   │   └── parser.py        # Job parsing utilities
│   └── main.py              # CLI entry point
├── queries/
│   └── query_db.py          # Interactive query tool
├── docs/
│   ├── PhaseI.pdf
│   ├── PhaseII.pdf
│   └── PhaseIII.pdf
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Scrapers

| Source | Title | Company | Location | Description | Skills |
|--------|-------|---------|----------|-------------|--------|
| LinkedIn | ✅ | ✅ | ✅ | ❌ | ❌ |
| Indeed | ✅ | ✅ | ✅ | ✅ | ✅ |
| Glassdoor | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |

## Query Tool

Interactive CLI for database queries:
```
Options:
  1. List tables
  2. Describe table
  3. Count records
  4. List all jobs
  5. Job details
  6. Search by skill
  7. Search by location
  8. Search by company
  9. Top skills
  0. Exit
```

## What I Learned

- **Database Design:** Normalization (1NF → 3NF), foreign keys, join tables
- **Oracle:** Sequences, triggers, CLOB fields, connection pooling
- **Web Scraping:** Selenium, anti-bot detection, headless browsers
- **Architecture:** Repository pattern, base classes, config management

## Future Improvements

- [ ] Add pagination for 100+ jobs
- [ ] Build REST API layer
- [ ] Create Streamlit dashboard
- [ ] Add unit tests
- [ ] Implement job deduplication