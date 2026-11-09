# US22 — Update current IDP

> As an interior designer, I want to update a current IDP so that customers can see its latest progress.

## Behaviour

- "Update current IDP" on the preview (`clickUpdate(idpId)`) loads the IDP with the controller's own loader `getCurrentIDP(designerId, idpId)` (`designerId = session["userId"]`).
- Found → `displayUpdateForm()` shows the form filled in with the saved details. The category drop-down comes from `getAvailableCategories()`, which borrows US45's `SearchIDPCategoryController.searchIDPCategories("")` and keeps the Active ones, sorted by name. None → "Current IDP not found" (HTTP 404, `displayNotFoundMessage()`).
- "Cancel" is a plain link back to the preview - nothing is saved.
- On "Save changes" (`submitUpdate(idpId, title, categoryId, description, location)`) the page trims the input and builds `idp = IDP(idpId, session userId, categoryId, title, description, location)`. A designerId, project type, status or created date in the form is ignored. There is no form token.
- `validateInput(idp)` has the same rules as US20: title required, 3-100 characters; description required, up to 2000; location optional, up to 200; the category must be one of the Active ones (`getAvailableCategories()` again). Bad input → "Please fix the highlighted fields", the typed values stay and nothing is saved.
- Otherwise `updateCurrentIDP(idp)` → the entity changes only title, categoryId, description and location of the owner's Active Current IDP, and only if its old and its new category are both Active.
- Updated → the preview with "Current IDP updated successfully". Not updated (the IDP or a category was suspended meanwhile) → "Current IDP not found" (HTTP 404).

## Who checks what

- **Boundary** (`UpdateCurrentIDPPage`): trims the input, takes the owner from the session, builds the `IDP` object and checks every field rule and the category itself (`validateInput(idp)`).
- **Control** (`UpdateCurrentIDPController`): `getCurrentIDP(designerId, idpId)` (US22's own loader for the form) and `updateCurrentIDP(idp)` just call the entity and return the result - no checks, no field rules, no category list.
- **Borrowed control** (`SearchIDPCategoryController`, from US45): `searchIDPCategories("")` lists the categories for the drop-down.
- **Entity** (`IDP`): `updateCurrentIDP(idp)` updates `WHERE idpId = ? AND designerId = ? AND projectType = 'Current' AND status = 'Active'` and only if the old and the new category are Active; 0 rows → False.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `UpdateCurrentIDPPage` — `clickUpdate(idpId)`, `displayUpdateForm(msg=None)`, `getAvailableCategories(): list`, `validateInput(idp): bool`, `submitUpdate(idpId, title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` | `boundary/updateCurrentIDPPage.py`, `templates/updateCurrentIDP.html`, `templates/currentIDPNotFound.html` |
| Control `UpdateCurrentIDPController` — `getCurrentIDP(designerId, idpId): IDP \| None`, `updateCurrentIDP(idp): bool` | `control/updateCurrentIDPController.py` |
| Borrowed control (from US45) `SearchIDPCategoryController` — `searchIDPCategories(keyword): list` | `control/searchIDPCategoryController.py` |
| Entity `IDP` — `getCurrentIDP(designerId, idpId): IDP \| None`, `updateCurrentIDP(idp): bool` | `entity/idp.py` (table `idp`) |
| Route | GET / POST `/designer/idps/current/<idpId>/update` (`@designerLoginRequired`) → `updateCurrentIDP(idpId)` in `app.py`; POST passes `title`, `categoryId` (int), `description`, `location` |

Messages: `MSG_UPDATED` "Current IDP updated successfully", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NOT_FOUND` "Current IDP not found"; field messages as US20 ("This field is required", "Title must be 3-100 characters", "Choose an available category").

## Files

- `US22 Update current IDP.drawio` — every diagram, one page each
- `US22 Update current IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Update action.png`
  - `4b Wireframe - Prefilled update form.png`
  - `4c Wireframe - Validation errors.png`
  - `4d Wireframe - Updated preview.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us22_updateCurrentIDP.py -v
```
