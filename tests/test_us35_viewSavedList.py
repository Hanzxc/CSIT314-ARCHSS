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
        cursor.execute("INSERT OR IGNORE INTO idp (idpId, designerId, categoryId, title, description, projectType, status) VALUES (107, 1, 1, 'Bookmarked Project', 'Desc', 'Past', 'Active')")
        cursor.execute("INSERT OR IGNORE INTO saved_idp (customerId, idpId) VALUES ((SELECT userId FROM user_account WHERE username='cust001'), 107)")
        conn.commit()
        conn.close()
        yield client

def test_view_saved_list(client):
    client.post('/customer/login', data=dict(username='cust001', password='Cust@123'))

    response = client.get('/customer/saved-list')
    assert response.status_code == 200
    assert b"Bookmarked Project" in response.data