# TODO — upgrades to make the app better

- **Part A:** US17, suspend the company profile instead of deleting it
- **Part B:** whole app, protect against forged form submissions (CSRF)

---

# Part A — US17: suspend the company profile instead of deleting it

**Why:** right now "Delete company profile" removes the row from `company_profile` for good. If a designer deletes by mistake, the company information is gone and there's no undo. Marking the row as `Suspended` instead keeps the data so it can be brought back. It also matches how the User Admin stories handle accounts and profiles (US6, US11 use a status, not a delete).

The confirmation box and token from US17 stay as they are. They protect against clicking Delete by accident. This change protects against what happens *after* a mistaken delete.

---

## 0. Decide first (whole team)

- [ ] **Wording.** The user story (#17) says "delete … so that it is no longer shown on the platform". Suggestion: keep the story, the use case name (UC17 Delete company profile), the button text and the success message the same, and only change what happens in the database. A suspended profile is "no longer shown", so the story is still met. Write this down as an assumption in the US17 doc.
- [ ] **How does a designer get it back?** Suspending only helps if there's a way to undo it. Pick one:
  - **(a) Recommended — reuse Create.** If a designer with a suspended profile clicks "Create company profile", the old row is reactivated with the new details. This keeps one row per designer (`designerId` is UNIQUE) and needs no new page.
  - **(b) Add a "Restore company profile" button** on the dashboard that reactivates the old details as they were. Nicer, but it's a new feature, so it needs its own wireframe and tests.
  - **(c) No restore for now.** The data is kept in the database and could be restored by hand. Simplest, but the designer can't undo anything themselves.

## 1. Database — `database/schema.sql` and `database/db.py`

- [ ] Add a status column to `company_profile`, using the same values as everywhere else:
  ```sql
  status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Suspended'))
  ```
- [ ] **Existing databases won't get the new column by themselves.** `CREATE TABLE IF NOT EXISTS` skips tables that already exist. Either:
  - add a small check in `initDatabase()`: if `PRAGMA table_info(company_profile)` has no `status` column, run `ALTER TABLE company_profile ADD COLUMN status TEXT NOT NULL DEFAULT 'Active'`, **or**
  - tell everyone to delete `database/archss.db` and run `python -m database.seedData` again.

## 2. Entity — `entity/companyProfile.py`

- [ ] `getCompanyProfile(designerId)`: only return Active rows (`... WHERE designerId = ? AND status = 'Active'`). This makes view (US15), update (US16) and search (US18) treat a suspended profile as "not created yet" with no other changes.
- [ ] Replace `deleteCompanyProfile(designerId, companyId)` with `suspendCompanyProfile(designerId, companyId)`:
  ```sql
  UPDATE company_profile SET status = 'Suspended'
  WHERE designerId = ? AND companyId = ? AND status = 'Active'
  ```
  Return `cursor.rowcount == 1`, the same as now. Suspending twice still returns False.
- [ ] `updateCompanyProfile()`: add `AND status = 'Active'` so a suspended profile can't be edited.
- [ ] `searchCompanyInformation()`: no change needed, because it already goes through `getCompanyProfile()`.
- [ ] For restore option (a): `createCompanyProfile()` must reactivate a suspended row instead of inserting. Otherwise the UNIQUE `designerId` makes the insert fail, and the designer sees "Company profile could not be created". For example, try an `UPDATE ... SET <fields>, status = 'Active' WHERE designerId = ? AND status = 'Suspended'` first, and only `INSERT` if no row was changed.

## 3. Control and boundary

- [ ] `DeleteCompanyProfileController.deleteCompanyProfile()` calls `CompanyProfile().suspendCompanyProfile(...)`. Keep the class and method names if you keep the "delete" wording (step 0). They have to match the class diagram.
- [ ] `DeleteCompanyProfilePage`: no logic change. You could reword the confirmation box text ("This removes your company information from the platform. Your user account is kept.") if the team wants to mention it can be restored.
- [ ] **Stale confirmation check.** Today an old confirmation can't remove a newer profile because the new profile gets a new `companyId`. With restore option (a) the `companyId` stays the same, so this protection is lost. Fix: clear `session["companyDeleteConfirmation"]` whenever a profile is created or restored (in `CreateCompanyProfilePage.submitCompanyProfile()` on success).
- [ ] `CreateCompanyProfileController.hasCompanyProfile()` uses `getCompanyProfile()`, so it will correctly say "no profile" for a suspended one. Check that the create flow then reactivates instead of failing.

## 4. Tests

These existing tests check that the row is gone and will need changing:

- [ ] `tests/test_us17_deleteCompanyProfile.py`
  - UT17.1: `countCompanies() == 0` → the row still exists with `status == 'Suspended'`.
  - UT17.7: `countCompanies() == 1` after one delete → there are still 2 rows; check the statuses instead.
  - UT17.9 and UT17.25 (old id / stale confirmation vs replacement): rewrite for the chosen restore option. With (a) the id is reused, so test that the confirmation was cleared when the profile was restored.
  - UT17.28: `countCompanies() == 0` → one Suspended row.
- [ ] New tests to add:
  - a suspended profile isn't shown by view (404), update (404) or search (404)
  - `updateCompanyProfile()` on a suspended profile returns False and changes nothing
  - suspending twice returns False the second time
  - the suspended row keeps all its data (company name, services, etc.)
  - (option a) creating after suspending reactivates the same row: one row, `status == 'Active'`, new details
- [ ] Run `python -m pytest -q`. Everything outside US17 should still pass, since US15/16/18 go through `getCompanyProfile()`.

## 5. Documents and diagrams

- [ ] `Sprint_2/US17 - Delete Company Profile/US17 Delete company profile.docx`: assumptions, basic flow step 6 ("marks the company profile as Suspended"), postconditions, the CompanyProfile row in the BCE table, the sequence diagram text and the affected unit test rows. (The docx is generated from the Sprint 1 template, so ask whoever made it to regenerate, or edit it by hand.)
- [ ] `Sprint_2/US17 - Delete Company Profile/US17 Delete company profile.drawio`: in the BCE diagram, change `deleteCompanyProfile(designerId, companyId)` to `suspendCompanyProfile(...)` on the entity and add the `status` attribute. Update the note (`DELETE company_profile WHERE …` → `UPDATE … SET status = 'Suspended'`). In the sequence diagram, rename message 25. Then re-export `5 BCE Class Diagram.png` and `6 Sequence Diagram.png`.
- [ ] `US14` docs (only for restore option a): creating when a suspended profile exists reactivates it.
- [ ] `Sprint_2/US17 - Delete Company Profile/README.md`: replace the "physical delete" paragraph.
- [ ] Root `README.md`: update the CompanyProfile attributes (add `status`) and the method table (`suspendCompanyProfile`).

---

# Part B — whole app: protect against forged form submissions (CSRF)

**What the problem is:** a forged submission (cross-site request forgery, CSRF) is when another website secretly sends a form to our app while the user is still logged in to it in the same browser. The browser sends our login cookie along with that form, so the app treats it as a real request from the user. For example, a page could quietly post to `/accounts/<id>/suspend` while a User Admin has our app open.

**Where we are now:**

- 14 templates have a POST form. Only the US17 delete box checks a token (`confirmationToken`). The forms in the other 13 have no protection:
  `base.html` (admin Log out), `login.html`, `createUserProfile.html`, `updateUserProfile.html`, `viewUserProfile.html` (suspend box), `createUserAccount.html`, `updateUserAccount.html`, `viewUserAccount.html` (suspend box), `interiorDesignerBase.html` (designer Log out), `interiorDesignerLogin.html`, `createCompanyProfile.html`, `updateCompanyProfile.html`, `platformManagerLogin.html`.
- Good already: every change happens through POST, and GET only opens forms or confirmation boxes. Keep it that way for new stories.
- Chrome and Edge block most cross-site form posts by default, but Firefox and Safari don't behave the same way. Flask doesn't set the cookie option that makes this reliable, so we shouldn't depend on it.

## 1. Turn on CSRF tokens for every form (Flask-WTF)

- [ ] Add `flask-wtf` to `requirements.txt` and run `pip install -r requirements.txt`.
- [ ] In `app.py`, after `app = Flask(__name__)`:
  ```python
  from flask_wtf.csrf import CSRFProtect
  csrf = CSRFProtect(app)
  ```
  Every POST without a valid token is now rejected with HTTP 400.
- [ ] Add this line inside **every** `<form method="POST">` in the 14 templates listed above, including `deleteCompanyProfile.html`:
  ```html
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  ```
  Tip: after adding them, search the templates for `method="POST"` and check each match has the line.
- [ ] Optional: show a friendly page instead of the plain "400 Bad Request". Use `@app.errorhandler(CSRFError)` and say something like "This form has expired - please go back and try again".
- [ ] Keep the US17 `confirmationToken`. It does a different job: it stops an old confirmation from deleting a newer profile.

## 2. Tell browsers not to send our cookie with other sites' forms

- [ ] In `app.py`:
  ```python
  app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
  ```
  This is a second layer of protection on top of the tokens. Flask already sets `SESSION_COOKIE_HTTPONLY = True` by default, so JavaScript can't read the cookie.

## 3. Tests

- [ ] In `tests/conftest.py`, switch CSRF off for the normal tests so the existing 386 tests don't all fail with 400:
  ```python
  from app import app
  app.config["WTF_CSRF_ENABLED"] = False
  ```
- [ ] Add a small test file (e.g. `tests/test_csrf.py`) that turns it **on** and checks:
  - a POST without a token is rejected (400) and nothing changes, e.g. for create user account and create company profile
  - a POST with the token from the page works
  - the login and logout forms still work with the token
- [ ] Run `python -m pytest -q`.

## 4. Before we push it live (end of project)

- [ ] **Change the secret key.** `app.py` line 36 has `app.secret_key = "change-this-later"`. Flask signs the login cookie with this key, and the CSRF tokens will depend on it too. Anyone who knows it can make their own login cookie. Read it from an environment variable instead:
  ```python
  import os
  app.secret_key = os.environ["SECRET_KEY"]
  ```
  Use a long random value, e.g. from `python -c "import secrets; print(secrets.token_hex(32))"`. The old value is in the git history, so use a **new** value. Don't just move the old one.
- [ ] Use HTTPS on the live site and set `app.config["SESSION_COOKIE_SECURE"] = True`, so the cookie is only sent over HTTPS.
- [ ] Turn off debug mode: `app.run(debug=True)` in `app.py` must not be used on the live server.

## 5. Documents

- [ ] Root `README.md`: add `flask-wtf` to the tech table, and add `csrf_token` to the "HTML form field names" list, with a note that every POST form must include it.
- [ ] Mention CSRF protection as an assumption in future story write-ups that add forms.
