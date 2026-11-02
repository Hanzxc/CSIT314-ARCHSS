# US30 — Customer log in

> As a customer, I want to log in so that I can view and manage my saved IDPs.

## Try it

Run `python -m database.seedData`, then `python app.py`. Open
`http://127.0.0.1:5000/customer/login` and use `cust001 / Cust@123`.
Successful login opens `/customer/dashboard`. The shared `/login` and legacy
`/dashboard` also route authorised customers to their dashboard, after the
existing designer and platform-manager role checks.

## Scope and rules

- Reuses `UserAccount.verifyCredentials()` and `UserProfile`; no schema change.
- Requires an Active account, an Active profile, and the existing
  `Search, view and save IDPs` permission. Profile names and IDs are not hardcoded.
- Empty/whitespace-only username or empty password shows the required-field error.
- Verification preserves the existing exact, case-sensitive credentials;
  username/password are not trimmed, and password whitespace is preserved.
- Unknown user, wrong password, suspended account/profile and missing customer
  permission all show `Invalid login details or access unavailable`.
- Success clears the old session and stores only userId, profileId and username.
  Failure creates no new customer session and leaves an existing session unchanged.
- Every dashboard request reloads the account/profile from the database. Missing
  session redirects to customer login; revoked or non-customer access returns 403.
- The dashboard follows the templates' header, sidebar and cards. Saved-IDP
  viewing/management are labelled as later features; this login story adds no
  saved-project storage, list or removal operation. Log out reuses existing US2.
- Passwords/hashes are never stored in the session or rendered in the dashboard.
  Existing shared password storage is reused without migration.

## Files

- `boundary/customerLoginPage.py`: form, validation, session and dashboard boundary.
- `control/customerLoginController.py`: authentication and customer access checks.
- `templates/customerLogin.html`, `customerBase.html`, `customerDashboard.html`,
  `customerAccessDenied.html`: shared-CSS customer screens.
- `app.py`, `boundary/loginPage.py`: customer routes and shared role routing.
- `tests/test_us30_customerLogin.py`: 30 numbered cases, 60 automated checks.

## Documentation and images

`US30 Customer log in.docx` follows the retained US13 document sample. It contains
the story, acceptance criteria, use case description, three diagrams, four
wireframes, manual test cases and verified unit-test results.

`US30 Customer log in.drawio` contains all seven editable pages. Separate PNGs:

- `diagrams/2 Use Case Diagram.png`
- `diagrams/5 BCE Class Diagram.png`
- `diagrams/6 Sequence Diagram.png` — one combined sequence
- `diagrams/4a Wireframe - Customer login.png`
- `diagrams/4b Wireframe - Customer dashboard.png`
- `diagrams/4c Wireframe - Invalid login.png`
- `diagrams/4d Wireframe - Missing fields.png`

## Validation

US30: **60 passed**. Full regression suite: **756 passed**. Test databases are
isolated from the demo database. Coverage includes invalid credentials, role
checks, revocation, session replacement, routing, escaping and no database writes.
Manual system-test outcomes in the Word document remain blank for execution.
