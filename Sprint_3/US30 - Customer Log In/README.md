# US30 — Customer log in

> As a customer, I want to log in so that I can view and manage my saved IDPs.

## Behaviour

- Customers log in on their own page, `/customer/login` (GET shows the form, POST submits it). The shared `/login` page (US1) is for User Admins only - a customer gets the US1 error message there.
- `submitLogin(username, password)` → `validateInput(username, password)` (both fields filled in, spaces-only username counts as empty).
  - `[input is invalid]` → `displayErrorMessage(MSG_EMPTY_FIELDS)` "Please enter your username and password" (wireframe 4d). The controller isn't called.
  - `[input is valid]` → the page trims the spaces from the username (not the password) → `login(username, password)`.
- `[account != None]` → `redirectToDashboard(account)`: the old session is cleared and only `userId`, `profileId` and `username` are saved (never the password) → HTTP 302 to `/customer/dashboard` (wireframe 4b).
- `[account == None]` → `displayErrorMessage(MSG_INVALID_LOGIN)` "Invalid login details or access unavailable" (wireframe 4c) - the same message for a wrong password, an unknown username, a suspended account or profile, or a profile without the customer permission.
- `openDashboard()` just renders the customer dashboard - it doesn't check the account or profile again.
- "Manage my saved IDPs" means saving an IDP (US33) and viewing or searching the saved list (US34, US35); there is no unsave. Logging out is US36.

## Who checks what

- **Boundary** (`CustomerLoginPage`): checks that both fields are filled in and trims the username, starts the session, shows the messages.
- **Control** (`CustomerLoginController`): `login()` makes one call and returns the result: `UserAccount().verifyCredentials(username, password, REQUIRED_CUSTOMER_PERMISSIONS)`. It doesn't check the input again.
- **Entity** (`UserAccount`): `verifyCredentials()` returns the account only if the password hash matches, the account is Active, its user profile is Active and that profile has every permission in `requiredPermissions` (`REQUIRED_CUSTOMER_PERMISSIONS = {"Search, view and save IDPs"}`) - otherwise `None`. It reads the profile row itself. Checking the role is allowed here because logging in is the use case itself.
- Precondition: the customer has a user account made by the User Admin (UC8) and is not logged in. `customerLoginRequired` in `app.py` only sends someone with no session from `/customer/dashboard` to `/customer/login`.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `CustomerLoginPage` — attribute `customerLoginController`; `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password)`, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` | `boundary/customerLoginPage.py`, `templates/customerLogin.html`, `templates/customerDashboard.html` |
| Control `CustomerLoginController` — `login(username, password): UserAccount \| None`, constant `REQUIRED_CUSTOMER_PERMISSIONS` | `control/customerLoginController.py` |
| Entity `UserAccount` — `verifyCredentials(username, password, requiredPermissions): UserAccount \| None` | `entity/userAccount.py` |
| Route | GET/POST `/customer/login` → `customerLogin()`, GET `/customer/dashboard` (`@customerLoginRequired`) → `customerDashboard()` in `app.py` |

Messages: `MSG_EMPTY_FIELDS` "Please enter your username and password", `MSG_INVALID_LOGIN` "Invalid login details or access unavailable".

## Files

- `US30 Customer log in.drawio` — every diagram, one page each
- `US30 Customer log in.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Customer login.png`
  - `4b Wireframe - Customer dashboard.png`
  - `4c Wireframe - Invalid login.png`
  - `4d Wireframe - Missing fields.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us30_customerLogin.py -v
```
