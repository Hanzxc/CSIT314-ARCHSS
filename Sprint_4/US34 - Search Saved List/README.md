# US34 — Search saved list

> As a customer, I want to search my saved list so that I can find an IDP I saved earlier.

## Behaviour

- The search bar is on the Saved IDPs page (US35). Search sends GET `/customer/saved-list/search?keyword=...`.
- `submitSearch(keyword)`: the page trims the spaces from the keyword, then `validateKeyword(keyword)` - at most 100 characters; an empty keyword is allowed and shows the whole saved list.
- Valid → `searchSavedList(customerId, keyword)` (controller, `customerId = session["userId"]`) → `SavedIDP.searchSavedRecords(customerId, keyword)` → `results`.
- The entity only looks in this customer's saved list and returns the IDPs whose title, description, location or category name contains the keyword (capitals ignored), only Active IDPs in Active categories, most recently saved first.
- `[results is not empty]` → `displaySearchResults(results)`: the matching cards, keyword kept in the box (wireframe 4a). `[no match]` → `displayNoResultsMessage(MSG_NO_RESULTS)`: "No saved IDPs match your search" (wireframe 4b).
- Keyword longer than 100 characters → `displayErrorMessage(MSG_KEYWORD_TOO_LONG)`: "The keyword can be at most 100 characters" (HTTP 400); the controller is never called.
- Clear goes back to the whole saved list (US35). View on a card opens the IDP's details (US32). Searching never changes any data.

## Who checks what

- **Boundary** (`SavedListPage`, shared with US35): trims the keyword and checks its length, then shows the results or a message.
- **Control** (`SearchSavedListController`): `searchSavedList(customerId, keyword)` just calls `SavedIDP().searchSavedRecords(customerId, keyword)` and returns the list - no checks, no trimming.
- **Entity** (`SavedIDP`): limits the search to this customer's saved list and to IDPs customers can still see.
- Precondition: logged in as a Customer (UC30). `customerLoginRequired` in `app.py` only sends someone with no session to `/customer/login`. The role isn't checked again (no `CustomerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SavedListPage` — attributes `searchSavedListController`, `keyword`; `validateKeyword(keyword): str \| None`, `submitSearch(keyword)`, `displaySearchResults(results)`, `displayNoResultsMessage(msg)`, `displayErrorMessage(msg)` | `boundary/savedListPage.py`, `templates/savedList.html` |
| Control `SearchSavedListController` — `searchSavedList(customerId, keyword): list` | `control/searchSavedListController.py` |
| Entity `SavedIDP` — `searchSavedRecords(customerId, keyword): list` (IDP objects) | `entity/savedIDP.py` (tables `saved_idp`, `idp`, `idp_category`) |
| Route | GET `/customer/saved-list/search` (`@customerLoginRequired`) → `searchSavedList()` in `app.py` |

Messages: `MSG_NO_RESULTS` "No saved IDPs match your search", `MSG_KEYWORD_TOO_LONG` "The keyword can be at most 100 characters".

## Files

- `US34 Search saved list.drawio` — every diagram, one page each
- `US34 Search saved list.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Search results.png`
  - `4b Wireframe - No results.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us34_searchSavedList.py -v
```
