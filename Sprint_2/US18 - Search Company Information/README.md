# US18 — Search company information

> As an interior designer, I want to search my company’s information so that I can find the details I need.

## Behaviour

- "Search company information" on the company profile page opens `/designer/company/search`; typing a keyword and clicking "Search" (or "Clear") sends it again (`searchCompanyInformation(keyword)`).
- The page trims the keyword and calls `searchCompanyInformation(designerId, keyword)` straight away, with `designerId = session["userId"]` - there is no "has a profile?" call first.
- The entity loads the designer's Active profile. None → it returns None. Otherwise it returns that `CompanyProfile` with `matchedFields` = the names of the six business fields (companyName, description, services, email, phone, address, in that order) whose field name or saved value contains the keyword. Capitals don't matter, `%` is searched as normal text, and an empty keyword matches all six.
- Three results:
  - `companyProfile == None` → "You have not created a company profile yet" (HTTP 404) with a create link (`displayNotFoundMessage()`).
  - `matchedFields` is empty → "No matching company information found", the keyword stays in the box (`displayNoResultsMessage()`).
  - else → a Field / Information table with one row per name in `matchedFields` (`displayResults(companyProfile)`). The field labels belong to the page (`FIELD_LABELS`): Company name, Company description, Services offered, Contact email, Contact phone, Company address. Empty optional values show "Not provided".
- Searching is read-only. A designerId in the URL is ignored; IDs, the created date and account details are never searched or shown. A deleted (Suspended) profile can't be searched.

## Who checks what

- **Boundary** (`SearchCompanyInformationPage`): trims the keyword, takes the owner from the session, picks one of the three results and turns field names into labels.
- **Control** (`SearchCompanyInformationController`): `searchCompanyInformation(designerId, keyword)` just calls the entity and returns the result - no checks, no trimming.
- **Entity** (`CompanyProfile`): reads only the owner's Active row and works out `matchedFields`. No `.strip()` here.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SearchCompanyInformationPage` — attributes `searchCompanyInformationController`, `keyword`; `searchCompanyInformation(keyword)`, `displayResults(companyProfile)`, `displayNoResultsMessage()`, `displayNotFoundMessage()`; constant `FIELD_LABELS` | `boundary/searchCompanyInformationPage.py`, `templates/searchCompanyInformation.html`, `templates/companyProfileNotFound.html` |
| Control `SearchCompanyInformationController` — `searchCompanyInformation(designerId, keyword): CompanyProfile \| None` | `control/searchCompanyInformationController.py` |
| Entity `CompanyProfile` — attribute `matchedFields: list[String]`; `searchCompanyInformation(designerId, keyword): CompanyProfile \| None` | `entity/companyProfile.py` (table `company_profile`) |
| Route | GET `/designer/company/search?keyword=...` (`@designerLoginRequired`) → `searchCompanyInformation()` in `app.py` |

Messages: `MSG_NO_RESULTS` "No matching company information found", `MSG_NOT_FOUND` "You have not created a company profile yet".

## Files

- `US18 Search company information.drawio` — every diagram, one page each
- `US18 Search company information.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Search button.png`
  - `4b Wireframe - Search results.png`
  - `4c Wireframe - No matching information.png`
  - `4d Wireframe - All information.png`
  - `4e Wireframe - Profile not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us18_searchCompanyInformation.py -v
```
