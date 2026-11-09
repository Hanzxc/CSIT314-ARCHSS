# US20 — Add current IDP

> As an interior designer, I want to add a current IDP so that I can show customers what I am working on.

## Behaviour

- "Add current IDP" on the Current IDPs card of the dashboard (`clickAddCurrentIDP()`) shows the form (`displayAddForm()`).
- The category drop-down comes from `getAvailableCategories()`: the page borrows US45's `SearchIDPCategoryController.searchIDPCategories("")` and keeps the Active categories, sorted by name. No Active category → "No IDP categories are available yet. Please try again later" and no form.
- On "Add current IDP" (`submitCurrentIDP(title, categoryId, description, location)`) the page trims the input and builds `idp = IDP(session userId, categoryId, title, description, location)`. The owner always comes from the session, never from the form.
- `validateInput(idp)`: title required, 3-100 characters; description required, up to 2000; location optional, up to 200; the category must be one of the Active ones (it calls `getAvailableCategories()` again). Bad input → "Please fix the highlighted fields", the typed values stay and nothing is saved.
- Otherwise `addCurrentIDP(idp)` → the entity inserts a Current, Active IDP only if its category is still Active and the owner exists. Added → the dashboard with "Current IDP added successfully". Not added → "Current IDP could not be added. Please try again".
- Photos are not part of this story. Viewing, updating, deleting and searching current IDPs are US21 - US24.

## Who checks what

- **Boundary** (`AddCurrentIDPPage`): trims the input, builds the `IDP` object and checks every field rule and that the category is one of the Active ones.
- **Control** (`AddCurrentIDPController`): `addCurrentIDP(idp)` just calls the entity and returns the result - no checks.
- **Borrowed control** (`SearchIDPCategoryController`, from US45): `searchIDPCategories("")` lists the categories for the drop-down.
- **Entity** (`IDP`): `addCurrentIDP(idp)` only inserts when the category is still Active (it could have been suspended meanwhile, US44) and the owner exists.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `AddCurrentIDPPage` — `clickAddCurrentIDP()`, `getAvailableCategories(): list`, `displayAddForm(msg=None)`, `validateInput(idp): bool`, `submitCurrentIDP(title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/addCurrentIDPPage.py`, `templates/addCurrentIDP.html` |
| Control `AddCurrentIDPController` — `addCurrentIDP(idp): bool` | `control/addCurrentIDPController.py` |
| Borrowed control (from US45) `SearchIDPCategoryController` — `searchIDPCategories(keyword): list` | `control/searchIDPCategoryController.py` |
| Entity `IDP` — `addCurrentIDP(idp): bool` | `entity/idp.py` (table `idp`) |
| Route | GET / POST `/designer/idps/add` (`@designerLoginRequired`) → `addCurrentIDP()` in `app.py` |

Messages: `MSG_ADDED` "Current IDP added successfully", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NO_CATEGORIES` "No IDP categories are available yet. Please try again later", `MSG_FAILED` "Current IDP could not be added. Please try again".

## Files

- `US20 Add current IDP.drawio` — every diagram, one page each
- `US20 Add current IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Add button.png`
  - `4b Wireframe - Add form.png`
  - `4c Wireframe - Form errors.png`
  - `4d Wireframe - IDP added.png`
  - `4e Wireframe - No categories yet.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us20_addCurrentIDP.py -v
```
