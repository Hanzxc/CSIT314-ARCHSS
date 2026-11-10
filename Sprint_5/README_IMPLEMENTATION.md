# Sprint 5 - US37, US38, US46, US47, US48

Rewritten on 6 Nov 2026 to follow the same pattern as US20 / US41 - US45: one boundary page and one
controller per user story, camelCase names, and no extra login re-check inside the use case (being
logged in is the precondition - lecturer feedback). The first version (one shared `IDPAnalyticsPage` /
`IDPAnalyticsController` for all five stories) is in commit `c12e75f`.

| Story | Page (boundary) | Controller | Route |
|---|---|---|---|
| US37 View IDP view statistics | `ViewIDPViewStatisticsPage` | `ViewIDPViewStatisticsController` | `/designer/idps/statistics/views` |
| US38 View IDP save statistics | `ViewIDPSaveStatisticsPage` | `ViewIDPSaveStatisticsController` | `/designer/idps/statistics/saves` |
| US46 Generate daily report | `GenerateDailyReportPage` | `GenerateDailyReportController` | `/manager/reports/daily?date=YYYY-MM-DD` |
| US47 Generate weekly report | `GenerateWeeklyReportPage` | `GenerateWeeklyReportController` | `/manager/reports/weekly?date=...` |
| US48 Generate monthly report | `GenerateMonthlyReportPage` | `GenerateMonthlyReportController` | `/manager/reports/monthly?date=...` |

All five use one entity, `IDPAnalytics` (`entity/idpAnalytics.py`), the same way `IDP` is shared by
US20 - US29: `getViewStatistics(designerId)`, `getSaveStatistics(designerId)`, `getDailyReport(selectedDate)`,
`getWeeklyReport(selectedDate)`, `getMonthlyReport(selectedDate)` and `getCategoryReport(startDate, endDate)`.
It returns `IDPAnalytics` objects (a list for the statistics, one report object with `startDate`, `endDate`
and `categories` for the reports), never dicts. Each controller is one call to the entity.

## How the numbers are counted
- **Views (US37, US46 - US48):** every time a customer opens an IDP in US32 View IDP, `IDP.viewIDP()` adds
  one row to `idp_view` (only for an IDP customers can see). Refreshing counts again; the redirect after a
  US33 Save (`?saved=1`) doesn't count.
- **Saves (US38, US46 - US48):** read from `saved_idp`, which US33 Save IDP fills. Each customer is counted
  once per IDP.
- **Report periods:** daily = that day, weekly = Monday to Sunday of that week, monthly = 1st to last day.
  The entity (`getDailyReport` / `getWeeklyReport` / `getMonthlyReport`) works out the period; the page only
  checks the date (a real `YYYY-MM-DD` date, not in the future).
- **Time zone:** the database stores UTC (`CURRENT_TIMESTAMP`); the report compares local dates
  (`date(..., 'localtime')`), so a Singapore "today" report includes views from before 8am.

## Files
- Code: `boundary/viewIDP*StatisticsPage.py`, `boundary/generate*ReportPage.py`, matching controllers in
  `control/`, `entity/idpAnalytics.py`, templates `idpStatistics.html` and `idpCategoryReport.html`.
- Tests: `tests/test_us37_viewIDPViewStatistics.py`, `test_us38_...`, `test_us46_...`, `test_us47_...`,
  `test_us48_...` (one per story; US47/US48 reuse the helpers in the US46 file).
- Docs: `Sprint_5/US37 - .../` to `US48 - .../` - each has the `.drawio` (Use Case, wireframe, BCE and
  Sequence pages), the exported PNGs in `diagrams/`, the use case description `.docx` and a `README.md`.
