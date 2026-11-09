# US32 — View IDP

> As a customer, I want to view an IDP so that I can see its details and learn about the designer’s work.

## Behaviour

- The customer clicks View on a US31 result (or opens the link): GET `/customer/idps/<idpId>?keyword=...`. The route passes `saved = (request.args.get("saved") == "1")`.
- `selectIDP(idpId, keyword, saved)` → the page trims the keyword (kept for Back to search) → `countView = not saved` → `viewIDP(idpId, countView)` (controller) → `IDP.viewIDP(idpId, countView)` → `idp`.
- `IDP.viewIDP()` returns the IDP if it is Active and its category is Active (Current or Past, any designer), otherwise `None`. When the IDP is found and `countView` is True it also inserts one `idp_view` row - that is the view counted by the statistics (US37, US46 - US48).
- `saved` is True only when US33's Save sends the customer back here (`/customer/idps/<idpId>?saved=1`), so that reload is not counted as a view.
- `[idp != None]` → the page borrows US15: `ViewCompanyProfileController().viewCompanyProfile(idp.designerId)` → `displayIDP(idp, companyProfile)` (wireframe 4b). If `companyProfile` is None the page shows "Designer information is not currently available." (wireframe 4c).
- `[idp == None]` → `displayNotFoundMessage()`: HTTP 404 "This IDP is not available." with Back to search (wireframe 4d).
- The Save IDP button (US33) is always shown - US33 handles an IDP that is already saved. Back to search keeps the trimmed keyword and always goes to the US31 page.

## Who checks what

- **Boundary** (`ViewIDPPage`): trims the keyword, works out `countView`, gets the company profile through US15's controller and shows the page or the 404.
- **Control** (`ViewIDPController`): `viewIDP(idpId, countView)` just calls `IDP().viewIDP(idpId, countView)` and returns the IDP or None - no checks, no dict, no customer id.
- **Borrowed control** (`ViewCompanyProfileController`, US15): `viewCompanyProfile(designerId)` returns the designer's Active company profile or None.
- **Entity** (`IDP`): checks the IDP and its category are Active, and records the view.
- Precondition: logged in as a Customer (UC30). `customerLoginRequired` in `app.py` only sends someone with no session to `/customer/login`. The role isn't checked again (no `CustomerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewIDPPage` — attributes `viewIDPController`, `keyword`; `selectIDP(idpId, keyword, saved=False)`, `displayIDP(idp, companyProfile)`, `displayNotFoundMessage()` | `boundary/viewIDPPage.py`, `templates/customerViewIDP.html`, `templates/customerIDPNotFound.html` |
| Control `ViewIDPController` — `viewIDP(idpId, countView): IDP \| None` | `control/viewIDPController.py` |
| Borrowed control `ViewCompanyProfileController` (from US15) — `viewCompanyProfile(designerId): CompanyProfile \| None` | `control/viewCompanyProfileController.py` |
| Entity `IDP` — `viewIDP(idpId, countView): IDP \| None` (inserts the `idp_view` row) | `entity/idp.py` |
| Route | GET `/customer/idps/<idpId>` (`@customerLoginRequired`) → `viewIDP(idpId)` in `app.py` |

## Files

- `US32 View IDP.drawio` — every diagram, one page each
- `US32 View IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Select IDP.png`
  - `4b Wireframe - IDP details.png`
  - `4c Wireframe - Designer information unavailable.png`
  - `4d Wireframe - IDP unavailable.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us32_viewIDP.py -v
```
