# US37 — View IDP view statistics

> As an interior designer, I want to see how many views each of my IDPs has so that I can tell which IDPs get the most attention.

## Behaviour

- "IDP Statistics" in the side menu, "View IDP statistics" on the dashboard or the "Views" tab (`clickViewIDPViews()`) calls `getViewStatistics(designerId)` with `designerId = session["userId"]`.
- The controller makes one call to `IDPAnalytics.getViewStatistics(designerId)` and returns `statistics` (a `list[IDPAnalytics]`) unchanged.
- `statistics` is not empty → `displayStatistics(statistics)` (wireframe 4a): a table of the designer's own Active IDPs (current and past) with IDP, Category, Type and Views, most viewed first. An IDP no customer has opened shows 0. Hint under the table: "A view is counted each time a customer opens the IDP."
- `statistics` is empty → `displayNoIDPsMessage(MSG_NO_IDPS)` (wireframe 4b): "You don't have any active IDPs yet, so there are no views to show", no table.
- Views are recorded by UC32 View IDP (`IDP.viewIDP`): one `idp_view` row each time a customer opens an IDP. US37 only counts them. Deleted (Suspended) IDPs and other designers' IDPs are never shown. The "Saves" tab on the same page is US38.

## Who checks what

- **Boundary** (`ViewIDPViewStatisticsPage`): takes the designer from the session and picks what to show (table or `MSG_NO_IDPS`) - there is no typed input.
- **Control** (`ViewIDPViewStatisticsController`): `getViewStatistics(designerId)` just calls the entity and returns the result - no checks.
- **Entity** (`IDPAnalytics`): `getViewStatistics(designerId)` returns one `IDPAnalytics` per Active IDP owned by the designer (idpId, title, projectType, categoryName, views), most viewed first.
- Precondition: logged in as an Interior Designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewIDPViewStatisticsPage` — `clickViewIDPViews()`, `displayStatistics(statistics)`, `displayNoIDPsMessage(msg)` | `boundary/viewIDPViewStatisticsPage.py`, `templates/idpStatistics.html`, `templates/interiorDesignerBase.html` |
| Control `ViewIDPViewStatisticsController` — `getViewStatistics(designerId): list[IDPAnalytics]` | `control/viewIDPViewStatisticsController.py` |
| Entity `IDPAnalytics` — `getViewStatistics(designerId): list[IDPAnalytics]` | `entity/idpAnalytics.py` (tables `idp`, `idp_category`, `idp_view`) |
| Route | GET `/designer/idps/statistics/views` → `viewIDPViewStatistics()` in `app.py` (`@designerLoginRequired`) |

Message: `MSG_NO_IDPS` "You don't have any active IDPs yet, so there are no views to show".

## Files

- `US37 View IDP view statistics.drawio` — every diagram, one page each
- `US37 View IDP view statistics.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Statistics table.png`
  - `4b Wireframe - No IDPs yet.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us37_viewIDPViewStatistics.py -v
```
