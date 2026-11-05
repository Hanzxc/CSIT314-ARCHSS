# US20 — Add current IDP

> As an interior designer, I want to add a current IDP so that I can show customers what I am working on.

## Behaviour

- Following the lecturer's feedback (the same way Sprint 1 and 2 were changed): the boundary trims and checks all the input, the controller just calls the entity and returns the result (no canXxx() access methods), the entity does the duplicate / still-Active checks, an entity object is passed around instead of a dict, and each B-C-E diagram has only one entity.
- An IDP is an interior design project. A current IDP is one the designer is still working on (US20 - US24); a past IDP is a completed one (US25 onwards). Both are rows in the idp table with projectType Current or Past.
- Being logged in as an Interior Designer (UC13) is the precondition, so the page and the diagrams don't check the designer again (no InteriorDesignerLoginController). designerLoginRequired in app.py only sends someone with no session to /designer/login.
- The form has a project title (required, 3-100 characters), an IDP category (required), a description (required, up to 2000) and a location (optional, up to 200).
- The category drop-down only lists Active IDP categories made by the Platform Manager (US41). Listing the categories is US45's job, so the page borrows SearchIDPCategoryController (empty keyword) and keeps the Active ones - the same way US8 borrows the US7 controller for its profile drop-down. A category that is Suspended (US44) can't be chosen, even by posting its id: the page rejects it, and the entity only saves the IDP if the category is still Active.
- The owner (designerId) is always the logged-in designer from the session, never a form field.
- A new IDP is saved as projectType Current and status Active, and appears under its category for the Platform Manager (US42). Viewing, updating, deleting and searching current IDPs are US21 - US24.
- Photos are not part of this story.

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
boundary/addCurrentIDPPage.py
control/addCurrentIDPController.py
entity/idp.py
templates/addCurrentIDP.html
tests/test_us20_addCurrentIDP.py
Sprint_3/US20 - Add Current IDP/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45, and `managerLoginRequired` (only sends someone with no session to `/manager/login`, like `designerLoginRequired`); no existing route changed
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `AddCurrentIDPPage` | `boundary/addCurrentIDPPage.py` |
| Control `AddCurrentIDPController` | `control/addCurrentIDPController.py` |
| Reused control `SearchIDPCategoryController` | Existing US45 `control/searchIDPCategoryController.py` (category drop-down) |
| Entity `IDP` | `entity/idp.py`, table `idp` in `database/schema.sql` |
| Route | GET/POST `/designer/idps/add` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US20 Add current IDP.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Add button.png
  4b Wireframe - Add form.png
  4c Wireframe - Form errors.png
  4d Wireframe - IDP added.png
  4e Wireframe - No categories yet.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 8 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us20_addCurrentIDP.py -v
python -m pytest -q
```
