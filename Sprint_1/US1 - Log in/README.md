# US1 — Log in

> As a user admin, I want to log in so that I can manage users.

## Behaviour

- `/login` shows the login form (username and password; the password is shown as dots).
- On "Log in" the page checks that both fields are filled in (`validateInput(username, password)`). An empty field → "Please enter your username and password", and the database is not checked.
- The page trims the spaces from the username, then calls `login(username, password)`.
- `LoginController.login()` makes one call: `UserAccount().verifyCredentials(username, password, REQUIRED_ADMIN_PERMISSIONS)`, where `REQUIRED_ADMIN_PERMISSIONS` = "Manage user accounts" + "Manage user profiles".
- `verifyCredentials()` returns the account only if the password hash matches, the account is Active, its user profile is Active and that profile has every required permission. Otherwise it returns None.
- Account found → `redirectToDashboard(account)` starts a new session (userId, profileId, username) and opens the User Admin dashboard (`/dashboard`).
- None → "Invalid login details or account suspended". The same message is used for a wrong username, a wrong password, a suspended account, a suspended profile and an account that isn't a User Admin, so nobody can guess which usernames exist.
- `/login` is for User Admins only. Interior designers, customers and platform managers log in on their own pages (US13 `/designer/login`, US30 `/customer/login`, US39 `/manager/login`); here they get the error message.

## Who checks what

- **Boundary** (`LoginPage`): checks the input (both fields filled in), trims the username, and starts the session after a successful login.
- **Control** (`LoginController`): just calls `UserAccount.verifyCredentials(username, password, REQUIRED_ADMIN_PERMISSIONS)` and returns the result - no checks of its own.
- **Entity** (`UserAccount`): checks the database - password hash, account Active, profile Active, required permissions. It reads the account's `user_profile` row itself, so the B-C-E diagram only shows `UserAccount`.
- Precondition: the User Admin has a user account and is not logged in. Checking the role here is allowed because logging in is the use case itself.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `LoginPage` — `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password): boolean`, `redirectToDashboard(account)`, `displayErrorMessage(msg)` | `boundary/loginPage.py`, `templates/login.html` |
| Control `LoginController` — `login(username, password): UserAccount`, constant `REQUIRED_ADMIN_PERMISSIONS` | `control/loginController.py` |
| Entity `UserAccount` — `verifyCredentials(username, password, requiredPermissions): UserAccount` | `entity/userAccount.py` (tables `user_account` and `user_profile`) |
| Route | GET / POST `/login` → `login()` in `app.py`; dashboard GET `/dashboard` |

Messages: `MSG_EMPTY_FIELDS` "Please enter your username and password", `MSG_INVALID_LOGIN` "Invalid login details or account suspended".

## Files

- `US1 Log in.drawio` — every diagram, one page each
- `US1 Log in.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Login page.png`
  - `4b Wireframe - Login failed.png`
  - `4c Wireframe - User Admin dashboard.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us1_login.py -v
```
