# US43 — Update IDP category

> As a platform manager, I want to update an IDP category so that its name and details stay up to date.

## Behaviour

- Only an active Platform Manager can use the IDP category pages: the account and its profile must both be Active and the profile must have the "Manage IDP categories" and "Generate reports" permissions. This is checked again from the database on every request with the US39 PlatformManagerLoginController.getAuthenticatedManager(). Someone not logged in goes to /manager/login; anyone else gets "Access unavailable" (HTTP 403).
- The manager starts from the category details page (US42) and clicks "Update". The form is filled in with the current name and description.
- The same rules as US41 apply: name 3-50 characters and unique (ignoring capitals), description up to 500. Keeping the category's own name is allowed.
- Only the name and description change. The status is shown but can't be edited here - it is changed by US44. Updating a Suspended category keeps it Suspended.
- The IDPs in the category are not changed, so they show under the new name straight away.

## Repository files

New files for this story:

```text
boundary/updateIDPCategoryPage.py
control/updateIDPCategoryController.py
templates/updateIDPCategory.html
tests/test_us43_updateIDPCategory.py
Sprint_3/US43 - Update IDP Category/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `UpdateIDPCategoryPage` | `boundary/updateIDPCategoryPage.py` |
| Control `UpdateIDPCategoryController` | `control/updateIDPCategoryController.py` |
| Reused control `PlatformManagerLoginController` | Existing US39 `control/platformManagerLoginController.py` |
| Entity `IDPCategory` | `entity/idpCategory.py` |
| Route | GET/POST `/manager/categories/<categoryId>/update` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US43 Update IDP category.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Update button.png
  4b Wireframe - Update form.png
  4c Wireframe - Name already used.png
  4d Wireframe - Category updated.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 7 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us43_updateIDPCategory.py -v
python -m pytest -q
```
