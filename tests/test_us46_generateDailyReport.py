# Unit tests for US46 Generate daily report.
# conftest.py gives each test a fresh database with the default users (cust001 is the customer).
# Manager tests add manager46 / Manager@123 (profile 4). Designer + IDP helpers come from the US37 tests.
# The helpers here are shared with the US47 and US48 tests.

from datetime import date, datetime, timedelta, timezone

from app import app
from entity.userAccount import UserAccount
from entity.idpAnalytics import IDPAnalytics
from control.generateDailyReportController import GenerateDailyReportController
from boundary.generateDailyReportPage import (GenerateDailyReportPage, MSG_INVALID_DATE, MSG_FUTURE_DATE,
                                              MSG_NO_ACTIVITY)
from control.platformManagerLoginController import REQUIRED_MANAGER_PERMISSIONS
from test_us37_viewIDPViewStatistics import (createDesigner, customerId, createCategory,
                                             addIDP, addView, addSave)


def createManager(username="manager46"):
    UserAccount().createUserAccount(UserAccount(username=username, password="Manager@123", fullName="Report Manager",
                                    email=username + "@archss.com", phone="", profileId=4))
    return UserAccount().verifyCredentials(username, "Manager@123", REQUIRED_MANAGER_PERMISSIONS).userId


def loggedInManager():
    createManager()
    client = app.test_client()
    client.post("/manager/login", data={"username": "manager46", "password": "Manager@123"})
    return client


def sampleData():
    # Kitchen: 3 views + 1 save on 5 Nov, Bedroom: 1 view on 5 Nov + 1 view on 4 Nov,
    # Bathroom: nothing. Every test that needs activity uses this.
    designer = createDesigner()
    kitchen = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    bedroom = addIDP(designer, createCategory("Bedroom"), "Cozy Bedroom", "Past")
    createCategory("Bathroom")
    for _ in range(3):
        addView(kitchen)
    addSave(customerId(), kitchen)
    addView(bedroom)
    addView(bedroom, "2026-11-04 12:00:00")
    return {"kitchen": kitchen, "bedroom": bedroom}


# ---------- IDPAnalytics.getCategoryReport() ----------

def test_ut46_1_getCategoryReport_oneDay_rankedByViewsThenSaves():
    sampleData()
    rows = IDPAnalytics().getCategoryReport(date(2026, 11, 5), date(2026, 11, 5))
    assert [(row.categoryName, row.views, row.saves) for row in rows] == \
        [("Kitchen", 3, 1), ("Bedroom", 1, 0), ("Bathroom", 0, 0)]


def test_ut46_2_getCategoryReport_otherDaysNotCounted():
    sampleData()
    rows = IDPAnalytics().getCategoryReport(date(2026, 11, 4), date(2026, 11, 4))
    assert (rows[0].categoryName, rows[0].views) == ("Bedroom", 1)
    assert IDPAnalytics().getCategoryReport(date(2026, 11, 6), date(2026, 11, 6))[0].views == 0


def test_ut46_3_getCategoryReport_tieOnViews_moreSavesFirst():
    designer = createDesigner()
    kitchen = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    bedroom = addIDP(designer, createCategory("Bedroom"), "Cozy Bedroom")
    addView(kitchen)
    addView(bedroom)
    addSave(customerId(), bedroom)
    rows = IDPAnalytics().getCategoryReport(date(2026, 11, 5), date(2026, 11, 5))
    assert [row.categoryName for row in rows] == ["Bedroom", "Kitchen"]


def test_ut46_4_getCategoryReport_showsStatusAndActiveIDPCount():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    addIDP(designer, kitchen, "One")
    addIDP(designer, kitchen, "Two")
    addIDP(designer, kitchen, "Deleted", status="Suspended")
    createCategory("Old Style", "Suspended")
    rows = {row.categoryName: row for row in
            IDPAnalytics().getCategoryReport(date(2026, 11, 5), date(2026, 11, 5))}
    assert rows["Kitchen"].totalIDPs == 2
    assert rows["Old Style"].status == "Suspended"


