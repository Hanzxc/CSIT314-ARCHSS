# US40 — Platform manager log out

> As a platform manager, I want to log out so that other people cannot use my account.

## Behaviour

- Every Platform Manager page has a "Log out" button in the header (the dashboard and the IDP category pages). It sends a POST to `/manager/logout`; opening `/manager/logout` with GET is not allowed and doesn't log anyone out.
- Clicking it calls `clickLogout()` → `logout()`: the controller notes whether someone was logged in (`loggedOut = "userId" in session`), clears the session and returns `loggedOut`. It does its own work - it doesn't call the US2 `LogoutController`.
- `loggedOut == True` → `displayLoginPage(MSG_LOGGED_OUT)`: the manager login page with "You have logged out successfully" (wireframe 4b).
- `loggedOut == False` (the session had already ended, e.g. it timed out or Log out came from an old tab) → `displayLoginPage(MSG_SESSION_ENDED)`: "Your session has already ended" (wireframe 4c). No error page.
- `displayLoginPage(msg)` flashes the message and redirects (HTTP 302) to `/manager/login`; the message is shown once only.
- After logging out, the dashboard and every `/manager/categories` page send the person to the manager login page (wireframe 4d): `managerLoginRequired` only lets a request through when there is a session.
- Logging out doesn't change the user account or any IDP category, and it only ends the session in this browser. The User Admin's log out (US2) and the designer's log out (US19) are separate stories.

## Who checks what

- **Boundary** (`PlatformManagerLogoutPage`): picks the message from the controller's result and redirects to the manager login page. There is no input to check.
- **Control** (`PlatformManagerLogoutController`): ends the session and returns whether a session was ended - one controller per use case, no other controller is called.
- **Entity**: none - log out doesn't read or change any saved data.
- Precondition: none is enforced - `/manager/logout` has no decorator in `app.py`, so logging out with no session just shows "Your session has already ended".

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `PlatformManagerLogoutPage` — `clickLogout()`, `displayLoginPage(msg)`; attribute `platformManagerLogoutController` | `boundary/platformManagerLogoutPage.py`, Log out button in `templates/platformManagerBase.html` and `templates/platformManagerDashboard.html` |
| Control `PlatformManagerLogoutController` — `logout(): bool` | `control/platformManagerLogoutController.py` |
| Route | POST `/manager/logout` → `platformManagerLogout()` in `app.py` |

Messages: `MSG_LOGGED_OUT` "You have logged out successfully", `MSG_SESSION_ENDED` "Your session has already ended".

## Files

- `US40 Platform manager log out.drawio` — every diagram, one page each
- `US40 Platform manager log out.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Logout button.png`
  - `4b Wireframe - Logged out.png`
  - `4c Wireframe - Session already ended.png`
  - `4d Wireframe - Protected page blocked.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us40_platformManagerLogout.py -v
```
