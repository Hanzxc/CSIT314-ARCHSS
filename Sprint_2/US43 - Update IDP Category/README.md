# US43 — Update IDP category

> As a platform manager, I want to update an IDP category so that its name and details stay up to date.

## Behaviour

- "Update" on the category details page (`clickUpdate(categoryId)`) loads the category with US43's own `getIDPCategory(categoryId)`.
  - Not found (e.g. a wrong link) → `displayNotFoundMessage()` shows "IDP category not found".
  - Found → `displayUpdateForm()` shows the form filled in with the current name and description (wireframe 4b).
- "Cancel" is a plain link back to the details page - nothing is sent or changed.
- On "Save changes" (`submitUpdate(categoryName, description)`) the page trims the spaces, builds `idpCategory = IDPCategory(categoryId, categoryName, description)` and checks it with `validateInput(idpCategory)` (same rules as US41: name 3-50 characters, description up to 500).
- Bad input → "Please fix the highlighted fields", the wrong field is highlighted, what was typed stays in the form, and the controller is never called.
- Otherwise `updateIDPCategory(idpCategory)`. The entity only changes a category that is still Active and whose new name isn't used by a different category (keeping its own name is fine). If it refuses → "This IDP category could not be updated - the name is already used or the category is suspended" and nothing is saved (wireframe 4c).
- Saved → the details page shows "IDP category updated successfully" (wireframe 4d). Only the name and description change: the status is never changed here (suspending is US44) and the IDPs in the category show under the new name straight away.
- A suspended category can't be updated (team decision): the details page (US42) only shows "Update" for an Active category.

## Who checks what

- **Boundary** (`UpdateIDPCategoryPage`): checks all the input, trims spaces, builds the `IDPCategory` object and passes it on; shows "IDP category not found" when the loader returns None.
- **Control** (`UpdateIDPCategoryController`): `getIDPCategory(categoryId)` (US43's own loader) and `updateIDPCategory(idpCategory)` just call the entity and return the result - no checks.
- **Entity** (`IDPCategory`): checks the database - only an Active row is changed, and the new name must not be used by another category (`isCategoryNameTaken(categoryName, categoryId)`) - then saves the name and description.
- Precondition: logged in as a Platform Manager (UC39). `managerLoginRequired` in `app.py` only sends someone with no session to `/manager/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `UpdateIDPCategoryPage` — `clickUpdate(categoryId)`, `displayUpdateForm(msg=None)`, `validateInput(idpCategory): bool`, `submitUpdate(categoryName, description)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()`; attributes `updateIDPCategoryController`, `categoryId`, `idpCategory`, `fieldErrors` | `boundary/updateIDPCategoryPage.py` (field rules from `getFieldErrors()` in `boundary/createIDPCategoryPage.py`), `templates/updateIDPCategory.html` |
| Control `UpdateIDPCategoryController` — `getIDPCategory(categoryId): IDPCategory \| None`, `updateIDPCategory(idpCategory): bool` | `control/updateIDPCategoryController.py` |
| Entity `IDPCategory` — `IDPCategory(categoryId=None, categoryName="", description="")`, `getIDPCategory(categoryId)`, `isCategoryNameTaken(categoryName, categoryId=None): bool`, `updateIDPCategory(idpCategory): bool` | `entity/idpCategory.py` (table `idp_category`) |
| Route | GET / POST `/manager/categories/<categoryId>/update` → `updateIDPCategory()` in `app.py` |

Messages: `MSG_UPDATED` "IDP category updated successfully", `MSG_CANNOT_UPDATE` "This IDP category could not be updated - the name is already used or the category is suspended", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NOT_FOUND` "IDP category not found" (plus the US41 field messages).

## Files

- `US43 Update IDP category.drawio` — every diagram, one page each
- `US43 Update IDP category.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Update button.png`
  - `4b Wireframe - Update form.png`
  - `4c Wireframe - Name already used.png`
  - `4d Wireframe - Category updated.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us43_updateIDPCategory.py -v
```
