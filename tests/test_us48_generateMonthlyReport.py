# Unit tests for US48 Generate monthly report.
# conftest.py gives each test a fresh database. Helpers come from the US37 and US46 tests.

from datetime import date

from entity.idpAnalytics import IDPAnalytics
from control.generateMonthlyReportController import GenerateMonthlyReportController
from boundary.generateMonthlyReportPage import GenerateMonthlyReportPage, MSG_INVALID_DATE, MSG_NO_ACTIVITY
from test_us37_viewIDPViewStatistics import addView, addSave, customerId, createCategory
from test_us46_generateDailyReport import sampleData, loggedInManager


# ---------- IDPAnalytics.getMonthlyReport() ----------

def test_ut48_1_getMonthlyReport_firstToLastDayOfMonth():
    report = IDPAnalytics().getMonthlyReport(date(2026, 11, 17))
    assert (report.startDate, report.endDate) == (date(2026, 11, 1), date(2026, 11, 30))


def test_ut48_2_getMonthlyReport_decemberAndLeapFebruary():
    december = IDPAnalytics().getMonthlyReport(date(2026, 12, 31))
    assert (december.startDate, december.endDate) == (date(2026, 12, 1), date(2026, 12, 31))
    assert IDPAnalytics().getMonthlyReport(date(2028, 2, 3)).endDate == date(2028, 2, 29)


def test_ut48_3_getMonthlyReport_countsTheWholeMonthOnly():
    ids = sampleData()
    addView(ids["bedroom"], "2026-11-30 12:00:00")    # still November
    addView(ids["bedroom"], "2026-10-31 12:00:00")    # October - not counted
    addSave(customerId(), ids["bedroom"], "2026-11-20 12:00:00")
    report = IDPAnalytics().getMonthlyReport(date(2026, 11, 5))
    assert [(row.categoryName, row.views, row.saves) for row in report.categories] == \
        [("Bedroom", 3, 1), ("Kitchen", 3, 1), ("Bathroom", 0, 0)]


# ---------- GenerateMonthlyReportPage (through the Flask route) ----------

def test_ut48_4_page_generate_showsMonthPeriod():
    sampleData()
    response = loggedInManager().get("/manager/reports/monthly?date=2026-11-05")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "01 Nov 2026 to 30 Nov 2026" in html
    assert "Monthly Category Report" in html


def test_ut48_5_page_invalidDate_showsError():
    response = loggedInManager().get("/manager/reports/monthly?date=")
    assert response.status_code == 400
    assert MSG_INVALID_DATE in response.get_data(as_text=True)


def test_ut48_6_page_open_noReportYet():
    html = loggedInManager().get("/manager/reports/monthly").get_data(as_text=True)
    assert "Any day in the month" in html and "<table" not in html


# ---------- GenerateMonthlyReportController.generateMonthlyReport() ----------

def test_ut48_7_controller_oneEntityCall_returnsReportUnchanged(monkeypatch):
    calls = []
    report = IDPAnalytics(startDate=date(2026, 11, 1), endDate=date(2026, 11, 30))
    monkeypatch.setattr(IDPAnalytics, "getMonthlyReport",
                        lambda self, selectedDate: calls.append(selectedDate) or report)
    assert GenerateMonthlyReportController().generateMonthlyReport(date(2026, 11, 5)) is report
    assert calls == [date(2026, 11, 5)]


# ---------- GenerateMonthlyReportPage.validateDate() / displayReport() ----------

def test_ut48_8_validateDate_onlyStrictYearMonthDay():
    page = GenerateMonthlyReportPage()
    assert page.validateDate("20261105") == MSG_INVALID_DATE
    assert page.validateDate("2026-W45-4") == MSG_INVALID_DATE


def test_ut48_9_page_noActivityMessageOnlyForAnEmptyMonth():
    createCategory("Patio")
    client = loggedInManager()
    html = client.get("/manager/reports/monthly?date=2026-09-15").get_data(as_text=True)
    assert MSG_NO_ACTIVITY in html and "Patio" in html and "<strong>0</strong>" in html
    sampleData()
    html = client.get("/manager/reports/monthly?date=2026-11-05").get_data(as_text=True)
    assert "<table" in html and MSG_NO_ACTIVITY not in html
