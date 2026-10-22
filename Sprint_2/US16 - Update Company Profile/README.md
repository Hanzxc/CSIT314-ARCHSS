# US16 — Update company profile

> As an interior designer, I want to update my company profile so that customers see the latest information.

Apply this repository update **after US13, US14 and US15**. It follows the same folder numbering, camelCase Python naming, simple test functions and helpers, three diagram types, one editable draw.io file, and labelled wireframe images with Notes panels. The sample designer remains `Tengku Uda Designer` (`designer13` / `Design@123`). No complete package is included.

## Behaviour

From the US15 company profile view, select **Update company profile**. The form loads the saved company name, description, services, email, phone and address. Select **Save changes** to validate and save; success redirects to the company profile view with `Company profile updated successfully` and the new business information. **Cancel** returns to that view without sending a save request.

The existing company record is updated. `companyId`, `designerId` and `createdDate` stay unchanged. No extra profile is inserted. An authorised designer with no profile receives the existing 404/missing-profile page with a US14 creation link. If the profile disappears before saving, an update still does not recreate it.

The same US14 rules apply: company name (3–100 characters), description (required, up to 2,000), services (required, up to 1,000); optional email (up to 254, basic format check), phone (up to 30) and address (up to 300). Fields are trimmed. Optional fields can be cleared. Invalid input retains attempted values in the form and leaves the saved record unchanged.

Ownership comes only from the authenticated session. Posted/query owner or company IDs are ignored. US13 account/profile status and designer permission checks are reused before opening and submitting the form, and repeated in the control. No session redirects to designer login; unsuitable access returns 403 before writing. The shared US15 company-content template reads the updated row, so future customer pages using that template/data receive the current company information; customer navigation/routes are still outside these designer stories.

## Repository files

Add these new files to the matching existing folders:

```text
boundary/updateCompanyProfilePage.py
control/updateCompanyProfileController.py
templates/updateCompanyProfile.html
tests/test_us16_updateCompanyProfile.py
Sprint_2/US16 - Update Company Profile/...
```

Combine these modified files with the group's latest versions:

```text
app.py
entity/companyProfile.py
templates/viewCompanyProfile.html
```

The entity adds `updateCompanyProfile(designerId, companyData)`; its existing create/get methods remain intact. The schema is unchanged, so no migration is required. US13, US14 and US15 test files are unchanged. All implementation files in the ZIP are required, not just the test and Sprint_2 folder. The archive paths are relative to the repository root. Keep other group files; do not replace entire folders or overwrite newer shared edits blindly. No commit, push or Git merge has been performed.

## Diagram and code consistency

| Element | Implementation |
|---|---|
| Boundary `UpdateCompanyProfilePage` | `boundary/updateCompanyProfilePage.py` |
| Control `UpdateCompanyProfileController` | `control/updateCompanyProfileController.py` |
| Entity `CompanyProfile` | Extended `entity/companyProfile.py` |
| Shared access check | Existing `InteriorDesignerLoginController.getAuthenticatedDesigner()` |
| Shared field rules | Existing `CreateCompanyProfileController.getFieldErrors()` |
| Edit form | `templates/updateCompanyProfile.html` |
| Entry link | `templates/viewCompanyProfile.html` |
| Route | GET/POST `/designer/company/update` in `app.py` |

The single sequence diagram follows submitting Save changes, validation, updating the owner-specific row and the success/failure response. Its top notes explain the initial GET/prepopulation and early access-denial flows. Relevant methods of reused classes are shown in the BCE diagram; unused members are omitted. `companyData` uses the same six field keys as US14.

```text
US16 Update company profile.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Update button.png
  4b Wireframe - Update form.png
  4c Wireframe - Update errors.png
  4d Wireframe - Company updated.png
  4e Wireframe - Profile not found.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains eight editable pages. PNGs are locally rendered vector illustrations, checked visually; they are not browser screenshots. Written use case descriptions, Word reports and written test case tables remain deferred.

## Automated pass/fail tests

Open a terminal at the **group repository root**, after combining all files:

```powershell
python -m pytest tests/test_us16_updateCompanyProfile.py -v --basetemp=.test-tmp-us16
python -m pytest -q --basetemp=.test-tmp-all
```

If `python` is not recognised on the computer used for these packages, use the installed executable:

```powershell
$us16Python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
& $us16Python -m pytest tests/test_us16_updateCompanyProfile.py -v --basetemp=.test-tmp-us16
& $us16Python -m pytest -q --basetemp=.test-tmp-all
```

**Verified: 28 US16 tests passed; 274 tests passed overall**, including all 246 prior tests. Tests cover valid updates, all six saved fields, stable identity/owner/time, missing records, access restrictions, invalid fields, optional field clearing, trimming, owner isolation, database rollback, prefilled form values, redirects/messages, retained invalid input, cancel, forged ownership, changed permissions and create-update-view integration.

The existing `conftest.py` supplies a fresh isolated database per test. Helpers create the fictional designer/company data. No server or manual credential entry is required, and these tests do not modify the demo database. `--basetemp` folders are disposable pytest scratch folders and are recreated by pytest. The initial test run failed because the new controller did not exist; the final runs passed. This is evidence of this development session, not prior group work.

## Try it in the browser

From the repository root start the same server as before:

```powershell
python app.py
```

Use the explicit executable above if needed. Leave the terminal running and open `http://127.0.0.1:5000/login`. Log in with your existing designer account, such as `designer13` / `Design@123` if you set up that account in US13/14.

1. If no company exists yet, create it through US14.
2. Select **View company profile** on the designer dashboard.
3. Select **Update company profile**.
4. Change the fields, for example:

| Field | Updated example |
|---|---|
| Company name | Uda Interiors Studio |
| Description | Modern homes and offices. |
| Services | Renovation, office design |
| Email | studio@udainteriors.com |
| Phone | +65 6987 6543 |
| Address | 20 Studio Street |

5. Select **Save changes** and check the success message and updated company view.

To try an error, clear the required company name and save. To try Cancel, change a value in the form and choose Cancel; the original saved details remain. Saving valid changes updates the real demo database and persists across restarts. Automated tests use fresh data, so you can repeat them freely.

Fresh databases/accounts use the existing US13/14 setup instructions; US16 does not reset credentials or company data. No separate server is needed for each story. Stop the application with Ctrl+C.
