"""Exercise real login across the previously separate story branches."""
import re

import pytest

from app import app
from database.db import getConnection


def test_addedProjectCanBeManagedFoundViewedSavedAndLoggedOut():
    conn = getConnection()
    category = conn.execute("INSERT INTO idp_category(categoryName) VALUES ('Integration Kitchen')").lastrowid
    conn.commit()
    conn.close()
    designer = app.test_client()
    designer.post('/designer/login', data=dict(username='designer1', password='Pass@123'))
    response = designer.post('/designer/idps/add', data=dict(title='Integrated Kitchen',
        categoryId=category, description='Initial design progress', location='Bedok'))
    assert response.status_code in (200, 302)
    conn = getConnection()
    project = conn.execute("SELECT idpId FROM idp WHERE title='Integrated Kitchen'").fetchone()['idpId']
    conn.close()
    assert b'Integrated Kitchen' in designer.get('/designer/idps/current').data
    form = designer.get(f'/designer/idps/current/{project}/update')
    token = re.search(rb'name="updateToken" value="([^"]+)"', form.data).group(1).decode()
    designer.post(f'/designer/idps/current/{project}/update', data=dict(title='Integrated Kitchen',
        categoryId=category, description='Carpentry completed', location='Bedok', updateToken=token))
    customer = app.test_client()
    customer.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    assert b'Integrated Kitchen' in customer.get('/customer/idps/search?keyword=integrated').data
    detail = customer.get(f'/customer/idps/{project}')
    assert b'Carpentry completed' in detail.data and b'>Save IDP</button>' in detail.data
    saved = customer.post(f'/customer/save-idp/{project}', follow_redirects=True)
    assert saved.status_code == 200 and b'Integrated Kitchen' in saved.data
    assert b'IDP saved to your favourites' in saved.data
    assert b'Remove from saved list' in customer.get(f'/customer/idps/{project}').data
    assert b'Integrated Kitchen' in customer.get('/customer/saved-list/search?keyword=Kitchen').data
    customer.post('/customer/logout', follow_redirects=True)
    assert customer.get('/customer/saved-list').headers['Location'].endswith('/customer/login')


@pytest.mark.parametrize('path,method', [('/customer/saved-list', 'get'),
    ('/customer/saved-list/search', 'get'), ('/customer/save-idp/999999', 'post')])
def test_savedRoutesRecheckUS30Access(path, method):
    client = app.test_client()
    client.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    conn = getConnection()
    conn.execute("UPDATE user_profile SET permissions='[]' WHERE profileId=3")
    conn.commit()
    conn.close()
    # Old role labels must not bypass current database permissions.
    with client.session_transaction() as state:
        state.update(user_role='Customer', user_id=3)
    assert getattr(client, method)(path).status_code == 403


@pytest.mark.parametrize('path,method', [('/customer/saved-list', 'get'),
    ('/customer/saved-list/search', 'get'), ('/customer/save-idp/999999', 'post')])
def test_savedRoutesRequireLogin(path, method):
    response = getattr(app.test_client(), method)(path)
    assert response.status_code == 302 and response.headers['Location'].endswith('/customer/login')
