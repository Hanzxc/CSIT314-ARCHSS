# US40 — Platform manager log out

> As a platform manager, I want to log out so that other people cannot use my account.

## Behaviour

- Every Platform Manager page has a "Log out" button in the header (the dashboard and the IDP category pages). It sends a POST to /manager/logout. Opening /manager/logout with GET is not allowed and doesn't log anyone out.
- PlatformManagerLogoutController reuses the US2 LogoutController.logout(), then clears anything left in the session - the same way US19 does it for designers.
- No entity class is needed. Logging out only ends the browser session - it doesn't change the user account or any IDP category.
- After logging out the manager goes to the manager login page with "You have logged out successfully". If the session had already ended, the message is "Your session has already ended". The message is shown once only.
- A manager can always log out, even if their account or profile was suspended after they logged in.
- Logging out only ends the session in this browser, not on other devices.
- The User Admin's log out (US2, /logout) and the designer's log out (US19, /designer/logout) are not changed.

## Repository files

New files for this story:

```text
boundary/platformManagerLogoutPage.py
control/platformManagerLogoutController.py
templates/platformManagerBase.html
tests/test_us40_platformManagerLogout.py
Sprint_3/US40 - Platform Manager Log out/...
```

Existing files with small additions (shared by US20 and US40 - US45; nothing removed):

- `app.py` — imports and routes for US20 and US40 - US45 added (no existing route changed)
- `database/schema.sql` — `idp_category` and `idp` tables appended (existing tables unchanged; `initDatabase()` creates them in an existing `archss.db`, no migration needed)
- `templates/platformManagerDashboard.html` — Log out button (US40) and IDP Categories links (US45)
- `templates/interiorDesignerDashboard.html` — "Add current IDP" button on the Current IDPs card (US20)

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `PlatformManagerLogoutPage` | `boundary/platformManagerLogoutPage.py` |
| Control `PlatformManagerLogoutController` | `control/platformManagerLogoutController.py` |
| Reused control `LogoutController` | Existing US2 `control/logoutController.py` |
| Header Log out button | `templates/platformManagerBase.html`, `templates/platformManagerDashboard.html` |
| Route | POST `/manager/logout` in `app.py` |

Class, method, attribute and variable names in the diagrams are the same as in the code.

```text
US40 Platform manager log out.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Logout button.png
  4b Wireframe - Logged out.png
  4c Wireframe - Session already ended.png
  4d Wireframe - Protected page blocked.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains 7 editable pages. PNGs are locally rendered vector illustrations of the same pages, not browser screenshots.

## Automated pass/fail tests

Open a terminal at the repository root:

```powershell
python -m pytest tests/test_us40_platformManagerLogout.py -v
python -m pytest -q
```
