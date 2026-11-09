# US17 — Delete company profile (and UC17-R Restore company profile)

> As an interior designer, I want to delete my company profile so that it is no longer shown on the platform.

## Behaviour

Delete (UC17, sequence diagram page 6):

- "Delete company profile" on the company profile page (`clickDelete()`) loads the profile with the controller's own loader `getCompanyProfile(designerId)` (`designerId = session["userId"]`).
- Found → `displayConfirmation(profile)` shows "Are you sure you want to delete <company name>?". The box holds the profile's `companyId` and `revision` as hidden fields - nothing is kept in the session. None → "You have not created a company profile yet" (HTTP 404).
- The box posts `submitDelete(choice, companyId, revision)`:
  - `choice == "delete"` → `confirmDelete(companyId, revision)` → `deleteCompanyProfile(designerId, companyId, expectedRevision)` → `CompanyProfile.suspendCompanyProfile(designerId, companyId, expectedRevision)`. The entity sets `status = 'Suspended'` only for the owner's Active row with that companyId and revision; the row and its details are kept.
    - `deleted == True` → dashboard with "Company profile deleted successfully" and "Restore company profile".
    - `deleted == False` (no longer Active, or the revision changed - e.g. an old box sent again) → "Company profile could not be deleted. Please reopen the confirmation" (HTTP 400). Nothing changes.
  - `choice == "cancel"` → `cancelDelete()` → `closeConfirmation()` → back to the company profile, nothing changes.
  - any other choice → "Please open the delete confirmation and try again" (HTTP 400).
- While Suspended the company can't be viewed (US15), updated (US16) or searched (US18), and Create (US14) is refused. The designer account and the login session are kept.

Restore (UC17-R, sequence diagram page 6b):

- The designer dashboard (US13's `openDashboard()`) asks `RestoreCompanyProfileController.getSuspendedCompanyProfile(designerId)`. If there is a Suspended profile it shows "Restore company profile" (status only, no company details) with hidden `companyId` and `revision`; otherwise View or Create.
- The button posts `submitRestore(companyId, revision)` to `/designer/company/restore` → `restoreCompanyProfile(designerId, companyId, expectedRevision)` → `CompanyProfile.restoreCompanyProfile(designerId, companyId, expectedRevision)`. The entity sets `status = 'Active'` and `revision = revision + 1` only for the owner's Suspended row with that companyId and revision. The saved details are not changed.
  - `restored == True` → company view with "Company profile restored successfully".
  - `restored == False` (no longer Suspended, or an old dashboard page) → dashboard with "Company profile could not be restored. Please reopen the dashboard and try again".
- Because restore adds 1 to the revision, an old Delete form can't suspend the restored profile. That entity revision check is the only guard: there is no confirmation token, no session confirmation record and no owner/companyId comparison in the pages. The owner always comes from the session.

## Who checks what

- **Boundary** (`DeleteCompanyProfilePage`, `RestoreCompanyProfilePage`, and US13's `InteriorDesignerLoginPage` for the Restore button): pick the branch from `choice`, pass the session owner and the hidden `companyId` + `revision` on, and show the result. No typed input to check.
- **Control** (`DeleteCompanyProfileController`, `RestoreCompanyProfileController`): just call the entity and return the result - no checks. `getCompanyProfile()` is US17's own loader for the box; `getSuspendedCompanyProfile()` gives the dashboard the Restore button.
- **Entity** (`CompanyProfile`): changes a row only when owner, companyId, revision and status (Active for delete, Suspended for restore) all match.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use cases don't check the designer again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `DeleteCompanyProfilePage` — `clickDelete()`, `displayConfirmation(profile)`, `submitDelete(choice, companyId, revision)`, `confirmDelete(companyId, revision)`, `cancelDelete()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` | `boundary/deleteCompanyProfilePage.py`, `templates/deleteCompanyProfile.html`, `templates/companyProfileDeleteError.html`, `templates/companyProfileNotFound.html` |
| Boundary `RestoreCompanyProfilePage` — `submitRestore(companyId, revision)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/restoreCompanyProfilePage.py` |
| Boundary `«boundary» (from US13) InteriorDesignerLoginPage` — `openDashboard()` (shows the Restore button) | `boundary/interiorDesignerLoginPage.py`, `templates/interiorDesignerDashboard.html` |
| Control `DeleteCompanyProfileController` — `getCompanyProfile(designerId): CompanyProfile \| None`, `deleteCompanyProfile(designerId, companyId, expectedRevision): bool` | `control/deleteCompanyProfileController.py` |
| Control `RestoreCompanyProfileController` — `getSuspendedCompanyProfile(designerId): CompanyProfile \| None`, `restoreCompanyProfile(designerId, companyId, expectedRevision): bool` | `control/restoreCompanyProfileController.py` |
| Entity `CompanyProfile` — `getCompanyProfile(designerId)`, `suspendCompanyProfile(designerId, companyId, expectedRevision): bool`, `getSuspendedCompanyProfile(designerId)`, `restoreCompanyProfile(designerId, companyId, expectedRevision): bool` | `entity/companyProfile.py` (table `company_profile`, columns `status` and `revision`) |
| Route | GET / POST `/designer/company/delete` and POST `/designer/company/restore` (both `@designerLoginRequired`) in `app.py` |

Messages: `MSG_DELETED` "Company profile deleted successfully", `MSG_NOT_FOUND` "You have not created a company profile yet", `MSG_CONFIRM_AGAIN` "Please open the delete confirmation and try again", `MSG_FAILED` "Company profile could not be deleted. Please reopen the confirmation", `MSG_RESTORED` "Company profile restored successfully", `MSG_RESTORE_FAILED` "Company profile could not be restored. Please reopen the dashboard and try again".

## Files

- `US17 Delete company profile.drawio` — every diagram, one page each (page 6 Delete, page 6b Restore)
- `US17 Delete company profile.docx` — user story, UC17 and UC17-R use case descriptions, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Delete button.png`
  - `4b Wireframe - Confirm delete.png`
  - `4c Wireframe - Company deleted.png`
  - `4d Wireframe - Profile not found.png`
  - `4e Wireframe - Confirmation error.png`
  - `4f Wireframe - Company restored.png`
  - `4g Wireframe - Restore failed.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`
  - `6b Sequence Diagram - Restore.png`

## Tests

```
python -m pytest tests/test_us17_deleteCompanyProfile.py tests/test_us17_restoreCompanyProfile.py -v
```
