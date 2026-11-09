# US42 — View IDP category

> As a platform manager, I want to view IDP categories and the IDPs in them so that I can check whether IDPs are grouped correctly.

## Behaviour

- The manager opens a category from the IDP Categories list (US45) by clicking "View" (`selectIDPCategory(categoryId)`).
- The page loads the category with `viewIDPCategory(categoryId)`.
  - Not found (e.g. a wrong link) → `displayErrorMessage(MSG_NOT_FOUND)` shows "IDP category not found" and a Back button (wireframe 4d).
  - Found → the page loads the IDPs grouped in it with `getIDPsInCategory(categoryId)` (a `list[IDP]`: every Active IDP whose `categoryId` is this category, newest first) and shows them with `displayIDPCategory(idpCategory, idps)`.
- The details page shows the name, the status badge, the description and the IDP list (title, type and location, wireframe 4b). An empty list → "No IDPs are in this category yet" (`MSG_NO_IDPS`, wireframe 4c).
- Suspended categories can still be viewed. The Update (US43) and Suspend (US44) buttons start from this page and are only shown for an Active category.
- Nothing is changed (read only). IDPs are added to a category by designers (US20).

## Who checks what

- **Boundary** (`ViewIDPCategoryPage`): there is no typed input; it shows the details, `MSG_NO_IDPS` for an empty list, or `MSG_NOT_FOUND` when the controller returns None.
- **Control** (`ViewIDPCategoryController`): `viewIDPCategory(categoryId)` and `getIDPsInCategory(categoryId)` just call the entity and return the result - no checks.
- **Entity** (`IDPCategory`): `getIDPCategory(categoryId)` returns the category or None; `getIDPsInCategory(categoryId)` reads the Active rows of the `idp` table for the category.
- Precondition: logged in as a Platform Manager (UC39). `managerLoginRequired` in `app.py` only sends someone with no session to `/manager/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewIDPCategoryPage` — `selectIDPCategory(categoryId)`, `displayIDPCategory(idpCategory, idps)`, `displayErrorMessage(msg)`; attribute `viewIDPCategoryController` | `boundary/viewIDPCategoryPage.py`, `templates/viewIDPCategory.html` |
| Control `ViewIDPCategoryController` — `viewIDPCategory(categoryId): IDPCategory \| None`, `getIDPsInCategory(categoryId): list[IDP]` | `control/viewIDPCategoryController.py` |
| Entity `IDPCategory` — `getIDPCategory(categoryId): IDPCategory \| None`, `getIDPsInCategory(categoryId): list[IDP]` | `entity/idpCategory.py` (tables `idp_category` and `idp`) |
| Route | GET `/manager/categories/<categoryId>` → `viewIDPCategory()` in `app.py` |

Messages: `MSG_NOT_FOUND` "IDP category not found", `MSG_NO_IDPS` "No IDPs are in this category yet".

## Files

- `US42 View IDP category.drawio` — every diagram, one page each
- `US42 View IDP category.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Categories list.png`
  - `4b Wireframe - Category details.png`
  - `4c Wireframe - No IDPs yet.png`
  - `4d Wireframe - Category not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us42_viewIDPCategory.py -v
```
