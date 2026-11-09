# US14 — Create company profile

> As an interior designer, I want to create a company profile so that customers can learn about my company and its services.

## Behaviour

- "Create company profile" on the designer dashboard (`clickCreateCompanyProfile()`) shows the empty form straight away (`displayCreateForm()`) - there is no "do you already have a profile?" check first. The dashboard only shows the button when the designer has no profile (UC13).
- The form has company name, company description, services offered, contact email, contact phone and company address. "Cancel" is a plain link back to the dashboard - nothing is sent or saved.
- On "Create company profile" (`submitCompanyProfile(companyName, description, services, email, phone, address)`) the page trims the spaces and builds `companyProfile = CompanyProfile(designerId, companyName, description, services, email, phone, address)` with `designerId = session["userId"]` (a designerId posted in the form is ignored).
- `validateInput(companyProfile)` uses `getFieldErrors(companyProfile)`, the shared field rules in `boundary/createCompanyProfilePage.py` (US16 uses them too): company name 3-100 characters, description up to 2000 and services up to 1000 are required; email (up to 254, must look like an email), phone (up to 30) and address (up to 300) are optional.
- Bad input → "Please fix the highlighted fields", the bad fields are highlighted, what was typed stays in the form, and the controller is never called.
- Otherwise `createCompanyProfile(companyProfile)` → the entity refuses a second row for the same designer (Active, or Suspended after a delete) → "You already have a company profile". A deleted profile is brought back with Restore on the dashboard (US17), not created again.
- Saved → the new profile is Active and the dashboard shows "Company profile created successfully" and "View company profile".

## Who checks what

- **Boundary** (`CreateCompanyProfilePage`): checks all the input with `getFieldErrors(companyProfile)`, trims spaces, takes the owner from the session, builds the `CompanyProfile` object and passes it on.
- **Control** (`CreateCompanyProfileController`): `createCompanyProfile(companyProfile)` just calls the entity and returns True or False - no checks.
- **Entity** (`CompanyProfile`): checks the database - the designer must not have a company row yet (Active or Suspended) - then inserts the fields as Active and commits. No `.strip()` here.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `CreateCompanyProfilePage` — `clickCreateCompanyProfile()`, `displayCreateForm(msg=None)`, `submitCompanyProfile(companyName, description, services, email, phone, address)`, `validateInput(companyProfile): bool`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`; module function `getFieldErrors(companyProfile)` | `boundary/createCompanyProfilePage.py`, `templates/createCompanyProfile.html` |
| Control `CreateCompanyProfileController` — `createCompanyProfile(companyProfile): bool` | `control/createCompanyProfileController.py` |
| Entity `CompanyProfile` — `createCompanyProfile(companyProfile): bool` | `entity/companyProfile.py` (table `company_profile`) |
| Route | GET / POST `/designer/company/create` (`@designerLoginRequired`) → `createCompanyProfile()` in `app.py` |

Messages: `MSG_CREATED` "Company profile created successfully", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_EXISTS` "You already have a company profile".

`database/seedCompanyData.py` adds 100 demo designers with one company profile each (running it again adds nothing).

## Files

- `US14 Create company profile.drawio` — every diagram, one page each
- `US14 Create company profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Create button.png`
  - `4b Wireframe - Create form.png`
  - `4c Wireframe - Form errors.png`
  - `4d Wireframe - Company created.png`
  - `4e Wireframe - Existing profile.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us14_createCompanyProfile.py -v
```
