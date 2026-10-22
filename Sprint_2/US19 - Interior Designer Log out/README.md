# US19 — Interior designer log out

> As an interior designer, I want to log out so that other people cannot use my account.

Apply this repository update **after US13–18**. It follows the same simple Python test/helper format, camelCase naming, three UML diagram types, one editable draw.io file and numbered PNG wireframes with Notes panels. Sample company/account names and branding remain unchanged. Only repository files are packaged, not a complete project.

## Behaviour

The shared designer header now contains a **Log out** button on the dashboard and company pages. It submits POST `/designer/logout`. GET on that address is not allowed and does not log out the user.

The new designer logout control reuses the existing US2 `LogoutController.logout()`, then clears any remaining session data. This removes authentication fields and pending company-delete confirmation data, including orphaned data if the authentication session already ended. The boundary adds a one-time success/info message and redirects to `/designer/login`:

- Existing login session: `You have logged out successfully`.
- No login session: `Your session has already ended`.

The existing designer login template displays and consumes the flashed message. Login fields are blank, and the user can sign in again. A follow-up request to any protected designer URL redirects to login. Company creation/update/deletion requests after logout cannot change data; old delete-confirmation values also fail after signing in again.

Logout retains the company profile, designer account and account status. It ends this browser's session, not sessions on all other devices/browsers; global session revocation is not implemented. It is allowed even if the account/profile was suspended after login, because a user must still be able to end their session. The existing admin `/logout`, `LogoutPage` and `LogoutController` are unchanged.

The application already returns `Cache-Control: no-store`; the tests verify those headers and protected HTTP requests after logout. They do not claim a visual test of every browser's Back/history behaviour. Flask session is infrastructure; no company/account entity or database write is needed for logout.

## Repository files

Add these new files to the existing matching folders:

```text
boundary/interiorDesignerLogoutPage.py
control/interiorDesignerLogoutController.py
tests/test_us19_interiorDesignerLogout.py
Sprint_2/US19 - Interior Designer Log out/...
```

Combine these modified files with the group's latest versions:

```text
app.py
templates/interiorDesignerBase.html
templates/interiorDesignerLogin.html
tests/test_us15_viewCompanyProfile.py
```

The US15 test change is intentional: `test_ut15_20_viewPage_isReadOnly` now checks the **main company content** for editable fields/submit buttons, rather than checking the entire response. The header now has a valid Log out submit button; the company view remains read-only. Its other checks (Back link and disallowed POST to the view route) remain intact. No US15 test was removed. The new US19 tests also check that the header has logout while company content remains read-only.

All files in the archive are needed, alongside the test and Sprint_2 folder. Paths are relative to your repository root. Add new files alongside existing ones; preserve newer group changes when combining modified versions. US13/14/16/17/18 tests and the database schema are unchanged. No migration is needed. No Git commit, push or merge has been performed.

## Diagram/code mapping

| Element | Implementation |
|---|---|
| Boundary `InteriorDesignerLogoutPage` | `boundary/interiorDesignerLogoutPage.py` |
| Control `InteriorDesignerLogoutController` | `control/interiorDesignerLogoutController.py` |
| Reused control `LogoutController` | Existing US2 `control/logoutController.py` |
| Shared header button | `templates/interiorDesignerBase.html` |
| Login result messages | `templates/interiorDesignerLogin.html` |
| Route | POST `/designer/logout` in `app.py` |

The BCE diagram intentionally has **no business Entity class**, because logout only changes session state. It retains the Boundary/Control/Entity column format and explains this in the Entity column. Flask session is correctly shown as framework infrastructure in the sequence diagram, not as a fake database entity. The single sequence diagram shows reuse of US2 logout, clearing session data, selecting success/already-ended messages and redirecting to designer login. The existing US13 login handler supplies the follow-up GET/login form.

```text
US19 Interior designer log out.drawio
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Logout button.png
  4b Wireframe - Logged out.png
  4c Wireframe - Session already ended.png
  4d Wireframe - Protected page blocked.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The draw.io file contains seven editable pages. PNGs are locally rendered vector illustrations checked visually, not browser screenshots. Written use case descriptions, Word reports and written test case tables remain deferred.

## Automated pass/fail tests

Open a terminal at your group's **repository root**, after combining all files:

```powershell
python -m pytest tests/test_us19_interiorDesignerLogout.py -v --basetemp=.test-tmp-us19
python -m pytest -q --basetemp=.test-tmp-all
```

If `python` is not recognised on the computer used for these packages:

```powershell
$us19Python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
& $us19Python -m pytest tests/test_us19_interiorDesignerLogout.py -v --basetemp=.test-tmp-us19
& $us19Python -m pytest -q --basetemp=.test-tmp-all
```

**Verified: 26 US19 tests passed; 356 tests passed overall.** Tests cover control results, full session clearing, stale anonymous data, shared header buttons, redirect/messages, repeated logout, POST-only routing, protected GETs/writes after logout, invalidated delete confirmation, retained account/company data, re-login, suspension, separate browser sessions, no-store headers, one-time messages and unchanged admin logout.

The existing `conftest.py` supplies a fresh isolated database for each test; helpers add the fictional account and company. No server or manual input is needed, and tests do not change the demo database. Keep `--basetemp` folders for disposable test data only; pytest recreates them. The first run failed because the new controller did not exist; the final runs passed. This records this development session, not prior group work.

## Try the website

Start the same application from the repository root:

```powershell
python app.py
```

Use the explicit executable above if needed. Leave the terminal running and open `http://127.0.0.1:5000/login`.

1. Log in with your existing fictional designer account, such as `designer13` / `Design@123` if set up in US13/14.
2. On the dashboard or a company page, select **Log out** in the header.
3. Check that designer login opens with `You have logged out successfully`.
4. Enter `http://127.0.0.1:5000/designer/dashboard` or `/designer/company` again: the application redirects to login instead of returning company information.
5. Sign in again. The account and any saved company profile are still available.

Normal logout is done using the button, not by typing `/designer/logout` into the address bar, because the route requires POST. Stop the server with Ctrl+C when finished. All stories/roles still run through the same server; fresh account/database setup remains as described for US13/14.

This completes the implementation deliverables for the assigned designer stories US13–19. US39 remains the separate platform-manager login story; written descriptions/test case tables are still pending.
