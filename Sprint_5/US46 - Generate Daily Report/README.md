# US46 — Generate daily report

> As a platform manager, I want to generate a daily report so that I can see which IDP categories were most popular on a selected day.

## Behaviour

- "Reports" in the side menu (or the Daily tab) opens the page (`clickGenerateDailyReport()` → `displayReportForm()`): the "Day" date box starts on today and no report is shown yet (wireframe 4a).
- "Generate report" sends GET `/manager/reports/daily?date=YYYY-MM-DD` → `submitDate(selectedDate)`. The page trims the date and runs `validateDate(selectedDate)`, which returns `error`:
  - not a real `YYYY-MM-DD` date (checked with `datetime.strptime(selectedDate, "%Y-%m-%d")`, so `2026-02-30`, `20261105` and `2026-W45-4` are rejected) → `MSG_INVALID_DATE`;
  - after today → `MSG_FUTURE_DATE`;
  - otherwise `None`.
- `error != None` → `displayErrorMessage(error)`: HTTP 400, the form again with the red message (wireframe 4d). The controller is never called.
- `error == None` → `generateDailyReport(selectedDate)` → `IDPAnalytics.getDailyReport(selectedDate)`. The entity works out the period itself - just that day (`startDate` and `endDate` are both `selectedDate`) - calls its own `getCategoryReport(startDate, endDate)` and returns `report`, an `IDPAnalytics` with `startDate`, `endDate` and `categories` (`list[IDPAnalytics]`). The controller returns it unchanged.
- The page shows "Period: 05 Nov 2026" and every IDP category (Active or Suspended) with its status, number of Active IDPs, views and saves in the period, ranked by views, then saves, then name (`displayReport(report)`, wireframe 4b, hint "Ranked by views, then saves."). When every category has 0 views and 0 saves → `displayReport(report, MSG_NO_ACTIVITY)`: the message above the table of zeros (wireframe 4c).
- Views come from UC32 View IDP (`idp_view`) and saves from UC33 Save IDP (`saved_idp`). Times are stored in UTC and compared as local dates, both ends of the period included. Nothing is changed (read only).
- The Daily | Weekly | Monthly tabs switch between US46, US47 and US48 on the same template.

## Who checks what

- **Boundary** (`GenerateDailyReportPage`): the only input is the date - it trims it and checks it (`validateDate`: a real `YYYY-MM-DD` date, not after today), then picks what to show: the report, the report with `MSG_NO_ACTIVITY`, or the error (HTTP 400).
- **Control** (`GenerateDailyReportController`): `generateDailyReport(selectedDate)` just calls `IDPAnalytics().getDailyReport(selectedDate)` and returns the report unchanged - one call, no checks, no period maths.
- **Entity** (`IDPAnalytics`): `getDailyReport(selectedDate)` works out `startDate` and `endDate`; `getCategoryReport(startDate, endDate)` reads every category with its Active IDP count, views and saves in the period.
- Precondition: logged in as a Platform Manager (UC39). `managerLoginRequired` in `app.py` only sends someone with no session to `/manager/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `GenerateDailyReportPage` — `clickGenerateDailyReport()`, `displayReportForm()`, `submitDate(selectedDate)`, `validateDate(selectedDate): str \| None`, `displayReport(report, msg=None)`, `displayErrorMessage(msg)`; attributes `generateDailyReportController`, `selectedDate` | `boundary/generateDailyReportPage.py`, `templates/idpCategoryReport.html`, `templates/platformManagerBase.html` |
| Control `GenerateDailyReportController` — `generateDailyReport(selectedDate): IDPAnalytics` | `control/generateDailyReportController.py` |
| Entity `IDPAnalytics` — `getDailyReport(selectedDate): IDPAnalytics`, `getCategoryReport(startDate, endDate): list[IDPAnalytics]`; attributes idpId, title, projectType, categoryId, categoryName, status, views, saves, totalIDPs, startDate, endDate, categories | `entity/idpAnalytics.py` (tables `idp_category`, `idp`, `idp_view`, `saved_idp`) |
| Route | GET `/manager/reports/daily` → `generateDailyReport()` in `app.py` (`@managerLoginRequired`): no `?date=` → `clickGenerateDailyReport()`, with `?date=` → `submitDate(date)` |

Messages: `MSG_INVALID_DATE` "Please choose a valid date", `MSG_FUTURE_DATE` "The date can't be in the future", `MSG_NO_ACTIVITY` "No IDPs were viewed or saved in this period".

## Files

- `US46 Generate daily report.drawio` — every diagram, one page each
- `US46 Generate daily report.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Date form.png`
  - `4b Wireframe - Report.png`
  - `4c Wireframe - No activity.png`
  - `4d Wireframe - Invalid date.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us46_generateDailyReport.py -v
```
