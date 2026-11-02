# Shared test setup for all user stories.
# pytest runs this automatically - every test gets its own fresh database
# in a temp folder, so tests never touch the real database/archss.db

import pytest

import database.db as db
from database.seedData import seedDefaultData


@pytest.fixture(autouse=True)
def testDatabase(tmp_path, monkeypatch):
    # point getConnection() at a temp database file instead of the real one
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.initDatabase()

    # Seed the current default users. Story fixtures create their own categories;
    # keep demo catalogue additions from changing those isolated starting states.
    conn = db.getConnection()
    seedDefaultData(conn)
    conn.execute("DELETE FROM idp_category")
    conn.commit()
    conn.close()
    yield
