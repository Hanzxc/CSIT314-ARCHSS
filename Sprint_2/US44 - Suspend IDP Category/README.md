# US44 — Suspend IDP category

> As a platform manager, I want to suspend an IDP category so that users can no longer see or select it.

## Behaviour

- "Suspend" is shown on the category details page (US42) only while the category is Active.
- Clicking it (`clickSuspend(categoryId)`) first gets the category by borrowing US42's `ViewIDPCategoryController.viewIDPCategory(categoryId)`.
  - Found → `displayConfirmation(idpCategory)` shows the "Are you sure?" box naming the category (wireframe 4b). The box is plain HTML on the details page (no JavaScript), like US6 and US11.
  - Not found → "This IDP category cannot be suspended".
- "Cancel" closes the box and nothing changes (`cancelSuspend()` → `closeConfirmation()`).
- "OK" (`confirmSuspend()`) calls `suspendIDPCategory(categoryId)`. The entity only changes an Active category, so one that is already Suspended (e.g. from an old tab) or no longer exists gives "This IDP category cannot be suspended". There is no `isActive()` check before the call.
- Suspended → the details page shows the Suspended badge and "IDP category suspended successfully"; the Suspend and Update buttons are gone (wireframe 4c).
- "Users can no longer see or select it": a Suspended category is not in the designer's IDP category drop-down (US20), and a form posted with its id is rejected (wireframe 4d). The category row and the IDPs in it are kept; the manager can still find it with the search (US45) and view it (US42).

## Who checks what

- **Boundary** (`SuspendIDPCategoryPage`): there is no typed input; it borrows US42's controller for the category in the box and shows the result.
- **Control** (`SuspendIDPCategoryController`): `suspendIDPCategory(categoryId)` just calls the entity and returns the result - no checks. The category in the box comes from US42's controller (one controller per use case).
- **Entity** (`IDPCategory`): only changes an Active row to Suspended (`... WHERE categoryId = ? AND status = 'Active'`); already suspended or no such id gives back False.
- Precondition: logged in as a Platform Manager (UC39). `managerLoginRequired` in `app.py` only sends someone with no session to `/manager/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SuspendIDPCategoryPage` — `clickSuspend(categoryId)`, `displayConfirmation(idpCategory)`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`; attributes `suspendIDPCategoryController`, `viewIDPCategoryController`, `categoryId` | `boundary/suspendIDPCategoryPage.py`, confirmation box in `templates/viewIDPCategory.html` |
| Control `SuspendIDPCategoryController` — `suspendIDPCategory(categoryId): bool` | `control/suspendIDPCategoryController.py` |
| Borrowed control `«control» (from US42) ViewIDPCategoryController` — `viewIDPCategory(categoryId): IDPCategory \| None` | `control/viewIDPCategoryController.py` |
| Entity `IDPCategory` — `getIDPCategory(categoryId)`, `suspendIDPCategory(categoryId): bool` | `entity/idpCategory.py` (table `idp_category`) |
| Route | GET / POST `/manager/categories/<categoryId>/suspend` → `suspendIDPCategory()` in `app.py` (POST `choice=cancel` → `cancelSuspend()`, otherwise `confirmSuspend()`) |

Messages: `MSG_SUSPENDED` "IDP category suspended successfully", `MSG_CANNOT_SUSPEND` "This IDP category cannot be suspended".

## Files

- `US44 Suspend IDP category.drawio` — every diagram, one page each
- `US44 Suspend IDP category.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Suspend button.png`
  - `4b Wireframe - Confirm suspend.png`
  - `4c Wireframe - Category suspended.png`
  - `4d Wireframe - Not selectable.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us44_suspendIDPCategory.py -v
```
