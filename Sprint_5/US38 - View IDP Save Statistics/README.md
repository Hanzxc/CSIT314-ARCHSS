# US38 — View IDP save statistics

> As an interior designer, I want to see how many users have saved each of my IDPs so that I can tell which IDPs people are interested in.

## Behaviour

- The "Saves" tab on the IDP Statistics page (`clickViewIDPSaves()`) calls `getSaveStatistics(designerId)` with `designerId = session["userId"]`.
- The controller makes one call to `IDPAnalytics.getSaveStatistics(designerId)` and returns `statistics` (a `list[IDPAnalytics]`) unchanged.
- `statistics` is not empty → `displayStatistics(statistics)` (wireframe 4a): a table of the designer's own Active IDPs (current and past) with IDP, Category, Type and Customers who saved it, most saved first. An IDP nobody has saved shows 0. Hint under the table: "Each customer who saved the IDP is counted once."
- `statistics` is empty → `displayNoIDPsMessage(MSG_NO_IDPS)` (wireframe 4b): "You don't have any active IDPs yet, so there are no saves to show", no table.
- Saves are added by UC33 Save IDP (`SavedIDP.createSavedRecord`) into `saved_idp`; each customer is counted once and views don't count. Deleted (Suspended) IDPs and other designers' IDPs are never shown. The "Views" tab on the same page is US37.

## Who checks what

- **Boundary** (`ViewIDPSaveStatisticsPage`): takes the designer from the session and picks what to show (table or `MSG_NO_IDPS`) - there is no typed input.
- **Control** (`ViewIDPSaveStatisticsController`): `getSaveStatistics(designerId)` just calls the entity and returns the result - no checks.
- **Entity** (`IDPAnalytics`): `getSaveStatistics(designerId)` returns one `IDPAnalytics` per Active IDP owned by the designer (idpId, title, projectType, categoryName, saves = number of different customers who saved it), most saved first.
- Precondition: logged in as an Interior Designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewIDPSaveStatisticsPage` — `clickViewIDPSaves()`, `displayStatistics(statistics)`, `displayNoIDPsMessage(msg)` | `boundary/viewIDPSaveStatisticsPage.py`, `templates/idpStatistics.html`, `templates/interiorDesignerBase.html` |
| Control `ViewIDPSaveStatisticsController` — `getSaveStatistics(designerId): list[IDPAnalytics]` | `control/viewIDPSaveStatisticsController.py` |
| Entity `IDPAnalytics` — `getSaveStatistics(designerId): list[IDPAnalytics]` | `entity/idpAnalytics.py` (tables `idp`, `idp_category`, `saved_idp`) |
| Route | GET `/designer/idps/statistics/saves` → `viewIDPSaveStatistics()` in `app.py` (`@designerLoginRequired`) |

Message: `MSG_NO_IDPS` "You don't have any active IDPs yet, so there are no saves to show".

## Files

- `US38 View IDP save statistics.drawio` — every diagram, one page each
- `US38 View IDP save statistics.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Statistics table.png`
  - `4b Wireframe - No IDPs yet.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us38_viewIDPSaveStatistics.py -v
```
