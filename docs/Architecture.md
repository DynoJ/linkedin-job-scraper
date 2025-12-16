# Architecture Evolution

This document explains the technical decisions behind three database migrations.

## Phase 1: SQLite Prototype (March 2025)

### Design Decisions
- **2-table schema:** `websites` + `scraped_data`
- **SQLite:** Chosen for zero-config development
- **File-based storage:** `scraper.db` in project root

### Limitations
- No normalization (job data mixed with company/location)
- No skill tagging
- Limited query capabilities

### Code Sample
```python
# db.py (Phase 1)
def init_db():
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS websites (
        website_id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        date_added DATETIME
    )''')
    # ...
```

---

## Phase 2: MySQL Migration (April 2025)

### Design Decisions
- **5-table 3NF schema:** Eliminated redundancy
- **MySQL:** Needed multi-user access + phpMyAdmin GUI
- **Foreign keys:** Enforced referential integrity

### Schema Changes
```
Before (SQLite):
websites → scraped_data

After (MySQL):
companies ← jobs → locations
              ↓
         job_skills
              ↓
           skills
```

### Migration Challenges
1. **AUTO_INCREMENT syntax:** SQLite vs MySQL
2. **TEXT vs VARCHAR:** Field size limits
3. **Foreign key constraints:** Had to migrate in order (parent → child)

### Code Changes
```python
# Before (SQLite)
c.execute("INSERT INTO scraped_data (content) VALUES (?)", (text,))

# After (MySQL)
cursor.execute(
    "INSERT INTO jobs (title, company_id, location_id, description) "
    "VALUES (%s, %s, %s, %s)",
    (title, company_id, location_id, description)
)
```

---

## Phase 3: Oracle Production (April 2025)

### Design Decisions
- **Oracle 19c:** Required by course, taught enterprise features
- **Docker:** Eliminated local installation issues
- **Sequences + Triggers:** Replaced MySQL's AUTO_INCREMENT

### Key Differences from MySQL

| Feature | MySQL | Oracle |
|---------|-------|--------|
| Auto-increment | `AUTO_INCREMENT` | `SEQUENCE` + `TRIGGER` |
| Large text | `TEXT` | `CLOB` |
| String concat | `CONCAT()` | `||` operator |
| Connection | `mysql.connector` | `oracledb` |

### Sequence/Trigger Pattern
```sql
-- Create sequence
CREATE SEQUENCE company_seq START WITH 1;

-- Create trigger
CREATE OR REPLACE TRIGGER trg_company_id
BEFORE INSERT ON companies
FOR EACH ROW
BEGIN
    :NEW.company_id := company_seq.NEXTVAL;
END;
```

### Migration Time
- Schema creation: 2 hours (rewrote all DDL)
- Code refactoring: 3 hours (connection handling)
- Testing: 2 hours (verify data integrity)

---

## Lessons Learned

### What Stayed the Same
✅ 3NF schema design (portable across all DBMSs)  
✅ Foreign key relationships  
✅ Core scraping logic  

### What Changed
❌ Auto-increment implementation  
❌ Large text field types  
❌ Connection/cursor syntax  
❌ SQL dialect (string functions, date formatting)  

### Key Takeaway
**Schema design is database-agnostic if done right.** I wrote the schema once in Phase 2 and only had to adjust syntax—not structure—for Phase 3.