# US17 — Delete company profile

> As an interior designer, I want to delete my company profile so that it is no longer shown on the platform.

Apply this repository update **after US13–16**. It follows the same simple Python test/helper format, camelCase filenames and methods, three UML diagram types, one editable draw.io file, numbered PNG filenames and labelled wireframes with Notes panels. Sample names and branding are unchanged. Only repository files are packaged, not a complete project.

## Behaviour and assumptions

The US15 company view now has a **Delete company profile** link alongside Update and Back. Opening it loads a confirmation dialog naming the existing company. Opening the dialog does not delete anything.

- **Cancel** clears the pending confirmation and returns to the company view, keeping its data.
- **Delete company profile** submits an explicit confirmation. Success deletes the company record, flashes `Company profile deleted successfully` and returns to the designer dashboard.
- The dashboard then offers US14 creation again, because no company profile remains. The old company view/update page returns the missing-profile response (404).
- The designer's user account and login session are retained; other designers' profiles are unaffected.

This implementation uses a **physical delete** of the company's database row, not an archived/hidden status. There is no restore operation in these stories. This is a design assumption to confirm with your group/tutor. Only `company_profile` is targeted; no user-account deletion, logout or IDP deletion is implemented. Later customer pages reading the same entity will no longer find the deleted record; customer routing is outside these designer stories.

Only the session user owns the deletion. Both `designerId` and the confirmed `companyId` must match the database row. Posted/query owner fields are ignored. A session-bound confirmation includes that specific company ID and a random token; the boundary checks it before deletion and consumes it once. Missing/wrong/reused confirmation, altered IDs and unknown choices return HTTP 400 without deleting a profile. An old confirmation cannot remove a replacement profile created later under the same account. Opening a new dialog replaces that session's pending confirmation.

US13 account/profile status and designer-permission checks are reused on GET and POST, and the control rechecks access before deleting. No session redirects to designer login; unsuitable access returns 403. No profile returns the existing 404 page with a creation link. A failed deletion with a remaining/replacement record returns a failure page to reopen confirmation; it does not delete that replacement automatically.

## Repository files

Add these new files to their matching existing folders:

```text
boundary/deleteCompanyProfilePage.py
control/deleteCompanyProfileController.py
templates/deleteCompanyProfile.html
templates/companyProfileDeleteError.html
tests/test_us17_deleteCompanyProfile.py
Sprint_2/US17 - Delete Company Profile/...
```

Combine these modified files with the group's latest versions:

```text
app.py
entity/companyProfile.py
templates/viewCompanyProfile.html
```

All implementation files are required alongside the test and Sprint_2 folder. Paths in the ZIP are relative to the repository root. Keep other group files; add new files alongside them and preserve newer shared changes when combining modified files. The entity gains `deleteCompanyProfile(designerId, companyId)` while retaining its create/get/update methods. There is no schema change or migration. US13–16 test files are unchanged. No Git commit, push or merge has been performed.

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `DeleteCompanyProfilePage` | `boundary/deleteCompanyProfilePage.py` |
| Control `DeleteCompanyProfileController` | `control/deleteCompanyProfileController.py` |
| Entity `CompanyProfile` | Extended `entity/companyProfile.py` |
| Shared access control | Existing `InteriorDesignerLoginController.getAuthenticatedDesigner()` |
| Confirmation dialog | `templates/deleteCompanyProfile.html` |
| Reopen-confirmation error page | `templates/companyProfileDeleteError.html` |
| Delete entry link | `templates/viewCompanyProfile.html` |
| Route | GET/POST `/designer/company/delete` in `app.py` |

The single sequence diagram covers opening the dialog, choosing Cancel or Delete, checking confirmation, deleting the exact owned record and success/failure outcomes. Early access-denial behaviour is stated at the top. The BCE diagram uses the actual class and method names and shows only relevant methods of reused classes. The confirmation/session logic lives in the Boundary; authorisation and persistence are delegated to the Control and Entity.

```text
US17 Delete company profile.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Delete button.png
  4b Wireframe - Confirm delete.png
  4c Wireframe - Company deleted.png
  4d Wireframe - Profile not found.png
  4e Wireframe - Confirmation error.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file has eight editable pages. PNGs are locally rendered vector illustrations checked visually, not browser screenshots. Written use case descriptions, Word reports and written test case tables remain deferred.

## Run pass/fail tests

Open a terminal at the group **repository root**, after combining all files:

```powershell
python -m pytest tests/test_us17_deleteCompanyProfile.py -v --basetemp=.test-tmp-us17
python -m pytest -q --basetemp=.test-tmp-all
```

If `python` is not recognised on the computer used to prepare these packages:

```powershell
$us17Python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
& $us17Python -m pytest tests/test_us17_deleteCompanyProfile.py -v --basetemp=.test-tmp-us17
& $us17Python -m pytest -q --basetemp=.test-tmp-all
```

**Verified: 28 US17 tests passed; 302 tests passed overall**, including all 274 prior tests. Tests cover successful deletion, Cancel, unchanged accounts/login, owner isolation, access restrictions, no deletion on GET, missing records, forged owner/company fields, confirmation validation/reuse, stale confirmation versus replacement records, escaped company names and the create–view–update–delete flow.

Tests use the existing `conftest.py` isolated temporary database and local helper functions. They do not delete records from your demo database. No website server or manual credential entry is needed. Use `--basetemp` folders only for disposable test scratch data; pytest recreates them. The first run failed because the new controller was absent; final runs passed. This records this development session, not prior group activity.

## Try it in the browser

From the repository root, start the same application:

```powershell
python app.py
```

Use the explicit executable above if needed. Leave the terminal running and visit `http://127.0.0.1:5000/login`.

1. Log in with your existing fictional designer account, such as `designer13` / `Design@123` if set up in US13/14.
2. Use US14 to create a sample company if none exists, then open **View company profile**.
3. Select **Delete company profile**. Verify that the confirmation names your sample company.
4. Try **Cancel** first: the company remains.
5. Open the dialog again and choose **Delete company profile** to remove that sample company's actual row from the demo database.
6. Check the success message and Create button on the dashboard. Visiting the old company view shows that no profile exists, while the account remains logged in.

A manual confirmed deletion persists across application restarts and has no undo here. Use sample data for the demonstration. You can create a new profile through US14 afterward. Automated tests are repeatable because they use fresh temporary databases instead.

Fresh accounts/databases use the earlier US13/14 setup. US17 does not reset credentials or seed company data automatically. Admin and designer features still run through one server. Stop it with Ctrl+C.
