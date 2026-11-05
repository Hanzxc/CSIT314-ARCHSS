import pytest
from app import app
from database.db import getConnection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'testsecret'
    with app.test_client() as client:
        conn = getConnection()
        cursor = conn.cursor()
        
        # Seed test category
        cursor.execute("""
            INSERT OR IGNORE INTO idp_category (categoryId, categoryName, status)
            VALUES (1, 'Living Room', 'Active')
        """)
        
        # Seed test designer account
        cursor.execute("""
            INSERT OR IGNORE INTO user_account (userId, username, password, fullName, profileId, status)
            VALUES (1, 'designer1', 'pw', 'Designer One', 2, 'Active')
        """)
        
        # Seed a base Past IDP for view/update/delete/search tests
        cursor.execute("""
            INSERT OR IGNORE INTO idp (idpId, designerId, categoryId, title, description, projectType, status)
            VALUES (200, 1, 1, 'Scandinavian Resale Flat', 'Minimalist timber elements', 'Past', 'Active')
        """)
        conn.commit()
        conn.close()
        yield client


# --- US25: Add Past IDP ---
def test_us25_add_past_idp(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'Interior Designer'

    response = client.post('/designer/past-idps/add', data={
        'title': 'Modern Luxury Condo',
        'categoryId': 1,
        'description': 'Full marble flooring and ambient LED lighting.',
        'location': 'Orchard'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Past IDP added successfully" in response.data or b"Modern Luxury Condo" in response.data


# --- US26: View Past IDPs ---
def test_us26_view_past_idp(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'Interior Designer'

    response = client.get('/designer/past-idps')
    assert response.status_code == 200
    assert b"Scandinavian Resale Flat" in response.data


# --- US27: Update Past IDP ---
def test_us27_update_past_idp(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'Interior Designer'

    response = client.post('/designer/past-idps/update/200', data={
        'title': 'Updated Scandinavian Resale',
        'categoryId': 1,
        'description': 'Updated scope details',
        'location': 'Bishan'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Past IDP updated successfully" in response.data or b"Updated Scandinavian Resale" in response.data


# --- US28: Delete Past IDP ---
def test_us28_delete_past_idp(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'Interior Designer'

    response = client.post('/designer/past-idps/delete/200', follow_redirects=True)
    assert response.status_code == 200
    assert b"Past IDP deleted successfully" in response.data or b"Scandinavian Resale Flat" not in response.data


# --- US29: Search Past IDPs ---
def test_us29_search_past_idp(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'Interior Designer'

    response = client.get('/designer/past-idps/search?keyword=Scandinavian')
    assert response.status_code == 200
    assert b"Scandinavian Resale Flat" in response.data