# LinkedIn Job Scraper

Automated LinkedIn job scraper demonstrating database evolution from SQLite prototype to Oracle production deployment.

## Project Evolution

| Phase | Database | Key Features | Report |
|-------|----------|--------------|--------|
| **1** | SQLite | 2-table design, basic scraper | [PDF](docs/PhaseI.pdf) |
| **2** | MySQL | 5-table 3NF schema, 10 queries | [PDF](docs/PhaseII.pdf) |
| **3** | Oracle | Docker, sequences/triggers | [PDF](docs/PhaseIII.pdf) |

### Phase 1: SQLite Prototype
Initial proof-of-concept with:
- `websites` table (URL storage)
- `scraped_data` table (content storage)
- Python + Selenium scraper

### Phase 2: MySQL Development  
Expanded to normalized 5-entity design:
- **Jobs** (title, description, post_date)
- **Companies** (name, industry, size)
- **Locations** (city, state, country)
- **Skills** (skill names)
- **Job_Skills** (many-to-many join table)

### Phase 3: Oracle Production (Current)
Enterprise deployment with:
- Oracle 19c in Docker containers
- Auto-incrementing via sequences + triggers
- CLOB fields for large text
- Environment-based configuration

## Tech Stack
**Phase 1:** Python 3.9, Selenium, SQLite  
**Phase 2:** Python 3.9, Selenium, MySQL 8.0, phpMyAdmin  
**Phase 3:** Python 3.9, Selenium, Oracle 19c, Docker

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.9+
- ChromeDriver

### Installation
```bash
# 1. Clone repo
git clone https://github.com/yourusername/linkedin-scraper
cd linkedin-scraper

# 2. Start Oracle
docker-compose up -d

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Oracle password

# 5. Run scraper
python src/main.py
```

## Database Schema (Current: Oracle)
```
┌─────────────┐      ┌──────────┐      ┌───────────┐
│  Companies  │◄─────┤   Jobs   │─────►│ Locations │
└─────────────┘      └──────────┘      └───────────┘
                           │
                           │
                     ┌─────▼──────┐
                     │ Job_Skills │
                     └─────┬──────┘
                           │
                     ┌─────▼──────┐
                     │   Skills   │
                     └────────────┘
```

## By the Numbers
- **3 database migrations** (SQLite → MySQL → Oracle)
- **5 normalized tables** (3NF compliant)
- **10 SQL queries** for analytics
- **15 jobs** scraped per run (configurable)
- **100% referential integrity** (foreign key constraints)

## Sample Queries
See `queries/analysis.sql` for all 10 queries:
- Top in-demand skills
- Jobs by location
- Remote work opportunities
- Salary analysis by company size
- Tech stack trends

## What I Learned

### Database Design
- Normalization (1NF → 2NF → 3NF)
- Multi-table joins (INNER, LEFT, CROSS)
- Referential integrity with foreign keys

### DBMS-Specific Features
- **SQLite:** Lightweight, file-based, `AUTOINCREMENT`
- **MySQL:** phpMyAdmin GUI, `AUTO_INCREMENT`, `TEXT` fields
- **Oracle:** Sequences, triggers, `CLOB` fields, enterprise tooling

### DevOps
- Docker containerization
- Environment variable management
- Schema migration strategies

## Future Improvements
- [ ] Add pagination (scrape 100+ jobs)
- [ ] Implement connection pooling
- [ ] Build Streamlit dashboard
- [ ] Add pytest unit tests
- [ ] GraphQL API layer

## License
MIT (for portfolio use only)
```

---

## **Repo Structure (Updated)**
```
linkedin-job-scraper/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── main.py          # Phase 3 (Oracle)
│   ├── scraper.py       # Phase 3
│   ├── database.py      # Phase 3
│   ├── data_parser.py
│   └── config.py
├── queries/
│   └── analysis.sql     # 10 queries from Phase 2/3
├── docs/
│   ├── Project6_SQLite.pdf   # Phase 1 report
│   ├── Project8_MySQL.pdf    # Phase 2 report
│   ├── Project9_Oracle.pdf   # Phase 3 report
│   └── ARCHITECTURE.md       # Evolution story
└── archive/             # OPTIONAL
    ├── phase1-sqlite/   # Original SQLite code
    └── phase2-mysql/    # Original MySQL code