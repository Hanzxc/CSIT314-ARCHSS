# Unit tests for US18 Search company information.
# conftest.py creates a fresh database for every test.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.searchCompanyInformationController import SearchCompanyInformationController
from control.interiorDesignerLoginController import REQUIRED_DESIGNER_PERMISSIONS


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def makeCompany(designerId, data):
    # the entity takes a CompanyProfile object now, not a dict
    return CompanyProfile(designerId=designerId, **data)


def createDesigner13():
    UserAccount().createUserAccount(
        UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="designer13@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer13", "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId


def createCompanyForDesigner13():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    return userId


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


def companyRows():
    conn = getConnection()
    rows = conn.execute("SELECT * FROM company_profile ORDER BY companyId").fetchall()
    conn.close()
    return [tuple(row) for row in rows]


# ---------- SearchCompanyInformationController.searchCompanyInformation() ----------

def test_ut18_1_search_partOfValue():
    userId = createCompanyForDesigner13()
    companyProfile = SearchCompanyInformationController().searchCompanyInformation(userId, "renov")
    assert isinstance(companyProfile, CompanyProfile)
    assert companyProfile.matchedFields == ["services"]
    assert companyProfile.services == "Space planning, renovation"


def test_ut18_2_search_capitals():
    userId = createCompanyForDesigner13()
    assert SearchCompanyInformationController().searchCompanyInformation(userId, "RENOVATION").matchedFields == ["services"]


def test_ut18_3_search_emptyKeyword_returnsAllFields():
    userId = createCompanyForDesigner13()
    companyProfile = SearchCompanyInformationController().searchCompanyInformation(userId, "")
    assert companyProfile.matchedFields == ["companyName", "description", "services", "email", "phone", "address"]


def test_ut18_4_search_noMatch():
    userId = createCompanyForDesigner13()
    companyProfile = SearchCompanyInformationController().searchCompanyInformation(userId, "zzzz")
    assert isinstance(companyProfile, CompanyProfile)
    assert companyProfile.matchedFields == []


def test_ut18_5_search_trimsKeyword():
    # the page trims the keyword now, not the controller
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search", query_string={"keyword": "  renovation  "})
    assert b"Space planning, renovation" in response.data
    assert b"hello@udainteriors.com" not in response.data
    assert b'value="renovation"' in response.data


def test_ut18_6_search_spacesOnly_returnsAll():
    # just spaces -> page trims it to "" -> everything shows
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search", query_string={"keyword": "   "})
    for text in companyData().values():
        assert text.encode() in response.data


def test_ut18_7_search_fieldName():
    userId = createCompanyForDesigner13()
    companyProfile = SearchCompanyInformationController().searchCompanyInformation(userId, "phone")
    assert companyProfile.matchedFields == ["phone"]
    assert companyProfile.phone == "+65 6123 4567"


def test_ut18_9_search_noProfile():
    userId = createDesigner13()
    assert SearchCompanyInformationController().searchCompanyInformation(userId, "") is None


# ---------- CompanyProfile.searchCompanyInformation() ----------

def test_ut18_10_entity_byEmail():
    userId = createCompanyForDesigner13()
    assert CompanyProfile().searchCompanyInformation(userId, "hello@").matchedFields == ["email"]


def test_ut18_11_entity_byAddress():
    userId = createCompanyForDesigner13()
    assert CompanyProfile().searchCompanyInformation(userId, "Design Street").matchedFields == ["address"]


def test_ut18_12_entity_otherOwnerExcluded():
    createCompanyForDesigner13()
    UserAccount().createUserAccount(UserAccount(username="designer18", password="Design@123", fullName="Daniel Tan", email="", phone="", profileId=2))
    otherId = UserAccount().verifyCredentials("designer18", "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId
    assert CompanyProfile().searchCompanyInformation(otherId, "Uda") is None


def test_ut18_13_entity_treatsPercentAsLiteral():
    userId = createCompanyForDesigner13()
    assert CompanyProfile().searchCompanyInformation(userId, "%").matchedFields == []
    data = companyData()
    data["description"] = "Save 20% on design"
    CompanyProfile().updateCompanyProfile(makeCompany(userId, data))
    assert CompanyProfile().searchCompanyInformation(userId, "%").matchedFields == ["description"]


def test_ut18_14_entity_doesNotChangeData():
    userId = createCompanyForDesigner13()
    before = companyRows()
    CompanyProfile().searchCompanyInformation(userId, "design")
    assert companyRows() == before


def test_ut18_15_entity_noInternalAccountData():
    userId = createCompanyForDesigner13()
    assert CompanyProfile().searchCompanyInformation(userId, "designer13").matchedFields == []
    assert CompanyProfile().searchCompanyInformation(userId, "Design@123").matchedFields == []


# ---------- whole page, through the browser (test client) ----------

def test_ut18_16_searchPage_showsResults():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search?keyword=renovation")
    assert response.status_code == 200
    assert b"Services offered" in response.data
    assert b"Space planning, renovation" in response.data
    assert b"hello@udainteriors.com" not in response.data
    assert b'value="renovation"' in response.data


def test_ut18_17_searchPage_noResults():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search?keyword=zzzz")
    assert response.status_code == 200
    assert b"No matching company information found" in response.data
    assert b'value="zzzz"' in response.data


def test_ut18_18_searchPage_noKeyword_showsAll():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search")
    for text in companyData().values():
        assert text.encode() in response.data


def test_ut18_19_searchPage_notLoggedIn():
    client = app.test_client()
    response = client.get("/designer/company/search?keyword=design")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")


def test_ut18_21_searchPage_noProfile():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search")
    assert response.status_code == 404
    assert b"You have not created a company profile yet" in response.data
    assert b'href="/designer/company/create"' in response.data


def test_ut18_22_searchPage_ignoresForgedOwner():
    createCompanyForDesigner13()
    UserAccount().createUserAccount(UserAccount(username="designer18", password="Design@123", fullName="Daniel Tan", email="", phone="", profileId=2))
    otherId = UserAccount().verifyCredentials("designer18", "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId
    data = companyData()
    data["services"] = "Other designer confidential service"
    CompanyProfile().createCompanyProfile(makeCompany(otherId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search?keyword=confidential&designerId=" + str(otherId))
    assert b"No matching company information found" in response.data
    assert b"Other designer confidential service" not in response.data


def test_ut18_23_searchPage_optionalFieldsEmpty():
    userId = createDesigner13()
    data = companyData()
    data.update(email="", phone="", address="")
    CompanyProfile().createCompanyProfile(makeCompany(userId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search")
    assert response.data.count(b"Not provided") == 3


def test_ut18_24_searchPage_escapesKeywordAndValue():
    userId = createDesigner13()
    data = companyData()
    data["description"] = "<script>alert(1)</script>"
    CompanyProfile().createCompanyProfile(makeCompany(userId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/search", query_string={"keyword": "<script>"})
    assert b"<script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_ut18_25_searchPage_doesNotChangeData():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    before = companyRows()
    client.get("/designer/company/search?keyword=design")
    client.get("/designer/company/search?keyword=zzzz")
    assert companyRows() == before


def test_ut18_27_viewPage_showsSearchLink():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert b'href="/designer/company/search"' in client.get("/designer/company").data


def test_ut18_28_search_afterUpdateAndDelete():
    userId = createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/create", data=companyData())
    data = companyData()
    data["services"] = "Office refurbishment"
    client.post("/designer/company/update", data=data)
    assert b"Office refurbishment" in client.get("/designer/company/search?keyword=refurb").data
    # the confirmation box posts the companyId + revision
    profile = CompanyProfile().getCompanyProfile(userId)
    client.get("/designer/company/delete")
    client.post("/designer/company/delete", data={"choice": "delete", "companyId": str(profile.companyId),
                                                "revision": str(profile.revision)})
    response = client.get("/designer/company/search?keyword=refurb")
    assert response.status_code == 404
    assert b"Office refurbishment" not in response.data


def test_ut18_suspendedProfile_isUnavailable():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    profile = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision) is True
    client = app.test_client()
    loginAsDesigner13(client)
    assert client.get("/designer/company/search?keyword=Uda").status_code == 404
    assert CompanyProfile().searchCompanyInformation(userId, "Uda") is None
