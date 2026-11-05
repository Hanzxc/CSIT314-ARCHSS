# US43 — Update IDP category

> As a platform manager, I want to update an IDP category so that its name and details stay up to date.

## Behaviour

- Following the lecturer's feedback (the same way Sprint 1 and 2 were changed): the boundary trims and checks all the input, the controller just calls the entity and returns the result (no canXxx() access methods), the entity does the duplicate / still-Active checks, an entity object is passed around instead of a dict, and each B-C-E diagram has only one entity.
- Being logged in as a Platform Manager (UC39) is the precondition of these use cases, so the pages and the B-C-E / sequence diagrams don't check the manager again (no PlatformManagerLoginController). managerLoginRequired in app.py only sends someone with no session to /manager/login.
- The manager starts from the category details page (US42) and clicks "Update". The form is filled in with the current name and description.
- The same rules as US41 apply: name 3-50 characters and unique (ignoring capitals), description up to 500. Keeping the category's own name is allowed.
- Only the name and description change. The status is shown but can't be edited here - it is changed by US44. Updating a Suspended category keeps it Suspended.
- The IDPs in the category are not changed, so they show under the new name straight away.

## Lecturer feedback changes

- **Boundary checks everything.** The page trims the input, puts it in an entity object and checks every field itself (`validateInput()`).
- **The controller just calls the entity** and returns the result. It doesn't re-check the input and has no `canXxx()` access methods.
- **The entity checks for duplicates / still-Active rows** (e.g. a taken category name, a category suspended meanwhile).
- **An entity object is passed around, not a `{}` dict.**
- **One entity per B-C-E diagram.**
- **No reload before saving.** `submitUpdate()` goes straight to update instead of loading the category again first - categories can't be deleted, so the only way the update fails is the name being taken. The status badge is shown on the first form only (status isn't part of the form).
- **Precondition, no double check.** Being logged in is the precondition, so the B-C-E and sequence diagrams no longer re-check the user with the US13 / US39 login controller. `designerLoginRequired` and `managerLoginRequired` in `app.py` only send someone with no session to the login page.

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

- `app.py` — imports and routes for US20 and US40 - US45, and `managerLoginRequired` (only sends someone with no session to `/manager/login`, like `designerLoginRequired`); no existing route changed
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `UpdateIDPCategoryPage` | `boundary/updateIDPCategoryPage.py` |
| Control `UpdateIDPCategoryController` | `control/updateIDPCategoryController.py` |
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
