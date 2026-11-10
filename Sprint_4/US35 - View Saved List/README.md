# US35 — View saved list

> As a customer, I want to view my saved list so that I can see all the IDPs I have saved.

## Behaviour

- "Saved IDPs" on the customer dashboard or the sidebar opens GET `/customer/saved-list`.
- `openSavedList()` → `getSavedList(customerId)` (controller, `customerId = session["userId"]`) → `SavedIDP.getSavedRecords(customerId)` → `savedIDPs`.
- The entity returns the customer's saved IDPs as IDP objects (with `categoryName`), only Active IDPs in Active categories, most recently saved first. A saved IDP that was deleted or whose category was suspended is left out (its `saved_idp` row stays).
- `[savedIDPs is not empty]` → `displaySavedProjects(savedIDPs)`: one card per IDP with title, category, location, project type and View (wireframe 4a). View opens the IDP's details (US32).
- `[nothing saved yet]` → `displayEmptyMessage(MSG_NO_SAVED)`: "You have not saved any IDPs yet" (wireframe 4b).
- The search bar on the same page is US34. Managing the saved list means saving (US33), viewing (US35) and searching (US34) only - there is no remove / unsave. Viewing never changes any data.

## Who checks what

- **Boundary** (`SavedListPage`, shared with US34): there is no typed input - it passes the logged-in customer's id and shows the list or the empty message.
- **Control** (`ViewSavedListController`): `getSavedList(customerId)` just calls `SavedIDP().getSavedRecords(customerId)` and returns the list - no checks.
- **Entity** (`SavedIDP`): reads only this customer's saved list and leaves out IDPs customers can't see.
- Precondition: logged in as a Customer (UC30). `customerLoginRequired` in `app.py` only sends someone with no session to `/customer/login`. The role isn't checked again (no `CustomerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SavedListPage` — attribute `viewSavedListController`; `openSavedList()`, `displaySavedProjects(savedIDPs)`, `displayEmptyMessage(msg)` | `boundary/savedListPage.py`, `templates/savedList.html` |
| Control `ViewSavedListController` — `getSavedList(customerId): list` | `control/viewSavedListController.py` |
| Entity `SavedIDP` — attributes `savedId`, `customerId`, `idpId`, `savedDate`; `getSavedRecords(customerId): list` (IDP objects) | `entity/savedIDP.py` (tables `saved_idp`, `idp`, `idp_category`) |
| Route | GET `/customer/saved-list` (`@customerLoginRequired`) → `savedList()` in `app.py` |

Messages: `MSG_NO_SAVED` "You have not saved any IDPs yet".

## Files

- `US35 View saved list.drawio` — every diagram, one page each
- `US35 View saved list.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Saved list.png`
  - `4b Wireframe - Nothing saved yet.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us35_viewSavedList.py -v
```
