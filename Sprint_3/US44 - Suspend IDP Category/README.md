# US44 — Suspend IDP category

> As a platform manager, I want to suspend an IDP category so that users can no longer see or select it.

## Behaviour

- Following the lecturer's feedback (the same way Sprint 1 and 2 were changed): the boundary trims and checks all the input, the controller just calls the entity and returns the result (no canXxx() access methods), the entity does the duplicate / still-Active checks, an entity object is passed around instead of a dict, and each B-C-E diagram has only one entity.
- Being logged in as a Platform Manager (UC39) is the precondition of these use cases, so the pages and the B-C-E / sequence diagrams don't check the manager again (no PlatformManagerLoginController). managerLoginRequired in app.py only sends someone with no session to /manager/login.
- The manager starts from the category details page (US42). The "Suspend" button is only shown while the category is Active.
- Suspending asks "Are you sure?" first. The box is plain HTML on the details page (no JavaScript), like US6 and US11.
- "Users can no longer see or select it": a Suspended category is not in the designer's IDP category drop-down (US20), and a form posted with its id is rejected.
- Suspending keeps the category row and the IDPs already in it - nothing is deleted. The manager can still find it with the search (US45) and view it (US42).
- A category that is already Suspended, or doesn't exist, can't be suspended.

## Lecturer feedback changes

- **Boundary checks everything.** The page trims the input, puts it in an entity object and checks every field itself (`validateInput()`).
- **The controller just calls the entity** and returns the result. It doesn't re-check the input and has no `canXxx()` access methods.
- **The entity checks for duplicates / still-Active rows** (e.g. a taken category name, a category suspended meanwhile).
- **An entity object is passed around, not a `{}` dict.**
- **One entity per B-C-E diagram.**
- **Precondition, no double check.** Being logged in is the precondition, so the B-C-E and sequence diagrams no longer re-check the user with the US13 / US39 login controller. `designerLoginRequired` and `managerLoginRequired` in `app.py` only send someone with no session to the login page.

## Repository files

New files for this story:

```text
boundary/suspendIDPCategoryPage.py
control/suspendIDPCategoryController.py
tests/test_us44_suspendIDPCategory.py
Sprint_3/US44 - Suspend IDP Category/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45, and `managerLoginRequired` (only sends someone with no session to `/manager/login`, like `designerLoginRequired`); no existing route changed
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `SuspendIDPCategoryPage` | `boundary/suspendIDPCategoryPage.py` (box in `templates/viewIDPCategory.html`) |
| Control `SuspendIDPCategoryController` | `control/suspendIDPCategoryController.py` |
| Reused control `ViewIDPCategoryController` | Existing US42 `control/viewIDPCategoryController.py` |
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
