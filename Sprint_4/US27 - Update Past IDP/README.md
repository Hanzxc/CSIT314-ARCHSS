# US27 — Update past IDP

> As an interior designer, I want to update a past IDP so that its details are correct.

## Behaviour

- "Update" on the past IDP's details (`openEditForm(idpId)`) loads the IDP with the controller's own loader `getPastIDP(designerId, idpId)` (`designerId = session["userId"]`).
- Found → `displayEditForm()` shows the form filled in with the saved details. The category drop-down comes from `getAvailableCategories()`, which borrows US45's `SearchIDPCategoryController.searchIDPCategories("")` and keeps the Active ones, sorted by name. None → "Past IDP not found" (HTTP 404, `displayNotFoundMessage(MSG_NOT_FOUND)`).
- "Cancel" is a plain link back to the details - nothing is saved.
- On "Save changes" (`submitUpdatedDetails(idpId, title, categoryId, description, location)`) the page trims the input and builds `idp = IDP(idpId, session userId, categoryId, title, description, location, 'Past')`.
- `validateInput(idp)` has the same rules as US25 (title 3-100, description required up to 2000, location up to 200, category one of the Active ones via `getAvailableCategories()`). Bad input → "Please fill in all required fields", the typed values stay and nothing is saved.
- Otherwise `updatePastIDP(idp)` → the entity changes only title, categoryId, description and location of the owner's Active past IDP, and only into an Active category.
- Updated → the details with "Past IDP updated successfully". Not updated → the page asks `getPastIDP(designerId, idpId)` again: None (deleted meanwhile or not theirs) → "Past IDP not found" (HTTP 404); still there (e.g. the new category was suspended meanwhile) → `displayErrorMessage(MSG_FAILED)` "Past IDP could not be updated. Please try again".

## Who checks what

- **Boundary** (`EditPastIDPPage`): trims the input, takes the owner from the session, builds the `IDP` object and checks every field rule and the category itself (`validateInput(idp)`).
- **Control** (`UpdatePastIDPController`): `getPastIDP(designerId, idpId)` (US27's own loader, also used after a failed update) and `updatePastIDP(idp)` just call the entity and return the result - no checks.
- **Borrowed control** (`SearchIDPCategoryController`, from US45): `searchIDPCategories("")` lists the categories for the drop-down.
- **Entity** (`IDP`): `updatePastIDPDetails(idp)` updates `WHERE idpId = ? AND designerId = ? AND projectType = 'Past' AND status = 'Active'` and only if the new category is Active; 0 rows → False.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `EditPastIDPPage` — `openEditForm(idpId)`, `getAvailableCategories(): list`, `displayEditForm(msg=None)`, `validateInput(idp): bool`, `submitUpdatedDetails(idpId, title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage(msg)` | `boundary/editPastIDPPage.py`, `templates/editPastIDP.html`, `templates/pastIDPNotFound.html` |
| Control `UpdatePastIDPController` — `getPastIDP(designerId, idpId): IDP`, `updatePastIDP(idp): bool` | `control/updatePastIDPController.py` |
| Borrowed control (from US45) `SearchIDPCategoryController` — `searchIDPCategories(keyword): list` | `control/searchIDPCategoryController.py` |
| Entity `IDP` — `getPastIDPDetails(designerId, idpId): IDP`, `updatePastIDPDetails(idp): bool` | `entity/idp.py` (table `idp`) |
| Route | GET / POST `/designer/past-idps/<idpId>/edit` (`@designerLoginRequired`) → `editPastIDP(idpId)` in `app.py` |

Messages: `MSG_UPDATED` "Past IDP updated successfully", `MSG_FIX_FIELDS` "Please fill in all required fields", `MSG_NOT_FOUND` "Past IDP not found", `MSG_FAILED` "Past IDP could not be updated. Please try again"; field messages `MSG_FIELD_REQUIRED` "This field is required", `MSG_TITLE_LENGTH` "Title must be 3-100 characters", `MSG_CHOOSE_CATEGORY` "Choose an available category" and "Maximum N characters" (the same as US25).

## Files

- `US27 Update past IDP.drawio` — every diagram, one page each
- `US27 Update past IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Update form.png`
  - `4b Wireframe - Update errors.png`
  - `4c Wireframe - Past IDP updated.png`
  - `4d Wireframe - Past IDP not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us27_updatePastIDP.py -v
```
