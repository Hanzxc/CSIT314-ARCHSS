# US36 — Customer log out

> As a customer, I want to log out so that other people cannot use my account.

## Behaviour

- Every customer page has a "Log out" button in the header (POST `/customer/logout`, in `customerBase.html`). GET on that address is not allowed (HTTP 405) and doesn't log anyone out.
- Clicking it calls `logout()`: the controller notes whether a customer was logged in (`loggedOut = "userId" in session`), clears the whole session once (`session.clear()`) and returns `loggedOut`. It does not call US2's `LogoutController`.
- `[loggedOut == True]` → `displayLoginPage(MSG_LOGGED_OUT)` → HTTP 302 to `/customer/login` with "You have logged out successfully" (wireframe 4b).
- `[loggedOut == False]` (the session had already ended) → `displayLoginPage(MSG_SESSION_ENDED)` → HTTP 302 to `/customer/login` with "Your session has already ended" (wireframe 4c). No error page.
- The message is shown once (flash). After logging out, the dashboard, Search IDPs and View IDP send the customer to `/customer/login` (`customerLoginRequired`, wireframe 4d).
- A customer can always log out, even if their account or profile was suspended after logging in. Only this browser's session ends; no saved data changes.

## Who checks what

- **Boundary** (`CustomerLogoutPage`): picks the message from the controller's result and redirects to the customer login page.
- **Control** (`CustomerLogoutController`): ends the session itself and returns whether a session was ended. There is no input to check.
- **Entity**: none - log out doesn't read or change any saved data.
- Precondition: none is enforced - `/customer/logout` has no decorator, so clicking it with no session just shows "Your session has already ended".

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `CustomerLogoutPage` — attribute `customerLogoutController`; `clickLogout()`, `displayLoginPage(msg)` | `boundary/customerLogoutPage.py`, Log out button in `templates/customerBase.html`, message on `templates/customerLogin.html` |
| Control `CustomerLogoutController` — `logout(): bool` | `control/customerLogoutController.py` |
| Route | POST `/customer/logout` → `customerLogout()` in `app.py` |

Messages: `MSG_LOGGED_OUT` "You have logged out successfully", `MSG_SESSION_ENDED` "Your session has already ended".

## Files

- `US36 Customer log out.drawio` — every diagram, one page each
- `US36 Customer log out.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Customer logout action.png`
  - `4b Wireframe - Logout successful.png`
  - `4c Wireframe - Session already ended.png`
  - `4d Wireframe - Protected page after logout.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us36_customerLogout.py -v
```
