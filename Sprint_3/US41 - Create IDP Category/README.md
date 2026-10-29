# US41 — Create IDP category

> As a platform manager, I want to create an IDP category so that similar interior design IDPs can be grouped together.

## Behaviour

- Only an active Platform Manager can use the IDP category pages: the account and its profile must both be Active and the profile must have the "Manage IDP categories" and "Generate reports" permissions. This is checked again from the database on every request with the US39 PlatformManagerLoginController.getAuthenticatedManager(). Someone not logged in goes to /manager/login; anyone else gets "Access unavailable" (HTTP 403).
- An IDP category groups similar interior design projects (IDPs), e.g. Living Room or Kitchen. It has a name, an optional description and a status (Active or Suspended).
- The category name is required, 3-50 characters, and must be unique. Capitals and spaces around the name don't matter ("kITCHEN " is the same as "Kitchen"). The description is optional, up to 500 characters.
- A new category always starts Active, so designers can choose it straight away when they add an IDP (US20).
- The IDP Categories list page is the US45 search page, the same way the User Profiles list is the US7 page.
- database/seedIDPCategoryData.py adds six demo categories (Living Room, Kitchen, Bedroom, Bathroom, Home Office, Commercial).

## Repository files

New files for this story:

```text
boundary/createIDPCategoryPage.py
control/createIDPCategoryController.py
entity/idpCategory.py
templates/createIDPCategory.html
templates/platformManagerBase.html
database/seedIDPCategoryData.py
tests/test_us41_createIDPCategory.py
Sprint_3/US41 - Create IDP Category/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `CreateIDPCategoryPage` | `boundary/createIDPCategoryPage.py` |
| Control `CreateIDPCategoryController` | `control/createIDPCategoryController.py` |
| Reused control `PlatformManagerLoginController` | Existing US39 `control/platformManagerLoginController.py` |
| Entity `IDPCategory` | `entity/idpCategory.py`, table `idp_category` in `database/schema.sql` |
| Route | GET/POST `/manager/categories/create` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US41 Create IDP category.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Create button.png
  4b Wireframe - Create form.png
  4c Wireframe - Form errors.png
  4d Wireframe - Category created.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 7 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us41_createIDPCategory.py -v
python -m pytest -q
```
