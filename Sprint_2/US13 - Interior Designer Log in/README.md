# US13 — Interior designer log in

> As an interior designer, I want to log in so that I can manage my company’s information and IDPs.

## Behaviour

- The designer logs in on the shared `/login` page with **Log in as** = Interior Designer (username and password; the password is shown as dots). `/designer/login` opens that page with Interior Designer already picked.
- On "Log in" the page checks that both fields are filled in (`validateInput(username, password)`). An empty field (or a username of only spaces) → "Please enter your username and password", and the database is not checked.
- The page trims the spaces from the username, then calls `login(username, password)`.
- `InteriorDesignerLoginController.login()` makes one call: `UserAccount().verifyCredentials(username, password, REQUIRED_DESIGNER_PERMISSIONS)`, where `REQUIRED_DESIGNER_PERMISSIONS` = "Manage company profile" + "Manage own IDPs".
- `verifyCredentials()` returns the account only if the password hash matches, the account is Active, its user profile is Active and that profile has both permissions. Otherwise it returns None. A custom profile with both permissions can log in too - we check the permissions, not the profile name.
- Account found → `redirectToDashboard(account)` clears the old session, saves userId, profileId and username (never the password) and sends the designer to `/designer/dashboard`.
- None → "Invalid login details or access unavailable". The same message is used for a wrong username, a wrong password, a suspended account, a suspended profile and an account that isn't an interior designer.
- `openDashboard()` just renders the dashboard - it doesn't check the account or profile again. It shows "Welcome back, <username>" and the Company Profile, Current IDPs, Past IDPs and IDP Statistics cards. For the Company Profile card it borrows two controllers:
  - US15 `ViewCompanyProfileController.viewCompanyProfile(designerId)` → an Active profile → "View company profile";
  - US17-R `RestoreCompanyProfileController.getSuspendedCompanyProfile(designerId)` → a deleted (Suspended) profile → "Restore company profile" with hidden `companyId` and `revision`;
  - neither → "Create company profile" (US14).
- With User Admin picked in **Log in as**, a designer gets the US1 error message.

## Who checks what

- **Boundary** (`InteriorDesignerLoginPage`): checks the input (both fields filled in), trims the username, starts the session after a successful login and renders the dashboard.
- **Control** (`InteriorDesignerLoginController`): just calls `UserAccount.verifyCredentials(username, password, REQUIRED_DESIGNER_PERMISSIONS)` and returns the result - no checks of its own.
- **Entity** (`UserAccount`): checks the database - password hash, account Active, profile Active, required permissions. It reads the account's `user_profile` row itself, so the B-C-E diagram only shows `UserAccount` (plus `CompanyProfile`, used only by the two borrowed controllers).
- Precondition: the designer has a user account (made with UC8) and is not logged in. Checking the role here is allowed because logging in is the use case itself. The dashboard route has `designerLoginRequired`, which only sends someone with no session to `/designer/login`.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `InteriorDesignerLoginPage` — `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password): bool`, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` | `boundary/interiorDesignerLoginPage.py`, `templates/login.html` (shared login page), `templates/interiorDesignerDashboard.html` |
| Control `InteriorDesignerLoginController` — `login(username, password): UserAccount \| None`, constant `REQUIRED_DESIGNER_PERMISSIONS` | `control/interiorDesignerLoginController.py` |
| Borrowed control `«control» (from US15) ViewCompanyProfileController` — `viewCompanyProfile(designerId)` | `control/viewCompanyProfileController.py` |
| Borrowed control `«control» (from US17-R) RestoreCompanyProfileController` — `getSuspendedCompanyProfile(designerId)` | `control/restoreCompanyProfileController.py` |
| Entity `UserAccount` — `verifyCredentials(username, password, requiredPermissions): UserAccount \| None` | `entity/userAccount.py` (tables `user_account` and `user_profile`) |
| Entity `CompanyProfile` — `getCompanyProfile(designerId)`, `getSuspendedCompanyProfile(designerId)` (through the borrowed controllers) | `entity/companyProfile.py` |
| Route | POST `/login` with `role=designer` → `login()` → `InteriorDesignerLoginPage`; GET `/designer/login` redirects to `/login?role=designer` (POST there still works); GET `/designer/dashboard` (`@designerLoginRequired`) → `interiorDesignerDashboard()` in `app.py` |

Messages: `MSG_EMPTY_FIELDS` "Please enter your username and password", `MSG_INVALID_LOGIN` "Invalid login details or access unavailable".

## Files

- `US13 Interior designer log in.drawio` — every diagram, one page each
- `US13 Interior designer log in.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Log in form.png`
  - `4b Wireframe - Missing required fields.png`
  - `4c Wireframe - Invalid login.png`
  - `4d Wireframe - Designer dashboard.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us13_interiorDesignerLogin.py -v
```
