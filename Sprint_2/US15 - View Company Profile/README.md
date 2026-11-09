# US15 — View company profile

> As an interior designer, I want to view my company profile so that I can check what customers see.

## Behaviour

- "View company profile" on the designer dashboard opens `/designer/company` (`clickView()`).
- The page asks its controller for the logged-in designer's profile: `viewCompanyProfile(designerId)` with `designerId = session["userId"]`. A designerId or companyId in the URL is ignored.
- `viewCompanyProfile()` makes one call to `CompanyProfile.getCompanyProfile(designerId)`, which only returns the designer's Active profile.
- Found → `displayCompanyProfile(profile)` shows the company name, description, services, email, phone and address. Empty optional fields show "Not provided". IDs, the created date and the designer's account details are not shown.
- None (never created, or deleted with US17) → "You have not created a company profile yet" (HTTP 404) with a "Create company profile" button.
- The page is read-only; POST to `/designer/company` is not allowed (HTTP 405). It has the Update (US16), Delete (US17) and Search (US18) buttons and "Back to dashboard".
- US13's dashboard borrows `ViewCompanyProfileController.viewCompanyProfile()` to decide whether to show "View company profile".

## Who checks what

- **Boundary** (`ViewCompanyProfilePage`): takes the designer from the session and chooses what to show (`[profile != None]` / `[profile == None]`). There is no typed input.
- **Control** (`ViewCompanyProfileController`): just calls the entity and returns the profile or None - one call, no checks.
- **Entity** (`CompanyProfile`): reads only this owner's Active row. Viewing never changes any data.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewCompanyProfilePage` — attribute `viewCompanyProfileController`; `clickView()`, `displayCompanyProfile(profile)`, `displayErrorMessage(msg)` | `boundary/viewCompanyProfilePage.py`, `templates/viewCompanyProfile.html`, `templates/companyProfileDetails.html`, `templates/companyProfileNotFound.html` |
| Control `ViewCompanyProfileController` — `viewCompanyProfile(designerId): CompanyProfile \| None` | `control/viewCompanyProfileController.py` |
| Entity `CompanyProfile` — `getCompanyProfile(designerId): CompanyProfile \| None` | `entity/companyProfile.py` (table `company_profile`) |
| Route | GET `/designer/company` (`@designerLoginRequired`) → `viewCompanyProfile()` in `app.py` |

Message: `MSG_NOT_FOUND` "You have not created a company profile yet".

## Files

- `US15 View company profile.drawio` — every diagram, one page each
- `US15 View company profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - View button.png`
  - `4b Wireframe - Company details.png`
  - `4c Wireframe - No company profile.png`
  - `4d Wireframe - Optional fields empty.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us15_viewCompanyProfile.py -v
```
