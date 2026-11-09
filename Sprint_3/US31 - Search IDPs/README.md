# US31 — Search IDPs

> As a customer, I want to search for IDPs so that I can find designs I like.

## Behaviour

- Search IDPs is opened from the customer dashboard or the sidebar: GET `/customer/idps/search?keyword=...`.
- `searchIDPs(keyword)` → the page trims the spaces from the keyword → `searchIDPs(keyword)` (controller) → `IDP.searchIDPs(keyword)` → `idps`.
- The catalogue is every Active IDP in an Active category, from every designer, both Current and Past. The keyword matches the title, description, location or category name, ignoring capitals (Unicode case folding); results are newest first and each IDP appears once. `%`, `_`, quotes and backslashes are normal characters.
- `[idps is not empty]` → `displayResults(idps)`: cards with title, category, location, project type and a short description; the keyword stays in the box (wireframes 4a, 4b).
- `[idps is empty]` → `displayNoResultsMessage()`: `MSG_NO_RESULTS` "No matching IDPs found" (wireframe 4c), or `MSG_NO_IDPS` "No IDPs are currently available" when the keyword is empty (wireframe 4d). Both are HTTP 200.
- An empty keyword (or Clear) lists every IDP the customer can see. Searching never changes data and is not counted as a view (viewing is US32).

## Who checks what

- **Boundary** (`SearchIDPPage`): trims the keyword (there are no other input rules) and shows the cards or the message.
- **Control** (`SearchIDPController`): `searchIDPs(keyword)` just calls `IDP().searchIDPs(keyword)` and returns the list - no checks, no trimming, no customer id.
- **Entity** (`IDP`): picks the Active IDPs in Active categories and matches the keyword. It doesn't trim the keyword.
- Precondition: logged in as a Customer (UC30). `customerLoginRequired` in `app.py` only sends someone with no session to `/customer/login`. The role isn't checked again (no `CustomerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SearchIDPPage` — attributes `searchIDPController`, `keyword`; `searchIDPs(keyword)`, `displayResults(idps)`, `displayNoResultsMessage()` | `boundary/searchIDPPage.py`, `templates/customerSearchIDPs.html` |
| Control `SearchIDPController` — `searchIDPs(keyword): list[IDP]` | `control/searchIDPController.py` |
| Entity `IDP` — `searchIDPs(keyword): list[IDP]` | `entity/idp.py` |
| Route | GET `/customer/idps/search` (`@customerLoginRequired`) → `searchIDPs()` in `app.py` |

Messages: `MSG_NO_RESULTS` "No matching IDPs found", `MSG_NO_IDPS` "No IDPs are currently available".

## Files

- `US31 Search IDPs.drawio` — every diagram, one page each
- `US31 Search IDPs.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Browse IDPs.png`
  - `4b Wireframe - Matching designs.png`
  - `4c Wireframe - No matching designs.png`
  - `4d Wireframe - Empty catalogue.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us31_searchIDPs.py -v
```
