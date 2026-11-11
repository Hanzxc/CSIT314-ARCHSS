# US39 — Platform manager log in

> As a platform manager, I want to log in so that I can manage IDP categories and reports.

## Behaviour

- The platform manager logs in on the shared `/login` page with **Log in as** = Platform Manager (username and password; the password is shown as dots). `/manager/login` opens that page with Platform Manager already picked.
- On "Log in" the page checks that both fields are filled in (`validateInput(username, password)`). An empty field (or a username of only spaces) → "Please enter your username and password", and the database is not checked.
- The page trims the spaces from the username, then calls `login(username, password)`.
- `PlatformManagerLoginController.login()` makes one call: `UserAccount().verifyCredentials(username, password, REQUIRED_MANAGER_PERMISSIONS)`, where `REQUIRED_MANAGER_PERMISSIONS` = "Manage IDP categories" + "Generate reports".
- `verifyCredentials()` returns the account only if the password hash matches, the account is Active, its user profile is Active and that profile has both permissions. Otherwise it returns None. A custom profile with both permissions can log in too.
- Account found → `redirectToDashboard(account)` clears the old session, saves userId, profileId and username (never the password) and sends the manager to `/manager/dashboard`.
- None → "Invalid login details or access unavailable". The same message is used for every kind of failure, so nobody can guess which usernames exist.
- `openDashboard()` just renders the dashboard ("Welcome back, <username>", the IDP Categories and Reports cards) - it doesn't check the account or profile again.
- With User Admin picked in **Log in as**, a platform manager gets the US1 error message. Log out is US40.

## Who checks what

- **Boundary** (`PlatformManagerLoginPage`): checks the input (both fields filled in), trims the username, starts the session after a successful login and renders the dashboard.
- **Control** (`PlatformManagerLoginController`): just calls `UserAccount.verifyCredentials(username, password, REQUIRED_MANAGER_PERMISSIONS)` and returns the result - no checks of its own.
- **Entity** (`UserAccount`): checks the database - password hash, account Active, profile Active, required permissions. It reads the account's `user_profile` row itself, so the B-C-E diagram only shows `UserAccount`.
- Precondition: the manager has a user account (made with UC8) and is not logged in. Checking the role here is allowed because logging in is the use case itself. The dashboard route has `managerLoginRequired`, which only sends someone with no session to `/manager/login`.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `PlatformManagerLoginPage` — `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password): bool`, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` | `boundary/platformManagerLoginPage.py`, `templates/login.html` (shared login page), `templates/platformManagerDashboard.html` |
| Control `PlatformManagerLoginController` — `login(username, password): UserAccount \| None`, constant `REQUIRED_MANAGER_PERMISSIONS` | `control/platformManagerLoginController.py` |
| Entity `UserAccount` — `verifyCredentials(username, password, requiredPermissions): UserAccount \| None` | `entity/userAccount.py` (tables `user_account` and `user_profile`) |
| Route | POST `/login` with `role=manager` → `login()` → `PlatformManagerLoginPage`; GET `/manager/login` redirects to `/login?role=manager` (POST there still works); GET `/manager/dashboard` (`@managerLoginRequired`) → `platformManagerDashboard()` in `app.py` |

Messages: `MSG_EMPTY_FIELDS` "Please enter your username and password", `MSG_INVALID_LOGIN` "Invalid login details or access unavailable".

## Files

- `US39 Platform manager log in.drawio` — every diagram, one page each
- `US39 Platform manager log in.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Log in form.png`
  - `4b Wireframe - Missing required fields.png`
  - `4c Wireframe - Invalid login.png`
  - `4d Wireframe - Manager dashboard.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us39_platformManagerLogin.py -v
```
