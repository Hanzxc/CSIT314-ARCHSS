# US44 — Suspend IDP category

> As a platform manager, I want to suspend an IDP category so that users can no longer see or select it.

## Behaviour

- Only an active Platform Manager can use the IDP category pages: the account and its profile must both be Active and the profile must have the "Manage IDP categories" and "Generate reports" permissions. This is checked again from the database on every request with the US39 PlatformManagerLoginController.getAuthenticatedManager(). Someone not logged in goes to /manager/login; anyone else gets "Access unavailable" (HTTP 403).
- The manager starts from the category details page (US42). The "Suspend" button is only shown while the category is Active.
- Suspending asks "Are you sure?" first. The box is plain HTML on the details page (no JavaScript), like US6 and US11.
- "Users can no longer see or select it": a Suspended category is not in the designer's IDP category drop-down (US20), and a form posted with its id is rejected.
- Suspending keeps the category row and the IDPs already in it - nothing is deleted. The manager can still find it with the search (US45) and view it (US42).
- A category that is already Suspended, or doesn't exist, can't be suspended.

## Repository files

New files for this story:

```text
boundary/suspendIDPCategoryPage.py
control/suspendIDPCategoryController.py
tests/test_us44_suspendIDPCategory.py
Sprint_3/US44 - Suspend IDP Category/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `SuspendIDPCategoryPage` | `boundary/suspendIDPCategoryPage.py` (box in `templates/viewIDPCategory.html`) |
| Control `SuspendIDPCategoryController` | `control/suspendIDPCategoryController.py` |
| Reused controls | US39 `PlatformManagerLoginController`, US42 `ViewIDPCategoryController` |
| Entity `IDPCategory` | `entity/idpCategory.py` |
| Route | GET/POST `/manager/categories/<categoryId>/suspend` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US44 Suspend IDP category.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Suspend button.png
  4b Wireframe - Confirm suspend.png
  4c Wireframe - Category suspended.png
  4d Wireframe - Not selectable.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 7 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us44_suspendIDPCategory.py -v
python -m pytest -q
```
