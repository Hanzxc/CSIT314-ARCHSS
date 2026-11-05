# tests/test_us33_saveIDP.py
import pytest
from app import app
from database.db import getConnection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO user_account (userId, username, password, fullName, profileId, status) VALUES (1, 'designer1', 'pw', 'Designer One', 2, 'Active')")
        cursor.execute("INSERT OR IGNORE INTO user_account (userId, username, password, fullName, profileId, status) VALUES (2, 'cust001', 'pw', 'Customer One', 1, 'Active')")
        cursor.execute("INSERT OR IGNORE INTO idp_category (categoryId, categoryName, status) VALUES (1, 'Living Room', 'Active')")
        cursor.execute("""
            INSERT OR IGNORE INTO idp (idpId, designerId, categoryId, title, description, projectType, status)
            VALUES (105, 1, 1, 'Modern Minimalist Flat', 'Renovated home', 'Past', 'Active')
        """)
        conn.commit()
        conn.close()
        yield client

def test_toggle_save_idp(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['user_role'] = 'Customer'

    # 1. Bookmark IDP
    response = client.post('/customer/save-idp/105', follow_redirects=True)
    assert response.status_code == 200
    assert b"IDP saved to your favourites" in response.data or b"Saved" in response.data

    # 2. Toggle Unsave IDP
    response2 = client.post('/customer/save-idp/105', follow_redirects=True)
    assert response2.status_code == 200
    assert b"IDP removed from your saved list" in response2.data or b"Unsaved" in response2.data