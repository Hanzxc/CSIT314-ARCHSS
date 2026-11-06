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
US20 - US29: `getViewStatistics`, `getSaveStatistics`, `getCategoryReport(startDate, endDate)` and
`recordView(idpId)`.

## How the numbers are counted
- **Views (US37, US46 - US48):** every time a customer opens an IDP in US32 View IDP,
  `ViewIDPController.viewIDP()` calls `IDPAnalytics.recordView()`, which adds one row to `idp_view`.
  Only Active IDPs in Active categories are counted. Refreshing counts again.
- **Saves (US38, US46 - US48):** read from `saved_idp`, which US33 Save IDP fills. Unsaving deletes the
  row, so it's "customers who have it saved now", not a history of every save.
- **Report periods:** daily = that day, weekly = Monday to Sunday of that week, monthly = 1st to last day.
  The controller works out the period; the page only checks the date (real date, not in the future).
- **Time zone:** the database stores UTC (`CURRENT_TIMESTAMP`); the report compares local dates
  (`date(..., 'localtime')`), so a Singapore "today" report includes views from before 8am.

## Files
- Code: `boundary/viewIDP*StatisticsPage.py`, `boundary/generate*ReportPage.py`, matching controllers in
  `control/`, `entity/idpAnalytics.py`, templates `idpStatistics.html` and `idpCategoryReport.html`.
- Tests: `tests/test_us37_viewIDPViewStatistics.py`, `test_us38_...`, `test_us46_...`, `test_us47_...`,
  `test_us48_...` (one per story; US47/US48 reuse the helpers in the US46 file).
- Diagrams: `Sprint_5/US37 - .../` to `US48 - .../` - each has the `.drawio` (Use Case, BCE and
  Sequence pages) and the exported PNGs in `diagrams/`. They were drawn from this code.
- `User story diagram/` is the original first-draft diagrams, kept for reference only.

## Changed outside Sprint 5
- `control/viewIDPController.py` (US32): one line to record the view. US32's sequence diagram needs a
  `recordView(idpId)` call added after `getIDP(idpId)`.
- `tests/test_us32_viewIDP.py`: `test_ut32_26_readOnly` now allows the new `idp_view` row (and checks
  exactly one is added per visible IDP).
- Dashboards and side menus link to the new pages.

## Still to do
- The `.docx` write-ups and wireframes (4a, 4b, ...) for each story, like the other sprints.
