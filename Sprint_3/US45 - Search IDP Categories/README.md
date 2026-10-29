# US45 — Search IDP categories

> As a platform manager, I want to search for IDP categories so that I can find the category I need to manage.

## Behaviour

- Only an active Platform Manager can use the IDP category pages: the account and its profile must both be Active and the profile must have the "Manage IDP categories" and "Generate reports" permissions. This is checked again from the database on every request with the US39 PlatformManagerLoginController.getAuthenticatedManager(). Someone not logged in goes to /manager/login; anyone else gets "Access unavailable" (HTTP 403).
- The search page is also the IDP Categories list (/manager/categories): an empty search shows every category, the same way the User Profiles list is the US7 search page.
- The keyword is matched against the name and the description. Capitals and spaces around the keyword don't matter.
- Suspended categories are included in the results, because the manager still needs to find them.
- Results are shown in the order the categories were created, with the name, description, status and a "View" link (US42).

## Repository files

New files for this story:

```text
boundary/searchIDPCategoryPage.py
control/searchIDPCategoryController.py
templates/idpCategories.html
tests/test_us45_searchIDPCategories.py
Sprint_3/US45 - Search IDP Categories/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `SearchIDPCategoryPage` | `boundary/searchIDPCategoryPage.py` |
| Control `SearchIDPCategoryController` | `control/searchIDPCategoryController.py` |
| Reused control `PlatformManagerLoginController` | Existing US39 `control/platformManagerLoginController.py` |
| Entity `IDPCategory` | `entity/idpCategory.py` |
| Route | GET `/manager/categories?keyword=...` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US45 Search IDP categories.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - All categories.png
  4b Wireframe - Search results.png
  4c Wireframe - No results.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 6 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us45_searchIDPCategories.py -v
python -m pytest -q
```
