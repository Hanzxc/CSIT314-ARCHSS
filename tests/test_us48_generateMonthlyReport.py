# Unit tests for US48 Generate monthly report.
# conftest.py gives each test a fresh database. Helpers come from the US37 and US46 tests.

from datetime import date

from control.generateMonthlyReportController import GenerateMonthlyReportController
from boundary.generateMonthlyReportPage import MSG_INVALID_DATE
from test_us37_viewIDPViewStatistics import addView, addSave, customerId
from test_us46_generateDailyReport import sampleData, loggedInManager, table


# ---------- GenerateMonthlyReportController.generateMonthlyReport() ----------

def test_ut48_1_controller_firstToLastDayOfMonth():
    report = GenerateMonthlyReportController().generateMonthlyReport(date(2026, 11, 17))
    assert (report["startDate"], report["endDate"]) == (date(2026, 11, 1), date(2026, 11, 30))


def test_ut48_2_controller_decemberAndLeapFebruary():
    controller = GenerateMonthlyReportController()
    december = controller.generateMonthlyReport(date(2026, 12, 31))
    assert (december["startDate"], december["endDate"]) == (date(2026, 12, 1), date(2026, 12, 31))
    february = controller.generateMonthlyReport(date(2028, 2, 3))
    assert february["endDate"] == date(2028, 2, 29)


def test_ut48_3_controller_countsTheWholeMonthOnly():
    ids = sampleData()
    addView(ids["bedroom"], "2026-11-30 12:00:00")    # still November
    addView(ids["bedroom"], "2026-10-31 12:00:00")    # October - not counted
    addSave(customerId(), ids["bedroom"], "2026-11-20 12:00:00")
    report = GenerateMonthlyReportController().generateMonthlyReport(date(2026, 11, 5))
    assert table(report["categories"]) == [("Bedroom", 3, 1), ("Kitchen", 3, 1), ("Bathroom", 0, 0)]


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
