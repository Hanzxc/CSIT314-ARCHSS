# US36 — Customer log out

> As a customer, I want to log out so that other people cannot use my account.

## Try it

Run the existing seed/startup commands and sign in at `/customer/login` as
`cust001 / Cust@123`. Select **Log out** in the customer header. The browser
returns to customer login with `You have logged out successfully`. Opening the
dashboard, search or an IDP detail link then redirects to customer login.

## Behaviour and scope

- The shared customer header submits POST `/customer/logout` from dashboard,
  search, detail and unavailable-IDP pages. Other methods return HTTP 405.
- `CustomerLogoutPage` delegates to `CustomerLogoutController`, which reuses
  US2's `LogoutController` and always clears the entire session, including
  orphaned identity values, prior feedback and transient action data.
- The boundary flashes one success message if userId was present, or
  `Your session has already ended` as information otherwise, then redirects to
  `/customer/login`. The login GET consumes that message. No authentication
  identity remains; once feedback is consumed, an empty session cookie expires.
- Logout needs no account/profile lookup and is not guarded by customer access.
  It still works after account/profile suspension, permission revocation or
  account deletion. Submitted identity fields and return URLs are ignored.
- Existing `Cache-Control: no-store` headers apply to logout, login and protected
  responses. US30/US31/US32 check authentication again on later requests.
- This follows the existing Flask signed-cookie design and ends the **current
  browser session only**. Other browsers/devices and previously copied cookies
  are not globally revoked. No server-side session registry is introduced.
- No Entity or schema change is needed. Logout changes no account, company,
  project, saved-project or statistics records. Existing admin/designer logout
  routes remain available.

## Implementation

- `control/customerLogoutController.py`: shared logout plus unconditional cleanup.
- `boundary/customerLogoutPage.py`: feedback and fixed customer-login redirect.
- `templates/customerBase.html`: dedicated customer POST logout action.
- `templates/customerLogin.html`: shared success/info flash rendering.
- `app.py`: POST `/customer/logout`.
- `tests/test_us36_customerLogout.py`: 30 numbered cases, 38 automated checks.

## Documentation and images

`US36 Customer log out.docx` follows the retained US13 sample and includes the
story, acceptance criteria, use case description, class/use-case/combined-sequence
diagrams, four wireframes, manual scenarios and verified unit results. Manual
Actual result and Pass / Fail cells remain blank for execution.

`US36 Customer log out.drawio` contains all seven editable pages. Separate PNGs:

- `diagrams/2 Use Case Diagram.png`
- `diagrams/5 BCE Class Diagram.png` — Boundary/Control/framework; no Entity needed
- `diagrams/6 Sequence Diagram.png` — one combined sequence
- `diagrams/4a Wireframe - Customer logout action.png`
- `diagrams/4b Wireframe - Logout successful.png`
- `diagrams/4c Wireframe - Session already ended.png`
- `diagrams/4d Wireframe - Protected page after logout.png`

## Validation

US36: **38 passed**. Full regression suite: **909 passed**. Isolated tests cover
session cleanup, feedback, repeated/anonymous logout, access revocation, protected
requests, browser scope, cookie expiry, no writes and existing logout routes.
