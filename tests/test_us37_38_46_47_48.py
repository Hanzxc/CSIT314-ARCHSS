"""Data-level US37/38/46/47/48 tests on a temporary SQLite database."""
import sqlite3
from pathlib import Path
import pytest
import entity.idpAnalytics as analytics_module
from entity.idpAnalytics import IDPAnalytics

@pytest.fixture
def repo_db(tmp_path, monkeypatch):
    db = tmp_path / 'analytics_only.db'
    schema = (Path(__file__).resolve().parents[1] / 'database' / 'schema.sql').read_text()
    con = sqlite3.connect(db)
    con.executescript(schema)
    con.executemany('INSERT INTO user_profile(profileId,profileName,permissions) VALUES(?,?,?)',
                    [(1,'Designer','[]'),(2,'Customer','[]'),(3,'Manager','[]')])
    con.executemany('INSERT INTO user_account(userId,username,password,fullName,profileId) VALUES(?,?,?,?,?)',
                    [(1,'d1','x','Designer One',1),(2,'d2','x','Designer Two',1),
                     (3,'c1','x','Customer One',2),(4,'c2','x','Customer Two',2)])
    con.executemany('INSERT INTO idp_category(categoryId,categoryName) VALUES(?,?)',
                    [(1,'Kitchen'),(2,'Bedroom')])
    con.executemany("INSERT INTO idp(idpId,designerId,categoryId,title,description,projectType) VALUES(?,?,?,?,?,?)",
                    [(1,1,1,'Modern Kitchen','Test', 'Current'),
                     (2,1,2,'Cozy Bedroom','Test', 'Past'),
                     (3,2,1,'Other Kitchen','Test', 'Current')])
    con.executemany('INSERT INTO saved_idp(customerId,idpId,savedDate) VALUES(?,?,?)',
                    [(3,1,'2026-11-05 10:00:00'),(4,1,'2026-11-05 12:00:00'),
                     (3,2,'2026-10-30 10:00:00')])
    con.executemany('INSERT INTO idp_view(idpId,viewedAt) VALUES(?,?)',
                    [(1,'2026-11-05 08:00:00'),(1,'2026-11-05 09:00:00'),
                     (2,'2026-11-04 10:00:00'),(3,'2026-11-05 11:00:00')])
    con.commit();con.close()
    def connection():
        c = sqlite3.connect(db)
        c.row_factory = sqlite3.Row
        return c
    monkeypatch.setattr(analytics_module, 'getConnection', connection)
    return connection

def test_us37_views_are_scoped_to_designer(repo_db):
    data = IDPAnalytics().get_designer_statistics(1)
    assert {r['idpId'] for r in data} == {1,2}
    assert {r['idpId']:r['views'] for r in data} == {1:2,2:1}

def test_us38_saved_users_counted(repo_db):
    data = IDPAnalytics().get_designer_statistics(1)
    assert {r['idpId']:r['saves'] for r in data} == {1:2,2:1}

def test_us46_daily_report(repo_db):
    r=IDPAnalytics().get_category_report('daily','2026-11-05')
    assert (r['start'],r['end_exclusive']) == ('2026-11-05','2026-11-06')
    assert [(x['categoryName'],x['views'],x['saves']) for x in r['categories']] == [
        ('Kitchen',3,2),('Bedroom',0,0)]

def test_us47_weekly_report(repo_db):
    r=IDPAnalytics().get_category_report('weekly','2026-11-05')
    assert (r['start'],r['end_exclusive']) == ('2026-11-02','2026-11-09')
    assert next(x for x in r['categories'] if x['categoryName']=='Bedroom')['views']==1

def test_us48_monthly_report(repo_db):
    r=IDPAnalytics().get_category_report('monthly','2026-11-05')
    assert (r['start'],r['end_exclusive']) == ('2026-11-01','2026-12-01')
    assert next(x for x in r['categories'] if x['categoryName']=='Bedroom')['saves']==0

def test_us48_december_rollover():
    assert IDPAnalytics.period_bounds('monthly','2026-12-31') == ('2026-12-01','2027-01-01')

def test_invalid_date_rejected():
    with pytest.raises(ValueError):
        IDPAnalytics.period_bounds('daily','2026-02-30')

def test_us37_view_records_only_active_idps(repo_db):
    a=IDPAnalytics()
    assert a.record_project_view(1)['title']=='Modern Kitchen'
    assert a.record_project_view(9999) is None
    conn=repo_db()
    assert conn.execute('SELECT COUNT(*) FROM idp_view WHERE idpId=1').fetchone()[0]==3
    conn.close()
