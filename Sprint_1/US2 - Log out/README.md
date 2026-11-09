# US2 — Log out

> As a user admin, I want to log out so that other people cannot use my account.

## Behaviour

- Every admin page has a "Log out" button in the header (POST `/logout`).
- Clicking it calls `logout()`: the controller notes whether someone was logged in (`loggedOut = "userId" in session`), clears the session and returns `loggedOut`.
- `loggedOut == True` → the login page with "You have logged out successfully" (wireframe 4b).
- `loggedOut == False` (the session had already ended, e.g. timed out) → the login page with "Your session has already ended" (wireframe 4c). No error page.
- After logging out, the Back button or an admin link only leads to the login page: `loginRequired` sends anyone with no session to `/login`.
- There is no "Are you sure?" box - logging out can't lose any data.

## Who checks what

- **Boundary** (`LogoutPage`): picks the message from the controller's result and shows the login page.
- **Control** (`LogoutController`): ends the session and returns whether a session was ended. There is no input to check.
- **Entity**: none - log out doesn't read or change any saved data.
- Precondition: none is enforced - `/logout` has no decorator, so clicking it with no session just shows "Your session has already ended".

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `LogoutPage` — `clickLogout()`, `displayLoginPage(msg)` | `boundary/logoutPage.py`, `templates/login.html`, Log out button in `templates/base.html` |
| Control `LogoutController` — `logout(): boolean` | `control/logoutController.py` |
| Route | POST `/logout` → `logout()` in `app.py` |

Messages: `MSG_LOGGED_OUT` "You have logged out successfully", `MSG_SESSION_ENDED` "Your session has already ended".

## Files

- `US2 Log out.drawio` — every diagram, one page each
- `US2 Log out.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Log out button.png`
  - `4b Wireframe - Logged out.png`
  - `4c Wireframe - Session already ended.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us2_logout.py -v
```
