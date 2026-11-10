# US25 — Add past IDP

> As an interior designer, I want to add a past IDP so that I can show customers my completed work.

## Behaviour

- "Add past IDP" on the dashboard, or "+ Add past IDP" on the past IDPs list (`openAddPastIDPForm()`), shows the form (`displayPastIDPForm()`).
- The category drop-down comes from `getAvailableCategories()`: the page borrows US45's `SearchIDPCategoryController.searchIDPCategories("")` and keeps the Active categories, sorted by name. No Active category → "No IDP categories are available yet. Please try again later" and no form.
- On "Add past IDP" (`submitPastIDP(title, categoryId, description, location)`) the page trims the input and builds `idp = IDP(session userId, categoryId, title, description, location, 'Past')`. The owner always comes from the session, never from the form.
- `validateInput(idp)`: title required, 3-100 characters; description required, up to 2000; location optional, up to 200; the category must be one of the Active ones (it calls `getAvailableCategories()` again). Bad input → "Please fill in all required fields", the typed values stay and nothing is saved.
- Otherwise `addPastIDP(idp)` → the entity inserts a Past, Active IDP only if its category is still Active. Added → the past IDPs list (US26) with "Past IDP added successfully". Not added → "Past IDP could not be added. Please try again".
- "Cancel" goes back to the past IDPs list. Photos are not part of this story. Viewing, updating, deleting and searching past IDPs are US26 - US29.

## Who checks what

- **Boundary** (`AddPastIDPPage`): trims the input, builds the `IDP` object and checks every field rule and that the category is one of the Active ones.
- **Control** (`AddPastIDPController`): `addPastIDP(idp)` just calls the entity and returns the result - no checks.
- **Borrowed control** (`SearchIDPCategoryController`, from US45): `searchIDPCategories("")` lists the categories for the drop-down.
- **Entity** (`IDP`): `createPastIDP(idp)` inserts the row as `projectType = 'Past'`, `status = 'Active'` only when the category is still Active (it could have been suspended meanwhile, US44).
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `AddPastIDPPage` — `openAddPastIDPForm()`, `getAvailableCategories(): list`, `displayPastIDPForm(msg=None)`, `validateInput(idp): bool`, `submitPastIDP(title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/addPastIDPPage.py`, `templates/addPastIDP.html` |
| Control `AddPastIDPController` — `addPastIDP(idp): bool` | `control/addPastIDPController.py` |
| Borrowed control (from US45) `SearchIDPCategoryController` — `searchIDPCategories(keyword): list` | `control/searchIDPCategoryController.py` |
| Entity `IDP` — `createPastIDP(idp): bool` | `entity/idp.py` (table `idp`) |
| Route | GET / POST `/designer/past-idps/add` (`@designerLoginRequired`) → `addPastIDP()` in `app.py` |

Messages: `MSG_ADDED` "Past IDP added successfully", `MSG_FIX_FIELDS` "Please fill in all required fields", `MSG_NO_CATEGORIES` "No IDP categories are available yet. Please try again later", `MSG_FAILED` "Past IDP could not be added. Please try again"; field messages `MSG_FIELD_REQUIRED` "This field is required", `MSG_TITLE_LENGTH` "Title must be 3-100 characters", `MSG_CHOOSE_CATEGORY` "Choose an available category" and "Maximum N characters".

## Files

- `US25 Add past IDP.drawio` — every diagram, one page each
- `US25 Add past IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Add form.png`
  - `4b Wireframe - Form errors.png`
  - `4c Wireframe - Past IDP added.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us25_addPastIDP.py -v
```
