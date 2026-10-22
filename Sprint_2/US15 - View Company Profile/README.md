# US15 — View company profile

> As an interior designer, I want to view my company profile so that I can check what customers see.

Apply this repository update **after US13 and US14**. The package follows the same simple Python test style, camelCase naming, three UML diagram types, numbered diagram PNGs, one editable draw.io file, and labelled wireframes with Notes panels. The sample designer remains `Tengku Uda Designer`, username `designer13`, password `Design@123`.

## What it adds

The Company Profile card on the designer dashboard now shows **View company profile** once a profile exists. The link opens `/designer/company` and displays the saved company name, description, services, email, phone and address. Blank optional contact fields show `Not provided`. Back to dashboard returns without changing data.

This is a read-only preview of the public-facing company content. The business details are in a reusable `companyProfileDetails.html` template, ready for later customer pages to include. Actual customer navigation/routes are outside US15 and are not claimed to be implemented. The designer navigation remains outside this reusable company card. Internal IDs, timestamps, account full name, account email and credentials are not displayed in the company card.

The view always uses the authenticated session's userId. A designer cannot choose a different owner through URL parameters. US13 account/profile status and designer permission checks are reused. No login session redirects to designer login; unsuitable access returns 403. An authorised designer with no profile gets a 404 page explaining that no profile exists, with a link to US14 creation. Edit, delete and logout remain in their assigned stories.

## Files to put into the group repository

New files:

```text
boundary/viewCompanyProfilePage.py
control/viewCompanyProfileController.py
templates/viewCompanyProfile.html
templates/companyProfileDetails.html
templates/companyProfileNotFound.html
tests/test_us15_viewCompanyProfile.py
Sprint_2/US15 - View Company Profile/...
```

Modified files to combine with your group's latest versions:

```text
app.py
templates/interiorDesignerDashboard.html
```

The archive's paths are relative to the repository root. Add new files to existing matching folders; do not replace whole folders. The modified files are based on the last delivered US14 version, so preserve any newer group changes when combining them. This is a prepared repository update; no commit, push or Git merge has been performed.

US15 reuses `CompanyProfile.getCompanyProfile(designerId)` and the US14 database table without changing the entity or schema. There is no new migration. All US13 and US14 test files are unchanged. The archive excludes database files and caches, and contains no complete project package.

## Code/diagram mapping

| Design element | Code |
|---|---|
| Boundary `ViewCompanyProfilePage` | `boundary/viewCompanyProfilePage.py` |
| Control `ViewCompanyProfileController` | `control/viewCompanyProfileController.py` |
| Entity `CompanyProfile` | Existing US14 `entity/companyProfile.py`, unchanged |
| Shared access check | Existing US13 `InteriorDesignerLoginController`, unchanged |
| Company details | `templates/companyProfileDetails.html` |
| Designer view wrapper | `templates/viewCompanyProfile.html` |
| Missing-profile response | `templates/companyProfileNotFound.html` |
| Route | GET `/designer/company` in `app.py` |

The BCE diagram uses the actual class and method names. It shows only relevant methods of reused classes. The single sequence diagram follows `clickView()`, access checks, the owner-specific lookup and the success/missing-profile response. The no-session redirect is stated at the top of the diagram.

## Diagram folder

```text
US15 View company profile.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - View button.png
  4b Wireframe - Company details.png
  4c Wireframe - No company profile.png
  4d Wireframe - Optional fields empty.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains seven editable pages. PNGs are report images generated locally from the vector boards and checked visually; they are not browser screenshots. Written use case descriptions and written test case tables remain deferred.

## Run pass/fail tests

Open a terminal **at your group repository root**, not inside Sprint_2 or tests. With Python configured:

```powershell
python -m pytest tests/test_us15_viewCompanyProfile.py -v --basetemp=.test-tmp-us15
python -m pytest -q --basetemp=.test-tmp-all
```

On the computer used to prepare this package, Python was available at the following path. If `python` is not recognised, use:

```powershell
$us15Python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
& $us15Python -m pytest tests/test_us15_viewCompanyProfile.py -v --basetemp=.test-tmp-us15
& $us15Python -m pytest -q --basetemp=.test-tmp-all
```

**Verified results: 24 US15 tests passed; 246 tests passed overall**, including all 222 preceding tests. No website server is needed for automated tests. The existing `conftest.py` supplies an isolated temporary database for every test, and local helper functions create the designer/company data they need. `--basetemp` folders are for disposable test files; pytest recreates them.

The tests check company fields, no profile, access restrictions, suspended accounts/profiles, ownership separation, ignored forged owner parameters, escaped text, no private account details in the business card, optional empty contacts, read-only behaviour, dashboard links and the create-then-view integration flow. The initial pre-implementation run failed because the new controller was absent; the final runs above passed. This records this development session, not earlier group work.

## Try the website

After adding all files, run the same application as before:

```powershell
python app.py
```

Use the explicit Python executable above if necessary. Leave the terminal running and open `http://127.0.0.1:5000/login` in your browser.

1. Log in as `designer13` / `Design@123` (if you created this demo account during US13/14).
2. If there is no company yet, use US14's Create company profile first.
3. On the dashboard, select **View company profile**.
4. Check the displayed information, then select **Back to dashboard**.

If you already saved a profile in US14, this view reads that same profile. US15 does not reset data or create another company. On a fresh database, run the existing `database.seedData` setup and create a designer account as described in the US13/14 instructions before logging in. Your admin can also create an account assigned to an active Interior Designer profile.

The same single server runs admin and designer features. Stop it with Ctrl+C when finished.
