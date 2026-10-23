# Regression checks for upgrading existing company databases without deleting data.
import sqlite3
import database.db as db


def test_existingCompanyDatabase_migratesWithoutDataLoss(tmp_path, monkeypatch):
    path = tmp_path / "old-company.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE company_profile (companyId INTEGER PRIMARY KEY, designerId INTEGER UNIQUE, companyName TEXT, description TEXT, services TEXT, email TEXT, phone TEXT, address TEXT, createdDate TEXT)")
    conn.execute("INSERT INTO company_profile VALUES (17, 4, 'Existing Interiors', 'About', 'Design', '', '', '', '2026-01-01')")
    conn.commit()
    before = conn.execute("SELECT * FROM company_profile").fetchone()
    conn.close()
    monkeypatch.setattr(db, "DB_PATH", str(path))
    db.initDatabase()
    db.initDatabase()
    conn = db.getConnection()
    row = conn.execute("SELECT * FROM company_profile").fetchone()
    conn.close()
    assert tuple(row)[:9] == before
    assert row["status"] == "Active"
    assert row["revision"] == 1


def test_existingSuspendedCompany_staysSuspendedAfterRestart():
    conn = db.getConnection()
    conn.execute("INSERT INTO company_profile (designerId, companyName, description, services, status) VALUES (1, 'Stored Interiors', 'About', 'Design', 'Suspended')")
    conn.commit()
    conn.close()
    db.initDatabase()
    conn = db.getConnection()
    row = conn.execute("SELECT status FROM company_profile WHERE designerId=1").fetchone()
    conn.close()
    assert row["status"] == "Suspended"