def test_ut46_5_getCategoryReport_usesLocalDate():
    # 20:00 UTC on 5 Nov - the report must use the date it was on this computer's clock
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    addView(idpId, "2026-11-05 20:00:00")
    localDay = datetime(2026, 11, 5, 20, tzinfo=timezone.utc).astimezone().date()
    assert IDPAnalytics().getCategoryReport(localDay, localDay)[0].views == 1
    otherDay = localDay + timedelta(days=1) if localDay.day == 5 else localDay - timedelta(days=1)
    assert IDPAnalytics().getCategoryReport(otherDay, otherDay)[0].views == 0


# ---------- GenerateDailyReportController.generateDailyReport() ----------

def test_ut46_6_controller_oneEntityCall_returnsReportUnchanged(monkeypatch):
    calls = []
    report = IDPAnalytics(startDate=date(2026, 11, 5), endDate=date(2026, 11, 5))
    monkeypatch.setattr(IDPAnalytics, "getDailyReport",
                        lambda self, selectedDate: calls.append(selectedDate) or report)
    assert GenerateDailyReportController().generateDailyReport(date(2026, 11, 5)) is report
    assert calls == [date(2026, 11, 5)]


# ---------- GenerateDailyReportPage (through the Flask route) ----------

def test_ut46_7_page_open_showsDateBoxWithTodayAndNoReport():
    html = loggedInManager().get("/manager/reports/daily").get_data(as_text=True)
    assert f'value="{date.today().isoformat()}"' in html
    assert "<table" not in html


def test_ut46_8_page_generate_showsRankedTable():
    sampleData()
    response = loggedInManager().get("/manager/reports/daily?date=2026-11-05")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "05 Nov 2026" in html and " to " not in html
    assert html.index("Kitchen") < html.index("Bedroom") < html.index("Bathroom")


def test_ut46_9_page_invalidDate_showsError():
    response = loggedInManager().get("/manager/reports/daily?date=2026-02-30")
    assert response.status_code == 400
    assert MSG_INVALID_DATE in response.get_data(as_text=True)
    assert "<table" not in response.get_data(as_text=True)


def test_ut46_10_page_futureDate_showsError():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = loggedInManager().get("/manager/reports/daily?date=" + tomorrow)
    assert response.status_code == 400
    assert MSG_FUTURE_DATE.replace("'", "&#39;") in response.get_data(as_text=True)


def test_ut46_11_page_noActivity_showsMessageAndZeroTable():
    createCategory("Kitchen")
    html = loggedInManager().get("/manager/reports/daily?date=2026-11-05").get_data(as_text=True)
    assert MSG_NO_ACTIVITY in html and "Kitchen" in html


def test_ut46_12_page_notLoggedIn_redirectsToManagerLogin():
    response = app.test_client().get("/manager/reports/daily")
    assert response.status_code == 302
    assert "/manager/login" in response.headers["Location"]


def test_ut46_13_dashboardAndMenu_linkToReports():
    client = loggedInManager()
    dashboard = client.get("/manager/dashboard").get_data(as_text=True)
    assert 'href="/manager/reports/daily"' in dashboard
    assert 'href="/manager/reports/weekly"' in dashboard and 'href="/manager/reports/monthly"' in dashboard
    menu = client.get("/manager/categories").get_data(as_text=True)
    assert 'href="/manager/reports/daily"' in menu


# ---------- IDPAnalytics.getDailyReport() ----------

def test_ut46_14_getDailyReport_periodIsJustThatDay():
    sampleData()
    report = IDPAnalytics().getDailyReport(date(2026, 11, 5))
    assert isinstance(report, IDPAnalytics)
    assert report.startDate == report.endDate == date(2026, 11, 5)
    first = report.categories[0]
    assert (first.categoryName, first.views, first.saves) == ("Kitchen", 3, 1)


# ---------- GenerateDailyReportPage.validateDate() / displayReport() ----------

def test_ut46_15_validateDate_onlyStrictYearMonthDay():
    page = GenerateDailyReportPage()
    assert page.validateDate("20261105") == MSG_INVALID_DATE
    assert page.validateDate("2026-W45-4") == MSG_INVALID_DATE
    assert page.validateDate("2026-11-05") is None


def test_ut46_16_page_withActivity_noNoActivityMessage():
    sampleData()
    html = loggedInManager().get("/manager/reports/daily?date=2026-11-05").get_data(as_text=True)
    assert "<table" in html and MSG_NO_ACTIVITY not in html
