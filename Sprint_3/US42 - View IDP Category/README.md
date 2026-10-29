# US42 — View IDP category

> As a platform manager, I want to view IDP categories and the IDPs in them so that I can check whether IDPs are grouped correctly.

## Behaviour

- Only an active Platform Manager can use the IDP category pages: the account and its profile must both be Active and the profile must have the "Manage IDP categories" and "Generate reports" permissions. This is checked again from the database on every request with the US39 PlatformManagerLoginController.getAuthenticatedManager(). Someone not logged in goes to /manager/login; anyone else gets "Access unavailable" (HTTP 403).
- The manager opens a category from the IDP Categories list (US45) by clicking "View".
- The details page shows the name, the status badge, the description and every Active IDP that is grouped in the category (title, type and location), newest first. This lets the manager check that IDPs are grouped correctly.
- IDPs are added to a category by designers (US20). Suspended categories can still be viewed.
- The Update (US43) and Suspend (US44) buttons start from this page.

## Repository files

New files for this story:

```text
boundary/viewIDPCategoryPage.py
control/viewIDPCategoryController.py
entity/idp.py
templates/viewIDPCategory.html
tests/test_us42_viewIDPCategory.py
Sprint_3/US42 - View IDP Category/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `ViewIDPCategoryPage` | `boundary/viewIDPCategoryPage.py` |
| Control `ViewIDPCategoryController` | `control/viewIDPCategoryController.py` |
| Reused control `PlatformManagerLoginController` | Existing US39 `control/platformManagerLoginController.py` |
| Entity `IDPCategory` | `entity/idpCategory.py` |
| Entity `IDP` | `entity/idp.py`, table `idp` in `database/schema.sql` |
| Route | GET `/manager/categories/<categoryId>` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US42 View IDP category.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Categories list.png
  4b Wireframe - Category details.png
  4c Wireframe - No IDPs yet.png
  4d Wireframe - Category not found.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 7 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us42_viewIDPCategory.py -v
python -m pytest -q
```
