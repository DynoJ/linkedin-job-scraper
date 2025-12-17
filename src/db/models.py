from src.db.connection import Database

SEQUENCES = [
    "CREATE SEQUENCE company_seq START WITH 1 INCREMENT BY 1",
    "CREATE SEQUENCE location_seq START WITH 1 INCREMENT BY 1",
    "CREATE SEQUENCE skill_seq START WITH 1 INCREMENT BY 1",
    "CREATE SEQUENCE job_seq START WITH 1 INCREMENT BY 1",
]

TABLES = [
    """
    CREATE TABLE companies (
        company_id NUMBER PRIMARY KEY,
        name VARCHAR2(255) NOT NULL,
        industry VARCHAR2(255),
        company_size VARCHAR2(100)
    )
    """,
    """
    CREATE TABLE locations (
        location_id NUMBER PRIMARY KEY,
        city VARCHAR2(100),
        state VARCHAR2(100),
        country VARCHAR2(100) DEFAULT 'USA',
        CONSTRAINT uq_location UNIQUE (city, state, country)
    )
    """,
    """
    CREATE TABLE skills (
        skill_id NUMBER PRIMARY KEY,
        skill_name VARCHAR2(100) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE jobs (
        job_id NUMBER PRIMARY KEY,
        title VARCHAR2(255) NOT NULL,
        company_id NUMBER,
        location_id NUMBER,
        description CLOB,
        post_date DATE,
        CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES companies(company_id),
        CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES locations(location_id)
    )
    """,
    """
    CREATE TABLE job_skills (
        job_id NUMBER,
        skill_id NUMBER,
        PRIMARY KEY (job_id, skill_id),
        CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
        CONSTRAINT fk_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
    )
    """,
]

TRIGGERS = [
    """
    CREATE OR REPLACE TRIGGER trg_company_id
    BEFORE INSERT ON companies
    FOR EACH ROW
    WHEN (NEW.company_id IS NULL)
    BEGIN
        SELECT company_seq.NEXTVAL INTO :NEW.company_id FROM dual;
    END;
    """,
    """
    CREATE OR REPLACE TRIGGER trg_location_id
    BEFORE INSERT ON locations
    FOR EACH ROW
    WHEN (NEW.location_id IS NULL)
    BEGIN
        SELECT location_seq.NEXTVAL INTO :NEW.location_id FROM dual;
    END;
    """,
    """
    CREATE OR REPLACE TRIGGER trg_skill_id
    BEFORE INSERT ON skills
    FOR EACH ROW
    WHEN (NEW.skill_id IS NULL)
    BEGIN
        SELECT skill_seq.NEXTVAL INTO :NEW.skill_id FROM dual;
    END;
    """,
    """
    CREATE OR REPLACE TRIGGER trg_job_id
    BEFORE INSERT ON jobs
    FOR EACH ROW
    WHEN (NEW.job_id IS NULL)
    BEGIN
        SELECT job_seq.NEXTVAL INTO :NEW.job_id FROM dual;
    END;
    """,
]


def init_schema() -> None:
    with Database.get_cursor() as cursor:
        for seq in SEQUENCES:
            try:
                cursor.execute(seq)
            except Exception as e:
                if "ORA-00955" not in str(e):
                    raise

        for table in TABLES:
            try:
                cursor.execute(table)
            except Exception as e:
                if "ORA-00955" not in str(e):
                    raise

        for trigger in TRIGGERS:
            cursor.execute(trigger)


def drop_schema() -> None:
    with Database.get_cursor() as cursor:
        for table in ["job_skills", "jobs", "skills", "locations", "companies"]:
            try:
                cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
            except Exception as e:
                if "ORA-00942" not in str(e):
                    raise

        for seq in ["job_seq", "skill_seq", "location_seq", "company_seq"]:
            try:
                cursor.execute(f"DROP SEQUENCE {seq}")
            except Exception as e:
                if "ORA-02289" not in str(e):
                    raise