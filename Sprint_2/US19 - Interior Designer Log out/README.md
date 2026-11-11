# US19 — Interior designer log out

> As an interior designer, I want to log out so that other people cannot use my account.

## Behaviour

- Every designer page has a "Log out" button in the header (POST `/designer/logout`). GET on that address is not allowed (HTTP 405) and doesn't log anyone out.
- Clicking it calls `logout()`: the controller notes whether a designer was logged in (`loggedOut = "userId" in session`), clears the whole session once (`session.clear()`) and returns `loggedOut`. It does not call US2's `LogoutController`.
- `loggedOut == True` → `displayLoginPage("You have logged out successfully")` → HTTP 302 to `/designer/login` (wireframe 4b).
- `loggedOut == False` (the session had already ended) → `displayLoginPage("Your session has already ended")` → HTTP 302 to `/designer/login` (wireframe 4c). No error page.
- The message is shown once (flash). After logging out, every designer page sends the user to `/designer/login` (`designerLoginRequired`), and create/update/delete requests change nothing.
- A designer can always log out, even if their account or profile was suspended after logging in. Only this browser's session ends. The company profile and the account are not changed. The User Admin's log out (US2, `/logout`) is separate and unchanged.

## Who checks what

- **Boundary** (`InteriorDesignerLogoutPage`): picks the message from the controller's result and redirects to the designer login page.
- **Control** (`InteriorDesignerLogoutController`): ends the session itself and returns whether a session was ended. There is no input to check.
- **Entity**: none - log out doesn't read or change any saved data.
- Precondition: none is enforced - `/designer/logout` has no decorator, so clicking it with no session just shows "Your session has already ended".

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `InteriorDesignerLogoutPage` — attribute `interiorDesignerLogoutController`; `clickLogout()`, `displayLoginPage(msg)` | `boundary/interiorDesignerLogoutPage.py`, Log out button in `templates/interiorDesignerBase.html`, message on `templates/login.html` (shared login page) |
| Control `InteriorDesignerLogoutController` — `logout(): bool` | `control/interiorDesignerLogoutController.py` |
| Route | POST `/designer/logout` → `interiorDesignerLogout()` in `app.py` |

Messages: `MSG_LOGGED_OUT` "You have logged out successfully", `MSG_SESSION_ENDED` "Your session has already ended".

## Files

- `US19 Interior designer log out.drawio` — every diagram, one page each
- `US19 Interior designer log out.docx` — user story, use case description, diagrams, wireframes and test cases
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
python -m pytest tests/test_us19_interiorDesignerLogout.py -v
```
