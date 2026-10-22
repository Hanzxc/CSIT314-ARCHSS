# US39 - Platform Manager Log in

As a platform manager, I want to log in so that I can manage IDP categories and reports.

## Merge into the existing repository
Apply after US13-19. This ZIP contains only new/changed source files and this Sprint_2 story folder. Keep all other existing repository files. Merge app.py and boundary/loginPage.py with any newer changes from teammates; copying files does not automatically merge Git branches. No database schema or entity changes are required. Existing US1-19 tests and fixtures are unchanged.

New files: boundary/platformManagerLoginPage.py, control/platformManagerLoginController.py, templates/platformManagerLogin.html, templates/platformManagerDashboard.html, templates/platformManagerAccessDenied.html, tests/test_us39_platformManagerLogin.py.
Changed files: app.py and boundary/loginPage.py.

## Behaviour and BCE mapping
Boundary PlatformManagerLoginPage validates required fields, displays messages and creates the session. Control PlatformManagerLoginController calls the existing UserAccount.verifyCredentials(), checks account.isActive(), loads UserProfile.getUserProfile(), and checks profile.isActive() plus both existing permissions: Manage IDP categories and Generate reports. Access is based on permissions rather than a fixed profile name or ID. Dashboard access reloads the account/profile on every request. Failed login creates no new authenticated session; an already authenticated session is retained on failed attempts, as with the existing designer login.

Successful login clears the old session and stores only userId, profileId and username. No password is stored in the session. /manager/login accepts GET and POST; /manager/dashboard accepts GET. The shared /login and /dashboard also route eligible managers to the manager dashboard. Existing designer routing takes precedence for a custom profile with both designer and manager permissions; the dedicated manager login always selects the manager dashboard. Existing permission guards continue to protect admin/designer areas.

IDP Categories and Reports are visual placeholders for later stories, not working management actions. Platform manager logout is US40 and is outside this package. US39 reuses the same account database as the admin and designer stories; it is not a separate application.

## Run the tests
In VS Code's terminal, from the group's repository root with the usual Python environment activated:

```powershell
python -m pytest tests/test_us39_platformManagerLogin.py -v
python -m pytest tests -q
```

Expected results on the supplied integrated US19 baseline: 30 US39 tests pass, 386 tests pass overall. Tests automatically create a fresh temporary database through the existing conftest.py; do not enter credentials manually into pytest. The code uses plain test functions/helpers in the US11/12 format, including controller/entity checks and Flask test-client page checks. Flask test-client tests exercise website routes without opening a real browser.

## Open the website
Start the existing application from the repository root:

```powershell
python app.py
```

Open http://127.0.0.1:5000/manager/login (or the shared /login). The test-only account is not automatically inserted into the normal website database. Using the existing User Admin account creation page, create an Active account with the Active Platform Manager profile and both manager permissions. Suggested fictional data: username manager39, password Manager@123, full name Daniel Tan, email manager39@archss.com. Use that username/password on the manager login page. A wrong password shows the generic error; missing fields show the required-fields message. Successful login shows the manager dashboard. Any other existing eligible manager account works too.

## Diagrams and wireframes
The diagrams folder contains the use case diagram, BCE class diagram, one sequence diagram including success/failure branches, and four labelled wireframes (form, missing input, failed login, successful dashboard). The seven-page draw.io file contains editable versions of all of them. These use the US13 layout and the existing website colours. The sequence and BCE names match the implemented methods; entity classes are reused. Wireframes are annotated design exports, not browser screenshots. Actual templates were also exercised through Flask's test client. Written use case descriptions and written test case tables remain deferred as requested.
