# Unit tests for US47 Generate weekly report.
# conftest.py gives each test a fresh database. Helpers come from the US37 and US46 tests.
# A week is Monday to Sunday: 5 Nov 2026 is a Thursday, so its week is 2 - 8 Nov.

from datetime import date

from entity.idpAnalytics import IDPAnalytics
from control.generateWeeklyReportController import GenerateWeeklyReportController
from boundary.generateWeeklyReportPage import GenerateWeeklyReportPage, MSG_INVALID_DATE, MSG_NO_ACTIVITY
from test_us37_viewIDPViewStatistics import addView, createCategory
from test_us46_generateDailyReport import sampleData, loggedInManager


# ---------- IDPAnalytics.getWeeklyReport() ----------

def test_ut47_1_getWeeklyReport_anyDayGivesMondayToSunday():
    for picked in (date(2026, 11, 2), date(2026, 11, 5), date(2026, 11, 8)):
        report = IDPAnalytics().getWeeklyReport(picked)
        assert (report.startDate, report.endDate) == (date(2026, 11, 2), date(2026, 11, 8))


def test_ut47_2_getWeeklyReport_weekCrossingMonthAndYear():
    report = IDPAnalytics().getWeeklyReport(date(2026, 12, 31))
    assert (report.startDate, report.endDate) == (date(2026, 12, 28), date(2027, 1, 3))


def test_ut47_3_getWeeklyReport_countsTheWholeWeek():
    ids = sampleData()                       # Bedroom: views on 4 and 5 Nov
    addView(ids["kitchen"], "2026-11-01 12:00:00")    # Sunday before - other week
    report = IDPAnalytics().getWeeklyReport(date(2026, 11, 5))
    assert [(row.categoryName, row.views, row.saves) for row in report.categories] == \
        [("Kitchen", 3, 1), ("Bedroom", 2, 0), ("Bathroom", 0, 0)]


# ---------- GenerateWeeklyReportPage (through the Flask route) ----------

def test_ut47_4_page_generate_showsWeekPeriod():
    sampleData()
    response = loggedInManager().get("/manager/reports/weekly?date=2026-11-05")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "02 Nov 2026 to 08 Nov 2026" in html
    assert "Weekly Category Report" in html


def test_ut47_5_page_invalidDate_showsError():
    response = loggedInManager().get("/manager/reports/weekly?date=not-a-date")
    assert response.status_code == 400
    assert MSG_INVALID_DATE in response.get_data(as_text=True)


def test_ut47_6_page_open_noReportYet():
    html = loggedInManager().get("/manager/reports/weekly").get_data(as_text=True)
    assert "Any day in the week" in html and "<table" not in html


# ---------- GenerateWeeklyReportController.generateWeeklyReport() ----------

def test_ut47_7_controller_oneEntityCall_returnsReportUnchanged(monkeypatch):
    calls = []
    report = IDPAnalytics(startDate=date(2026, 11, 2), endDate=date(2026, 11, 8))
    monkeypatch.setattr(IDPAnalytics, "getWeeklyReport",
                        lambda self, selectedDate: calls.append(selectedDate) or report)
    assert GenerateWeeklyReportController().generateWeeklyReport(date(2026, 11, 5)) is report
    assert calls == [date(2026, 11, 5)]


# ---------- GenerateWeeklyReportPage.validateDate() / displayReport() ----------

def test_ut47_8_validateDate_onlyStrictYearMonthDay():
    page = GenerateWeeklyReportPage()
    assert page.validateDate("20261105") == MSG_INVALID_DATE
    assert page.validateDate("2026-W45-4") == MSG_INVALID_DATE


def test_ut47_9_page_noActivityMessageOnlyForAnEmptyWeek():
    createCategory("Patio")
    client = loggedInManager()
    html = client.get("/manager/reports/weekly?date=2026-10-20").get_data(as_text=True)
    assert MSG_NO_ACTIVITY in html and "Patio" in html and "<strong>0</strong>" in html
    sampleData()
    html = client.get("/manager/reports/weekly?date=2026-11-05").get_data(as_text=True)
    assert "<table" in html and MSG_NO_ACTIVITY not in html
