# US45 — Search IDP categories

> As a platform manager, I want to search for IDP categories so that I can find the category I need to manage.

## Behaviour

- The search page is also the IDP Categories list (`/manager/categories`): an empty search shows every category, the same way the User Profiles list is the US7 search page (wireframe 4a).
- Clicking "Search" (`searchIDPCategories(keyword)`) trims the spaces around the keyword (None counts as empty) and keeps it in the search box, then calls the controller.
- The keyword is matched against the name and the description; capitals don't matter. Suspended categories are included, because the manager still needs to find them.
- Matches → `displayResults(categories)` lists them in the order they were created, with the name, description, status and a "View" link (US42, wireframe 4b).
- No matches → `displayNoResultsMessage()` shows "No IDP categories found"; the manager can type another keyword (wireframe 4c).

## Who checks what

- **Boundary** (`SearchIDPCategoryPage`): tidies the keyword (trims spaces) and shows the results or the no-results message.
- **Control** (`SearchIDPCategoryController`): `searchIDPCategories(keyword)` just calls the entity and returns the result - no checks.
- **Entity** (`IDPCategory`): `searchIDPCategories(keyword)` does a case-insensitive search of the name and description; an empty keyword matches every row.
- Precondition: logged in as a Platform Manager (UC39). `managerLoginRequired` in `app.py` only sends someone with no session to `/manager/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SearchIDPCategoryPage` — `searchIDPCategories(keyword)`, `displayResults(categories)`, `displayNoResultsMessage()`; attributes `searchIDPCategoryController`, `keyword` | `boundary/searchIDPCategoryPage.py`, `templates/idpCategories.html` |
| Control `SearchIDPCategoryController` — `searchIDPCategories(keyword): list` | `control/searchIDPCategoryController.py` |
| Entity `IDPCategory` — `searchIDPCategories(keyword): list` | `entity/idpCategory.py` (table `idp_category`) |
| Route | GET `/manager/categories?keyword=...` → `idpCategories()` in `app.py` |

Messages: `MSG_NO_RESULTS` "No IDP categories found".

## Files

- `US45 Search IDP categories.drawio` — every diagram, one page each
- `US45 Search IDP categories.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - All categories.png`
  - `4b Wireframe - Search results.png`
  - `4c Wireframe - No results.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us45_searchIDPCategories.py -v
```
