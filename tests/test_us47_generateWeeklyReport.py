# Unit tests for US47 Generate weekly report.
# conftest.py gives each test a fresh database. Helpers come from the US37 and US46 tests.
# A week is Monday to Sunday: 5 Nov 2026 is a Thursday, so its week is 2 - 8 Nov.

from datetime import date

from control.generateWeeklyReportController import GenerateWeeklyReportController
from boundary.generateWeeklyReportPage import MSG_INVALID_DATE
from test_us37_viewIDPViewStatistics import addView
from test_us46_generateDailyReport import sampleData, loggedInManager, table


# ---------- GenerateWeeklyReportController.generateWeeklyReport() ----------

def test_ut47_1_controller_anyDayGivesMondayToSunday():
    controller = GenerateWeeklyReportController()
    for picked in (date(2026, 11, 2), date(2026, 11, 5), date(2026, 11, 8)):
        report = controller.generateWeeklyReport(picked)
        assert (report["startDate"], report["endDate"]) == (date(2026, 11, 2), date(2026, 11, 8))


def test_ut47_2_controller_weekCrossingMonthAndYear():
    report = GenerateWeeklyReportController().generateWeeklyReport(date(2026, 12, 31))
    assert (report["startDate"], report["endDate"]) == (date(2026, 12, 28), date(2027, 1, 3))


def test_ut47_3_controller_countsTheWholeWeek():
    ids = sampleData()                       # Bedroom: views on 4 and 5 Nov
    addView(ids["kitchen"], "2026-11-01 12:00:00")    # Sunday before - other week
    report = GenerateWeeklyReportController().generateWeeklyReport(date(2026, 11, 5))
    assert table(report["categories"]) == [("Kitchen", 3, 1), ("Bedroom", 2, 0), ("Bathroom", 0, 0)]


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
