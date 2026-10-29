# US20 — Add current IDP

> As an interior designer, I want to add a current IDP so that I can show customers what I am working on.

## Behaviour

- An IDP is an interior design project. A current IDP is one the designer is still working on (US20 - US24); a past IDP is a completed one (US25 onwards). Both are rows in the idp table with projectType Current or Past.
- Only an active Interior Designer can add an IDP (the US13 InteriorDesignerLoginController access check, rechecked on every request). Someone not logged in goes to /designer/login; anyone else gets HTTP 403.
- The form has a project title (required, 3-100 characters), an IDP category (required), a description (required, up to 2000) and a location (optional, up to 200).
- The category drop-down only lists Active IDP categories made by the Platform Manager (US41). A category that is Suspended (US44) can't be chosen, even by posting its id.
- The owner (designerId) is always the logged-in designer from the session, never a form field.
- A new IDP is saved as projectType Current and status Active, and appears under its category for the Platform Manager (US42). Viewing, updating, deleting and searching current IDPs are US21 - US24.
- Photos are not part of this story.

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

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `AddCurrentIDPPage` | `boundary/addCurrentIDPPage.py` |
| Control `AddCurrentIDPController` | `control/addCurrentIDPController.py` |
| Reused control `InteriorDesignerLoginController` | Existing US13 `control/interiorDesignerLoginController.py` |
| Entity `IDP` | `entity/idp.py`, table `idp` in `database/schema.sql` |
| Entity `IDPCategory` | `entity/idpCategory.py` |
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
