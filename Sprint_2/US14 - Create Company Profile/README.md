# US14 — Create company profile

> As an interior designer, I want to create a company profile so that customers can learn about my company and its services.

US14 adds the `company_profile` table and the `CompanyProfile` entity that US15–US18 use. A logged-in designer (US13) can create one company profile from their dashboard. The full write-up (user story, use case description, diagrams, wireframes and test cases) is in `US14 Create company profile.docx`.

## Behaviour

When the designer has no company profile yet, the Company Profile card on the designer dashboard shows **Create company profile**. It opens `/designer/company/create`, where the form has these fields:

| Field | Rule |
|---|---|
| Company name * | required, 3–100 characters |
| Company description * | required, up to 2,000 characters |
| Services offered * | required, up to 1,000 characters |
| Contact email | optional, up to 254 characters, must look like an email |
| Contact phone | optional, up to 30 characters |
| Company address | optional, up to 300 characters |

Spaces at the start and end of each field are removed before checking and saving.

- **Success:** the profile is saved, and the designer goes back to the dashboard with `Company profile created successfully`. The card then shows "Company profile created" and a **View company profile** button (US15).
- **Invalid input:** `Please fix the highlighted fields`. Each wrong field shows its own error ("This field is required", "Maximum N characters", "Company name must be 3-100 characters" or "Enter a valid email address"). What was typed is kept and nothing is saved.
- **Already has a profile:** `You already have a company profile`. The existing profile is not changed.
- **Save failed for another reason:** `Company profile could not be created. Please try again`.
- **Cancel** is a link back to the dashboard. It sends nothing.

Rules:

- **One profile per designer.** `designerId` is `UNIQUE` in the table, so a second profile can't be saved even if the form is submitted twice at once.
- **The owner always comes from the session.** A `designerId` added to the form is ignored.
- **Access is checked on both GET and POST, and again in the controller** using the US13 `getAuthenticatedDesigner()`. No session redirects to `/designer/login`. Anyone without designer access, e.g. a User Admin or a designer suspended after logging in, gets "Access unavailable" (HTTP 403).
- The field rules live in `CreateCompanyProfileController.getFieldErrors()`, and US16 reuses them for updates.

## Database

`database/schema.sql` adds:

```sql
CREATE TABLE IF NOT EXISTS company_profile (
    companyId    INTEGER PRIMARY KEY AUTOINCREMENT,
    designerId   INTEGER NOT NULL UNIQUE REFERENCES user_account(userId),
    companyName  TEXT NOT NULL,   -- CHECK 3-100 characters
    description  TEXT NOT NULL,   -- CHECK 1-2000
    services     TEXT NOT NULL,   -- CHECK 1-1000
    email        TEXT NOT NULL DEFAULT '',
    phone        TEXT NOT NULL DEFAULT '',
    address      TEXT NOT NULL DEFAULT '',
    createdDate  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

You don't need to delete an existing `database/archss.db`. `initDatabase()` runs when `python app.py` starts and adds the new table.

`database/seedCompanyData.py` adds 100 demo designers (`companydemo001` … `companydemo100`, password `Demo@123`), each with a company profile. Run it after `database.seedData`. Running it again doesn't add duplicates.

## Files

| Design element | Code |
|---|---|
| Boundary `CreateCompanyProfilePage` | `boundary/createCompanyProfilePage.py` |
| Control `CreateCompanyProfileController` | `control/createCompanyProfileController.py` |
| Control (reused) `InteriorDesignerLoginController` | `control/interiorDesignerLoginController.py` (US13) |
| Entity `CompanyProfile` | `entity/companyProfile.py` — `getCompanyProfile()`, `createCompanyProfile()` |
| Table | `company_profile` in `database/schema.sql` |
| Demo data | `database/seedCompanyData.py` |
| Form | `templates/createCompanyProfile.html` |
| Dashboard button | `templates/interiorDesignerDashboard.html` |
| Route | GET/POST `/designer/company/create` in `app.py` |
| Tests | `tests/test_us14_createCompanyProfile.py` (UT14.1 – UT14.31) |

## Diagram folder

```text
US14 Create company profile.docx      write-up
US14 Create company profile.drawio    all diagrams, one page each (8 pages)
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Create button.png
  4b Wireframe - Create form.png
  4c Wireframe - Form errors.png
  4d Wireframe - Company created.png
  4e Wireframe - Existing profile.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The BCE and sequence diagrams use the same class and method names as the code.

## Run the tests

From the repository root:

```powershell
python -m pytest tests/test_us14_createCompanyProfile.py -v
python -m pytest -q
```

31 US14 tests pass, and the whole suite passes (386 tests as of 23 October 2026). Each test gets a fresh database from `conftest.py` and creates its own designer (`designer13` / `Design@123`) and sample company ("Uda Interiors"), so your demo database is never touched.

## Try it in the browser

```powershell
python -m database.seedData     # only needed once
python app.py
```

1. Open http://127.0.0.1:5000/designer/login and log in as an active designer with no company yet, e.g. `design006` / `Pass@123`.
2. On the dashboard, click **Create company profile**.
3. Try submitting with the company name empty to see the errors, then fill it in properly and click **Create company profile**.
4. The dashboard shows the success message and the **View company profile** button.

To see designers who already have a company, run `python -m database.seedCompanyData` and log in as `companydemo001` / `Demo@123`.
