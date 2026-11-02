# US31 — Search IDPs

> As a customer, I want to search for IDPs so that I can find designs I like.

## Try it

Run `python -m database.seedData`, `python -m database.seedCurrentIDPData`, then
`python app.py`. Log in at `/customer/login` as `cust001 / Cust@123`.
Select **Search IDPs** on the dashboard or sidebar, or open
`http://127.0.0.1:5000/customer/idps/search`. Try `kitchen`, `Tampines` or an empty keyword.

## Search behaviour

- Searches all designers' **Active** IDPs in **Active** categories, including
  **Current and Past** projects. Catalogue visibility follows the existing
  project/category status fields; no company-profile or owner-only filter is added.
- Reuses US30 customer access: Active account/profile with the existing
  `Search, view and save IDPs` permission. The controller rechecks access before
  querying. No session redirects to customer login; denied access returns 403.
- Searches title, description, location and joined category name as one literal,
  trimmed, Unicode case-insensitive substring. Accents are retained; multiple
  words are one phrase. Percent, underscore, quotes and backslashes are ordinary
  search characters. SQL uses bound parameters.
- Empty/missing/whitespace keywords browse all visible projects. Clear removes
  the keyword. Results are newest ID first, without duplicate projects.
- Cards show title, category, optional location, project type and a short
  description using the template's 200-character truncation filter.
- Nonempty search with no matches shows `No matching IDPs found`; an empty
  catalogue with a blank keyword shows `No IDPs are currently available`.
  Both are normal HTTP 200 pages. The trimmed keyword is retained.
- Results reflect saved updates, deletions and category visibility changes on
  the next request. Search writes no records or customer view statistics.
- Detailed viewing and saving remain separate stories; the result cards add no
  dead View/Save links or designer-only management actions.

## Implementation

- `entity/idp.py`: `searchIDPs(keyword)` and the customer catalogue visibility query.
- `control/searchIDPController.py`: customer identity/access and search delegation.
- `boundary/searchIDPPage.py`: form input, access handling and result/empty states.
- `templates/customerSearchIDPs.html`: shared customer layout, search bar and cards.
- `templates/customerBase.html`, `customerDashboard.html`: navigation entry points.
- `app.py`: GET `/customer/idps/search?keyword=...`.
- `tests/test_us31_searchIDPs.py`: 32 numbered cases, 57 automated checks.

No schema migration or new dependency is required.

## Documentation and images

`US31 Search IDPs.docx` follows the retained US13 Word sample. It contains the
story, acceptance criteria, use case description, three diagrams, four wireframes,
manual system tests and verified unit outcomes. Manual result cells stay blank.

`US31 Search IDPs.drawio` contains all seven editable diagram/wireframe pages.
Separate PNGs in `diagrams/`:

- `2 Use Case Diagram.png`
- `5 BCE Class Diagram.png`
- `6 Sequence Diagram.png` — one combined sequence
- `4a Wireframe - Browse IDPs.png`
- `4b Wireframe - Matching designs.png`
- `4c Wireframe - No matching designs.png`
- `4d Wireframe - Empty catalogue.png`

## Validation

US31: **57 passed**. Full regression suite: **813 passed**. Tests use isolated
databases and cover all search fields, project types/owners, visibility, Unicode,
literal input, access revocation, escaping, navigation, fresh results and no writes.
