# US24 — Search current IDPs

> As an interior designer, I want to search my current IDPs so that I can find the IDP I need to manage.

## Behaviour

- "Search current IDPs" on Current IDPs opens the search page; the form sends `keyword` with GET (`searchCurrentIDPs(keyword)`).
- The page trims the keyword, keeps it for the search box and calls `searchCurrentIDPs(designerId, keyword)` straight away (`designerId = session["userId"]`). The controller and the entity don't trim it again.
- The entity matches the keyword as plain text (any case; %, _, quotes and backslashes are ordinary characters) against the title, description, location and category name of the owner's Active Current IDPs in Active categories, newest first, each IDP once. An empty keyword (or "Clear") returns all of them.
- Results → `displayResults(idps)`: the cards, "N current IDPs found" and the keyword. None → `displayNoResultsMessage()`: "No matching current IDPs found", or "You have no current IDPs to display" for an empty keyword.
- "View" on a result opens the US21 preview. Searching changes nothing; a designerId in the URL is ignored.

## Who checks what

- **Boundary** (`SearchCurrentIDPPage`): trims the keyword (the only input; it can be empty) and takes the owner from the session.
- **Control** (`SearchCurrentIDPController`): `searchCurrentIDPs(designerId, keyword)` just calls the entity and returns the result - no checks, no trimming.
- **Entity** (`IDP`): `searchCurrentIDPs(designerId, keyword)` only searches the owner's Active Current IDPs in Active categories; no `.strip()` here.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SearchCurrentIDPPage` — `searchCurrentIDPs(keyword)`, `displayResults(idps)`, `displayNoResultsMessage()` | `boundary/searchCurrentIDPPage.py`, `templates/searchCurrentIDPs.html`, `templates/currentIDPCards.html` |
| Control `SearchCurrentIDPController` — `searchCurrentIDPs(designerId, keyword): list` | `control/searchCurrentIDPController.py` |
| Entity `IDP` — `searchCurrentIDPs(designerId, keyword): list` | `entity/idp.py` (table `idp`, joined with `idp_category`) |
| Route | GET `/designer/idps/current/search?keyword=...` (`@designerLoginRequired`) → `searchCurrentIDPs()` in `app.py` |

Messages: `MSG_NO_RESULTS` "No matching current IDPs found", `MSG_NO_IDPS` "You have no current IDPs to display".

## Files

- `US24 Search current IDPs.drawio` — every diagram, one page each
- `US24 Search current IDPs.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Search form.png`
  - `4b Wireframe - Matching results.png`
  - `4c Wireframe - No matching results.png`
  - `4d Wireframe - No current IDPs.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us24_searchCurrentIDPs.py -v
```
