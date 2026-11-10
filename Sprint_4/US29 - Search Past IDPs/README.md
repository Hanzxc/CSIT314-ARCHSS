# US29 — Search past IDPs

> As an interior designer, I want to search my past IDPs so that I can find the IDP I need to manage.

## Behaviour

- The search bar sits on the past IDPs list (US26). "Search" (`submitSearch(keyword)`) trims the keyword and keeps it in the box.
- `validateKeyword(keyword)`: at most 100 characters, empty is allowed. Too long → `displayErrorMessage(MSG_KEYWORD_TOO_LONG)` "The keyword can be at most 100 characters" (HTTP 400) and the controller is not called.
- Otherwise `searchPastIDPs(designerId, keyword)` with `designerId = session["userId"]` → the entity matches the keyword (any case) against the title, description, location and category name of the designer's own Active past IDPs, newest first. An empty keyword returns all of them.
- Matches → `displaySearchResults(results)` with "View" links (US26 details). None → `displayNoResultsMessage(MSG_NO_RESULTS)` "No past IDPs match your search". "Clear" goes back to the full list.
- Current IDPs, deleted past IDPs and other designers' IDPs are never shown. Searching changes nothing.

## Who checks what

- **Boundary** (`PastIDPSearchPage`): trims the keyword and checks its length (`validateKeyword`).
- **Control** (`SearchPastIDPController`): `searchPastIDPs(designerId, keyword)` just calls the entity and returns the result - no checks, no trimming.
- **Entity** (`IDP`): `searchByKeywordAndDesigner(keyword, designerId)` only searches the owner's rows with `projectType = 'Past' AND status = 'Active'`.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `PastIDPSearchPage` — `submitSearch(keyword)`, `validateKeyword(keyword): str \| None`, `displaySearchResults(results)`, `displayNoResultsMessage(msg)`, `displayErrorMessage(msg)` | `boundary/pastIDPSearchPage.py`, `templates/pastIDPs.html` |
| Control `SearchPastIDPController` — `searchPastIDPs(designerId, keyword): list` | `control/searchPastIDPController.py` |
| Entity `IDP` — `searchByKeywordAndDesigner(keyword, designerId): list` | `entity/idp.py` (table `idp`) |
| Route | GET `/designer/past-idps/search?keyword=...` (`@designerLoginRequired`) → `searchPastIDPs()` in `app.py` |

Messages: `MSG_NO_RESULTS` "No past IDPs match your search", `MSG_KEYWORD_TOO_LONG` "The keyword can be at most 100 characters".

## Files

- `US29 Search past IDPs.drawio` — every diagram, one page each
- `US29 Search past IDPs.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Search results.png`
  - `4b Wireframe - No results.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us29_searchPastIDPs.py -v
```
