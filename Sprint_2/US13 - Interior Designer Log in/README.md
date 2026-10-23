# US13 — Interior designer log in

> As an interior designer, I want to log in so that I can manage my company’s information and IDPs.

US13 is the first Sprint 2 story. It adds a separate login page and dashboard for interior designers. All the company profile stories (US14–US18) and designer log out (US19) build on it. The full write-up (user story, use case description, diagrams, wireframes and test cases) is in `US13 Interior designer log in.docx`.

## Behaviour

Designers log in at `/designer/login` with the username and password their User Admin created (US8). The login only works when:

- the username and password are correct,
- the account is **Active**,
- its user profile is **Active**, and
- the profile has **both** the `Manage company profile` and `Manage own IDPs` permissions.

The check uses the permissions, not the profile name. A custom profile with those two permissions can also log in as a designer.

Messages:

- Empty username or password: `Please enter your username and password`
- Any other failure (wrong password, unknown user, suspended account/profile, not a designer): `Invalid login details or access unavailable`. It's the same message every time, so the page doesn't reveal which part was wrong.

A successful login clears the old session and saves only `userId`, `profileId` and `username`. The password is never put in the session. The designer then goes to `/designer/dashboard`, which shows "Welcome back, <username>" and the Company Profile, Current IDPs and Past IDPs cards. Current/Past IDPs are placeholders for later stories.

The dashboard checks the account and profile again every time it is opened. With no session it redirects to `/designer/login`. If the account or profile was suspended (or the permissions removed) after login, it shows "Access unavailable" (HTTP 403).

`InteriorDesignerLoginController.getAuthenticatedDesigner(userId)` is the access check that every designer page in US14–US18 reuses.

### Changes to Sprint 1 code

- The shared `/login` (US1, `LoginPage.redirectToDashboard()`) now sends designers to the designer dashboard and managers (US39) to the manager dashboard. It also clears the old session before saving the new one.
- `loginRequired` in `app.py` now rechecks the account and profile from the database. User Admin pages need **both** `Manage user accounts` and `Manage user profiles`. Anyone else gets HTTP 403, and designers/managers opening `/dashboard` are redirected to their own dashboard.

No new table is needed — `UserAccount` and `UserProfile` are reused unchanged.

## Files

| Design element | Code |
|---|---|
| Boundary `InteriorDesignerLoginPage` | `boundary/interiorDesignerLoginPage.py` (login page + `openDashboard()`) |
| Control `InteriorDesignerLoginController` | `control/interiorDesignerLoginController.py` |
| Entity `UserAccount`, `UserProfile` | existing `entity/userAccount.py`, `entity/userProfile.py` |
| Login page | `templates/interiorDesignerLogin.html` |
| Dashboard | `templates/interiorDesignerDashboard.html` (extends `interiorDesignerBase.html`) |
| Access refused | `templates/interiorDesignerAccessDenied.html` |
| Routes | GET/POST `/designer/login`, GET `/designer/dashboard` in `app.py` |
| Tests | `tests/test_us13_interiorDesignerLogin.py` (UT13.1 – UT13.24) |

## Diagram folder

```text
US13 Interior designer log in.docx      write-up
US13 Interior designer log in.drawio    all diagrams, one page each (7 pages)
diagrams/
  2 Use Case Diagram.png
  4a Wireframe - Log in form.png
  4b Wireframe - Missing required fields.png
  4c Wireframe - Invalid login.png
  4d Wireframe - Designer dashboard.png
  5 BCE Class Diagram.png
  6 Sequence Diagram.png
```

The BCE and sequence diagrams use the same class and method names as the code.

## Run the tests

From the repository root:

```powershell
python -m pytest tests/test_us13_interiorDesignerLogin.py -v
python -m pytest -q
```

24 US13 tests pass, and the whole suite passes (386 tests as of 23 October 2026). `conftest.py` gives every test its own fresh database, and the tests create the designer `designer13` / `Design@123` (Tengku Uda Designer) themselves, so you don't need to set anything up.

## Try it in the browser

```powershell
python -m database.seedData     # only needed once
python app.py
```

Open http://127.0.0.1:5000/designer/login and log in with any active sample designer, e.g. `design006` / `Pass@123`. Or log in as `admin01` / `Admin@123`, create an account in the **Interior Designer** profile (US8), and use that. The shared http://127.0.0.1:5000/login also works for designers.
