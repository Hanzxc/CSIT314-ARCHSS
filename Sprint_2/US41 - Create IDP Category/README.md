# US41 — Create IDP category

> As a platform manager, I want to create an IDP category so that similar interior design IDPs can be grouped together.

## Behaviour

- An IDP category groups similar interior design projects (IDPs), e.g. Living Room or Kitchen. It has a name, an optional description and a status (Active or Suspended).
- "+ Create IDP category" on the IDP Categories list (`clickCreateIDPCategory()`) shows the empty form (`displayCreateForm()`). "Cancel" is a plain link back to the list - nothing is sent or saved.
- On "Create" (`submitIDPCategory(categoryName, description)`) the page trims the spaces, builds `idpCategory = IDPCategory(categoryName, description)` and checks it with `validateInput(idpCategory)` (`getFieldErrors()`): the name is required and 3-50 characters, the description is optional and up to 500 characters.
- Bad input → "Please fix the highlighted fields", the wrong field is highlighted, what was typed stays in the form, and the controller is never called.
- Otherwise `createIDPCategory(idpCategory)`. The entity checks that no other category has the name (`isCategoryNameTaken(idpCategory.categoryName)`, capitals ignored, so "kITCHEN " is the same as "Kitchen"). Name taken → "An IDP category with this name already exists" and nothing is saved (wireframe 4c).
- Saved → the new category is Active (designers can choose it straight away in US20) and the IDP Categories list shows "IDP category created successfully" (wireframe 4d).
- The IDP Categories list page is the US45 search page, the same way the User Profiles list is the US7 page. `database/seedIDPCategoryData.py` adds six demo categories (Living Room, Kitchen, Bedroom, Bathroom, Home Office, Commercial).

## Who checks what

- **Boundary** (`CreateIDPCategoryPage`): checks all the input (`validateInput(idpCategory)`), trims spaces and builds the `IDPCategory` object it passes on.
- **Control** (`CreateIDPCategoryController`): `createIDPCategory(idpCategory)` just calls the entity and returns the result - no checks.
- **Entity** (`IDPCategory`): checks the database - the name must not be used by another category - then saves the new category as Active.
- Precondition: logged in as a Platform Manager (UC39). `managerLoginRequired` in `app.py` only sends someone with no session to `/manager/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `CreateIDPCategoryPage` — `clickCreateIDPCategory()`, `displayCreateForm(msg=None)`, `validateInput(idpCategory): bool`, `submitIDPCategory(categoryName, description)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`; attributes `createIDPCategoryController`, `idpCategory`, `fieldErrors` | `boundary/createIDPCategoryPage.py` (field rules in `getFieldErrors(idpCategory)`), `templates/createIDPCategory.html` |
| Control `CreateIDPCategoryController` — `createIDPCategory(idpCategory): bool` | `control/createIDPCategoryController.py` |
| Entity `IDPCategory` — `IDPCategory(categoryId=None, categoryName="", description="")`, `isCategoryNameTaken(categoryName, categoryId=None): bool`, `createIDPCategory(idpCategory): bool` | `entity/idpCategory.py` (table `idp_category`) |
| Route | GET / POST `/manager/categories/create` → `createIDPCategory()` in `app.py` |

Messages: `MSG_CREATED` "IDP category created successfully", `MSG_NAME_TAKEN` "An IDP category with this name already exists", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NAME_LENGTH` "Category name must be 3-50 characters", `MSG_DESCRIPTION_LENGTH` "Description must be 500 characters or fewer".

## Files

- `US41 Create IDP category.drawio` — every diagram, one page each
- `US41 Create IDP category.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Create button.png`
  - `4b Wireframe - Create form.png`
  - `4c Wireframe - Form errors.png`
  - `4d Wireframe - Category created.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us41_createIDPCategory.py -v
```
