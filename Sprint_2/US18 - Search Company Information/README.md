# US18 — Search company information

> As an interior designer, I want to search my company’s information so that I can find the details I need.

Apply this repository update **after US13–17**. The package keeps the same Python helper/test format, camelCase naming, three diagram types, one editable draw.io file and labelled PNG wireframes with Notes panels. The sample name remains `Tengku Uda Designer` (`designer13` / `Design@123`). Only repository files are packaged; no complete project is included.

## Behaviour and design assumption

Each designer currently owns one company profile. US18 therefore searches **fields inside that designer's company information**, rather than listing/searching other designers' companies. Results are rows with a **Field** label and its saved **Information**. This interpretation is an assumption to confirm with your group/tutor.

From the company view, select **Search company information**. The search page is `/designer/company/search`; submitting uses GET with the `keyword` query parameter. A keyword matches a partial **field label OR saved value**. Search is case-insensitive, trims surrounding spaces and treats characters such as `%` literally rather than as SQL wildcards. It reads the current saved company record and never changes it.

Searched fields, in display order:

1. Company name
2. Company description
3. Services offered
4. Contact email
5. Contact phone
6. Company address

Empty/space-only keyword and **Clear** show all six fields. A matching label such as `phone` can return its row even if its optional value is blank; blank optional values display `Not provided`. That placeholder is display text, not part of the saved information being searched. No matches shows `No matching company information found` with HTTP 200 and retains the keyword. An authorised designer with no company profile instead gets the existing missing-profile response (404) with a US14 creation link.

Ownership always comes from the authenticated session. A `designerId` or `companyId` in the URL cannot select another company's data. US13 account/profile status and designer permissions are rechecked; missing session redirects to designer login, unsuitable access returns 403. Company/account IDs, creation timestamps and private account credentials are excluded from searched fields. Updates from US16 are searchable immediately; a US17-deleted company cannot be searched.

## Repository files

Add these new files to the matching existing folders:

```text
boundary/searchCompanyInformationPage.py
control/searchCompanyInformationController.py
templates/searchCompanyInformation.html
tests/test_us18_searchCompanyInformation.py
Sprint_2/US18 - Search Company Information/...
```

Combine these modified files with your group's latest versions:

```text
app.py
entity/companyProfile.py
templates/viewCompanyProfile.html
```

All implementation files in the ZIP are required, alongside the test and Sprint_2 folder. Paths are relative to the repository root. Add files to existing folders; keep other group files and preserve any newer shared changes when combining modified versions. `CompanyProfile` gains a search method and a constant mapping its six business fields to labels; its existing create/get/update/delete methods are retained. No schema change or migration is needed. US13–17 test files are unchanged. No Git commit, push or merge has been performed.

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `SearchCompanyInformationPage` | `boundary/searchCompanyInformationPage.py` |
| Control `SearchCompanyInformationController` | `control/searchCompanyInformationController.py` |
| Entity `CompanyProfile` | Extended `entity/companyProfile.py` |
| Shared access control | Existing `InteriorDesignerLoginController.getAuthenticatedDesigner()` |
| Results UI | `templates/searchCompanyInformation.html` |
| Entry link | `templates/viewCompanyProfile.html` |
| Route | GET `/designer/company/search` in `app.py` |

The entity's search first loads only the owner-specific row through the existing parameterised `getCompanyProfile(designerId)`. It then checks the six labels/values in Python using case-folded substring comparison. Results are dictionaries `{field, label, value}`; they are data structures, not extra entity classes. No search result returns another company's row.

The single sequence diagram follows access checking, profile existence, searching and results/no-results responses. Early access denial is stated at its top. The BCE diagram uses the actual class and method names, showing only relevant members of reused classes.

```text
US18 Search company information.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Search button.png
  4b Wireframe - Search results.png
  4c Wireframe - No matching information.png
  4d Wireframe - All information.png
  4e Wireframe - Profile not found.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains eight editable pages. PNGs are locally rendered vector illustrations checked visually, not browser screenshots. Written use case descriptions, Word reports and written test case tables remain deferred.

## Automated pass/fail tests

Open a terminal at your group's **repository root**, after combining all files:

```powershell
python -m pytest tests/test_us18_searchCompanyInformation.py -v --basetemp=.test-tmp-us18
python -m pytest -q --basetemp=.test-tmp-all
```

If `python` is not recognised on the computer used for these packages:

```powershell
$us18Python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
& $us18Python -m pytest tests/test_us18_searchCompanyInformation.py -v --basetemp=.test-tmp-us18
& $us18Python -m pytest -q --basetemp=.test-tmp-all
```

**Verified: 28 US18 tests passed; 330 tests passed overall**, including all 302 prior tests. Tests cover partial values and labels, capitalisation, whitespace/empty search, no matches, literal wildcard characters, optional blank values, access restrictions, owner isolation, forged owner fields, escaping, unchanged data and search after update/deletion.

The existing `conftest.py` gives every test an isolated temporary database. Local helpers add the fictional designer and company. No server or manual credential entry is needed, and tests do not change the demo database. Keep `--basetemp` folders dedicated to disposable test files; pytest recreates them. The initial test run failed because the new controller was absent; final runs passed. This records this development session, not earlier group work.

## Try the website

From the repository root start the same application:

```powershell
python app.py
```

Use the explicit Python executable above if necessary. Leave the terminal running and open `http://127.0.0.1:5000/login`.

1. Log in with your existing fictional designer account, for example `designer13` / `Design@123` if set up in US13/14.
2. If you deleted the sample company in US17, create a company again through US14.
3. Open **View company profile**, then **Search company information**.
4. Try these keywords against the original sample data:

| Keyword | Expected result |
|---|---|
| `renov` | Services offered: Space planning, renovation |
| `PHONE` | Contact phone: +65 6123 4567 |
| `hello@` | Contact email: hello@udainteriors.com |
| `Design Street` | Company address: 10 Design Street |
| `zzzz` | No matching company information found |
| Empty, or select Clear | All six company fields |

Results reflect your currently saved values. If you changed the sample values in US16, search for those new values or use field labels such as `phone` or `services`.

**Back to company profile** returns to the read-only company view. Search itself does not save, delete or recreate a company. Existing US13/14 setup handles fresh accounts/databases; this update does not reset credentials or seed data. All stories still run through one server. Stop it with Ctrl+C.
