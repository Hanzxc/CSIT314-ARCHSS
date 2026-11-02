# US32 — View IDP

> As a customer, I want to view an IDP so that I can see its details and learn about the designer's work.

## Try it

Run `python -m database.seedData`, `python -m database.seedCurrentIDPData`, then
`python app.py`. Log in at `/customer/login` as `cust001 / Cust@123`, open
**Search IDPs**, and select **View** on a result. Existing Active company profiles
appear in **About the designer**; otherwise a normal information message appears.

## Behaviour

- GET `/customer/idps/<idpId>?keyword=...` opens a customer detail page.
- Reuses US30 access: Active account/profile and the existing
  `Search, view and save IDPs` permission. Boundary and controller recheck access.
  No session redirects to customer login; denied access returns HTTP 403.
- `IDP.getIDP()` uses the same visibility query as US31: Active project and Active
  category, both Current and Past, across all designers. Missing/Suspended IDPs
  or hidden categories return HTTP 404 with `This IDP is not available.`
- Shows title, category, optional location, project type and full untruncated
  description. Reuses `idpDetailContent.html` and retains description line breaks.
- Retrieves company information using the selected project's saved designerId.
  **About the designer** shows an Active company name, description and services.
  Missing/Suspended company profiles show `Designer information is not currently
  available.` while the otherwise visible project remains available.
- Personal account details, credentials and business contact fields are not
  displayed by this story. No designer edit/delete or Save actions are added.
- US31 result cards link to the exact IDP and carry the trimmed keyword. **Back
  to search** restores it on the fixed US31 search route, even after HTTP 404.
  Direct links with no keyword return to the all-results search state.
- Reloading uses current saved values/visibility. Viewing writes no database
  records, saved-project state or customer statistics. No schema migration or
  new dependency is required.

## Implementation

- `entity/idp.py`: customer-visible `getIDP(idpId)` query.
- `control/viewIDPController.py`: access, project lookup and Active company lookup.
- `boundary/viewIDPPage.py`: access/keyword state, detail and unavailable responses.
- `templates/customerViewIDP.html`, `customerIDPNotFound.html`: shared customer layout.
- `templates/customerSearchIDPs.html`: View links on result cards.
- `app.py`: GET detail route; unsupported write methods return HTTP 405.
- `tests/test_us32_viewIDP.py`: 32 numbered cases, 58 automated checks.

## Documentation and images

`US32 View IDP.docx` follows the retained US13 Word sample and contains the story,
acceptance criteria, use case description, three diagrams, four wireframes,
manual scenarios and verified unit outcomes. Manual outcome cells remain blank.

`US32 View IDP.drawio` contains all seven editable pages. Separate PNG exports:

- `diagrams/2 Use Case Diagram.png`
- `diagrams/5 BCE Class Diagram.png`
- `diagrams/6 Sequence Diagram.png` — one combined sequence
- `diagrams/4a Wireframe - Select IDP.png`
- `diagrams/4b Wireframe - IDP details.png`
- `diagrams/4c Wireframe - Designer information unavailable.png`
- `diagrams/4d Wireframe - IDP unavailable.png`

## Validation

US32: **58 passed**. Full regression suite: **871 passed**. Tests use isolated
databases and cover full details, company fallbacks, catalogue visibility, stale
links, customer access/revocation, keyword return links, escaping and no writes.
