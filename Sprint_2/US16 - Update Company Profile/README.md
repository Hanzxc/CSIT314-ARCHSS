# US16 — Update company profile

> As an interior designer, I want to update my company profile so that customers see the latest information.

## Behaviour

- "Update company profile" on the company profile page (`clickUpdate()`) loads the current details with the controller's own loader `getCompanyProfile(designerId)` (`designerId = session["userId"]`).
- Found → `displayUpdateForm()` shows the form filled in with the saved details. None → "You have not created a company profile yet" (HTTP 404).
- "Cancel" is a plain link back to the company profile - nothing is saved.
- On "Save changes" (`submitUpdate(companyName, description, services, email, phone, address)`) the page trims the spaces and builds `companyProfile = CompanyProfile(designerId, companyName, description, services, email, phone, address)`. A designerId or companyId in the form or URL is ignored.
- `validateInput(companyProfile)` uses `getFieldErrors(companyProfile)` from `boundary/createCompanyProfilePage.py` - the same field rules as US14. Bad input → "Please fix the highlighted fields", the typed values stay and the saved profile is not changed.
- Otherwise `updateCompanyProfile(companyProfile)` → the entity changes only the six business fields of the owner's Active row. companyId, designerId and createdDate stay the same and no new row is added. Optional fields can be cleared.
- Updated → the company profile page with "Company profile updated successfully". Not updated (no Active row any more, e.g. deleted in the meantime) → "You have not created a company profile yet" (HTTP 404). A Suspended (deleted) profile is never updated.

## Who checks what

- **Boundary** (`UpdateCompanyProfilePage`): checks all the input with the shared `getFieldErrors(companyProfile)`, trims spaces, takes the owner from the session, builds the `CompanyProfile` object and passes it on.
- **Control** (`UpdateCompanyProfileController`): `getCompanyProfile(designerId)` (US16's own loader for the form) and `updateCompanyProfile(companyProfile)` just call the entity and return the result - no checks.
- **Entity** (`CompanyProfile`): only updates the owner's Active row (`WHERE designerId = ? AND status = 'Active'`) and returns False if no row changed.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `UpdateCompanyProfilePage` — `clickUpdate()`, `displayUpdateForm(msg=None)`, `validateInput(companyProfile): bool`, `submitUpdate(companyName, description, services, email, phone, address)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()`; uses `getFieldErrors(companyProfile)` from `createCompanyProfilePage.py` | `boundary/updateCompanyProfilePage.py`, `templates/updateCompanyProfile.html`, `templates/companyProfileNotFound.html` |
| Control `UpdateCompanyProfileController` — `getCompanyProfile(designerId): CompanyProfile \| None`, `updateCompanyProfile(companyProfile): bool` | `control/updateCompanyProfileController.py` |
| Entity `CompanyProfile` — `getCompanyProfile(designerId)`, `updateCompanyProfile(companyProfile): bool` | `entity/companyProfile.py` (table `company_profile`) |
| Route | GET / POST `/designer/company/update` (`@designerLoginRequired`) → `updateCompanyProfile()` in `app.py` |

Messages: `MSG_UPDATED` "Company profile updated successfully", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NOT_FOUND` "You have not created a company profile yet".

## Files

- `US16 Update company profile.drawio` — every diagram, one page each
- `US16 Update company profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Update button.png`
  - `4b Wireframe - Update form.png`
  - `4c Wireframe - Update errors.png`
  - `4d Wireframe - Company updated.png`
  - `4e Wireframe - Profile not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us16_updateCompanyProfile.py -v
```
