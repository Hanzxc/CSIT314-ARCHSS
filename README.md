# CSIT314-ARCHSS

Interior Design Platform - CSIT314 group project.
Sprint 1 covers the User Admin's user stories **US1 - US12** (log in, log out, create / view / update / suspend / search user profiles and user accounts).
Sprint 2 covers the Interior Designer's stories **US13 - US19** (log in, create / view / update / delete / search company profile, log out) and the Platform Manager's **US39** (log in).
The design docs (one .docx write-up per story) and diagrams for each story are in [Sprint_1/](Sprint_1/) and [Sprint_2/](Sprint_2/).

## Integration with the November 6 main branch

The current-project and customer stories are combined with the newer add/past-IDP,
category and saved-list features. The shared IDP model retains both sets of
methods. The designer dashboard offers both Add and View current IDPs.

`idpDetailContent.html` is the reusable content partial for designer previews and
customer details; `idpDetails.html` retains the upstream public-page template.
The original Word documents and diagram images are preserved as story snapshots.

Saved-list routes now use the same US30 customer session and access checks as
customer search/detail pages. Saved IDPs are accessible from the dashboard/sidebar,
and the detail page shows the appropriate Save/Remove action. The isolated test
setup keeps demo categories separate from story fixtures; past-project tests use
the current login flow and routes.

## US30 Customer log in

Customers can log in at `/customer/login` with `cust001 / Cust@123` after seeding.
The shared `/login` also directs authorised customers to `/customer/dashboard`.
Access requires an Active account/profile and the existing customer permission;
the dashboard rechecks these on every request. Successful login replaces the old
session without storing credentials. Saved-IDP viewing and management are later
features, clearly labelled on the dashboard. Existing US2 logout is reused.

The Word document, three diagrams, four wireframe PNGs and editable drawio file
are in `Sprint_3/US30 - Customer Log In/`. US30 has **60 passing checks**;
the complete suite has **756 passing tests**.

## US31 Customer search for IDPs

After customer login, select **Search IDPs** from the dashboard or sidebar.
GET `/customer/idps/search?keyword=...` searches title, description, location and
category with literal case-insensitive matching. Empty search or Clear browses
all Active IDPs in Active categories, across designers and both Current/Past
project types. Result cards show design summaries; detail viewing and saving are
later stories. Search rechecks US30 access and changes no records or statistics.

The Word document, three diagrams, four wireframe PNGs and editable drawio file
are in `Sprint_3/US31 - Search IDPs/`. US31 has **57 passing checks**;
the complete suite has **813 passing tests**.

## US32 Customer view of an IDP

Select **View** on a customer search result to open `/customer/idps/<idpId>`.
The page shows full project details and the designer's Active company name,
description and services when available. Missing company information uses a
fallback message. Project/category visibility follows US31, and customer access
is checked through US30. **Back to search** retains the keyword. Viewing is read-only.

The Word document, three diagrams, four wireframe PNGs and editable drawio file
are in `Sprint_3/US32 - View IDP/`. US32 has **58 passing checks**;
the complete suite has **871 passing tests**.

## US36 Customer log out

The customer header now submits POST `/customer/logout`, clears the current
browser session and returns to `/customer/login` with one-time success or
already-ended feedback. It works even after access is revoked. Later dashboard,
search and detail requests require login again. This follows the existing
current-browser signed-cookie session design; it does not add global revocation
of other browsers or copied cookies. Persistent records remain unchanged.

The Word document, three diagrams, four wireframe PNGs and editable drawio file
are in `Sprint_3/US36 - Customer Log Out/`. US36 has **38 passing checks**;
the complete suite has **909 passing tests**.

## Tech we're using

| What | Tool | Why |
|---|---|---|
| Language | **Python 3.11+** | easy for everyone to read and write |
| Web pages | **Flask** | simplest way to turn our wireframes into web pages - each Boundary class is a page |
| Database | **SQLite** | built into Python, nothing to install, works on GitHub Actions too |
| Unit tests | **pytest** | for TDD - write the test first, then the code |
| CI/CD | **GitHub Actions** | runs the tests on every push (to set up) |

## Setup

```
pip install -r requirements.txt
python -m database.seedData          # creates the database + 100 profiles / 100 accounts of test data
python -m database.seedCompanyData   # optional: 100 demo designers (companydemo001 ... / Demo@123), each with a company profile
python app.py          # starts the site at http://127.0.0.1:5000
pytest                 # runs all the unit tests
```

## US21 View current IDPs

The designer dashboard and sidebar link to `/designer/idps/current`. Selecting View opens
`/designer/idps/current/<idpId>`, using a reusable customer-facing `idpDetailContent.html` partial.
Both pages recheck US13 designer access and only retrieve the session owner's Active Current
IDPs in Active categories. Missing/unavailable details return 404; no projects is a normal
empty state. Viewing does not write data or increase customer view statistics.

US21 includes the prerequisite `idp` and `idp_category` table definitions and IDP attributes
from the US20 feature branch; it does not merge that branch or implement US20's add form.
Startup adds missing tables while preserving existing records. The eventual US32 customer
page can reuse the detail partial; that customer route is not implemented by US21.

For optional demo projects, run `python -m database.seedData` then
`python -m database.seedCurrentIDPData`. Sign in at `/designer/login` with
`idpdemo001 / Demo@123` (or `idpdemo002 / Demo@123`). Each owns two current projects.
Re-running the demo seed does not duplicate records or reactivate suspended records.

Run `python -m pytest tests/test_us21_viewCurrentIDPs.py -q` for the story's tests.
The Word document, editable diagrams and wireframes are in `Sprint_3/US21 - View Current IDPs/`.

## US22 Update current IDP

Open an own project from Current IDPs, select **Update current IDP**, edit its prefilled
title, category, description/progress and optional location, then **Save changes**.
The saved US21 preview shows the updated content; **Cancel** returns without saving.
Wireframes and the update page follow the existing designer templates and shared CSS.

GET/POST `/designer/idps/current/<idpId>/update` rechecks designer access and ownership.
Only Active Current IDPs in Active source categories can be edited, and the selected
destination category must be Active at save time. Posted owner/type/status/date fields
are ignored. Invalid fields preserve input; submissions require the hidden user/project
form token. US22 adds no new database columns and works with the US21 demo projects.

Documentation, use case/BCE/combined sequence diagrams and four wireframes are in
`Sprint_3/US22 - Update Current IDP/`. Run `python -m pytest tests/test_us22_updateCurrentIDP.py -q`.
Verified suite: 569 tests passed, including 86 US22 checks and all 483 previous tests.

## US23 Delete current IDP

Open an own Current IDP preview and choose **Delete current IDP**. The existing-style
confirmation dialog offers Delete and Cancel. Confirmed deletion sets the project to
Suspended, preserving its record while hiding it from the current list, preview and
update pages. Cancel leaves the project unchanged. No restore workflow is added.

GET/POST `/designer/idps/current/<idpId>/delete` rechecks designer access, session ownership
and visibility. Delete requires an explicit choice and a matching confirmation token.
The guarded write also checks a compact fingerprint of the reviewed content; changes
made after confirmation require a fresh review. Other projects and related data are retained.

Documentation, three diagrams and four template-matching wireframes are in
`Sprint_3/US23 - Delete Current IDP/`. Run `python -m pytest tests/test_us23_deleteCurrentIDP.py -q`.
Verified suite: 641 tests passed, including 72 US23 checks and all 569 previous tests.

## US24 Search current IDPs

From **Current IDPs**, select **Search current IDPs**. The GET search at
`/designer/idps/current/search?keyword=...` matches title, description/progress, location
or category using case-insensitive literal substring matching. Empty searches and
**Clear** show all visible own projects; results use the same cards as US21, newest first.
**View** opens the existing preview and its management actions.

Search always checks designer access and session ownership and excludes Past, Suspended,
deleted and hidden-category projects. No-match and empty states are normal pages. Search
does not write to the database. No migration or new dependency is required.

Documentation, three diagrams and four template-matching wireframes are in
`Sprint_3/US24 - Search Current IDPs/`. Run `python -m pytest tests/test_us24_searchCurrentIDPs.py -q`.
Verified suite: 696 tests passed, including 55 US24 checks and all 641 previous tests.

If you already have a `database/archss.db` from Sprint 1 you don't need to delete it - `python app.py` adds the new `company_profile` table on startup.

Log in pages: User Admin `/login`, Interior Designer `/designer/login`, Platform Manager `/manager/login`. The shared `/login` also sends designers and managers to their own dashboard. The sample accounts from `seedData` use the password `Pass@123` (e.g. `design006` is an active designer, `pm005` an active manager).

## Folder layout (B-C-E)

The actor only talks to the **boundary**, the boundary only talks to the **controller**, and the controller works with the **entity** classes. One controller per use case.

**Who checks what** (from the lecturer's feedback):

| Layer | Its job |
|---|---|
| Boundary | checks **all** the input (required fields, lengths, email format, the admin not suspending themselves) and trims spaces before passing anything on |
| Control | just calls the entity and returns the result straight back - no re-checking, no `success` variable |
| Entity | checks for duplicates / the database state (username or profile name taken, profile not Active, company profile already exists, only suspending Active rows), then inserts / updates and commits. No `.strip()` here |

Being logged in as the right role is a **precondition** of each use case, so it isn't checked again inside the B-C-E flow. `app.py` only has small route decorators (`loginRequired` for admin pages, `designerLoginRequired` for US14 - US18) so a page doesn't crash when nobody is logged in.

```
CSIT314-ARCHSS/
├── app.py                      Flask app - links each URL to its boundary class
├── requirements.txt            flask, pytest
├── pytest.ini                  lets the tests import our folders
├── boundary/                   pages (what the user sees)
│   ├── loginPage.py                    US1
│   ├── logoutPage.py                   US2
│   ├── createUserProfilePage.py        US3
│   ├── viewUserProfilePage.py          US4
│   ├── updateUserProfilePage.py        US5
│   ├── suspendUserProfilePage.py       US6
│   ├── searchUserProfilePage.py        US7
│   ├── createUserAccountPage.py        US8
│   ├── viewUserAccountPage.py          US9
│   ├── updateUserAccountPage.py        US10
│   ├── suspendUserAccountPage.py       US11
│   ├── searchUserAccountPage.py        US12
│   ├── interiorDesignerLoginPage.py    US13 (also the designer dashboard)
│   ├── createCompanyProfilePage.py     US14
│   ├── viewCompanyProfilePage.py       US15
│   ├── updateCompanyProfilePage.py     US16
│   ├── deleteCompanyProfilePage.py     US17
│   ├── restoreCompanyProfilePage.py    US17 (restore)
│   ├── searchCompanyInformationPage.py US18
│   ├── interiorDesignerLogoutPage.py   US19
│   └── platformManagerLoginPage.py     US39 (also the manager dashboard)
├── control/                    one controller per use case (just calls the entity)
│   ├── loginController.py              US1
│   ├── logoutController.py             US2
│   ├── createUserProfileController.py  US3
│   ├── viewUserProfileController.py    US4
│   ├── updateUserProfileController.py  US5
│   ├── suspendUserProfileController.py US6
│   ├── searchUserProfileController.py  US7
│   ├── createUserAccountController.py  US8
│   ├── viewUserAccountController.py    US9
│   ├── updateUserAccountController.py  US10
│   ├── suspendUserAccountController.py US11
│   ├── searchUserAccountController.py  US12
│   ├── interiorDesignerLoginController.py    US13
│   ├── createCompanyProfileController.py     US14
│   ├── viewCompanyProfileController.py       US15
│   ├── updateCompanyProfileController.py     US16
│   ├── deleteCompanyProfileController.py     US17
│   ├── restoreCompanyProfileController.py    US17 (restore)
│   ├── searchCompanyInformationController.py US18
│   ├── interiorDesignerLogoutController.py   US19
│   └── platformManagerLoginController.py     US39
├── entity/                     reads and writes the database
│   ├── userAccount.py
│   ├── userProfile.py
│   └── companyProfile.py       US14 - US18
├── database/
│   ├── schema.sql              user_profile + user_account + company_profile tables
│   ├── db.py                   getConnection(), initDatabase()
│   ├── seedData.py             default + sample profiles and accounts
│   └── seedCompanyData.py      100 demo designers with company profiles
├── templates/                  HTML pages, from the wireframes (base.html = admin header + menu, interiorDesignerBase.html = designer header + menu)
├── static/                     style.css shared by every page
├── tests/                      one test file per user story (UT cases from the docs)
├── Sprint_1/                   US1-US12 docs + diagrams
└── Sprint_2/                   US13-US19 + US39 docs + diagrams (draw.io)
```

## Naming rules

**Use the names exactly as they are in our class diagrams.** Don't rename anything, so the code matches the design.

| Thing | Style | Example |
|---|---|---|
| Files | camelCase, same as the class | `loginController.py` |
| Classes | PascalCase | `LoginController` |
| Functions / methods | camelCase | `verifyCredentials()` |
| Variables / attributes | camelCase | `profileId`, `fullName` |
| Message constants | UPPER_SNAKE_CASE | `MSG_INVALID_LOGIN` |
| Database tables | snake_case | `user_account`, `user_profile` |
| Database columns | camelCase, same as the attribute | `profileName` |
| Test files / functions | `test_us<N>_...py` / `test_ut<N>_<M>_...` | `test_ut1_1_verifyCredentials_correct` |

Controllers inside a page are always called `self.<controllerName>` e.g. `self.loginController`.

## Classes and functions

### Entity

**UserAccount** - `entity/userAccount.py`

| Attributes | |
|---|---|
| `userId` int, `username` str, `password` str (sha256 hash), `fullName` str, `email` str, `phone` str, `profileId` int, `status` str, `createdDate` str | |

| Method | Returns | Used in |
|---|---|---|
| `verifyCredentials(username, password)` | UserAccount or None | US1 |
| `isActive()` | bool | US1, US11 |
| `getUserAccount(userId)` | UserAccount or None | US9, US10, US11 |
| `isUsernameTaken(username, userId=None)` | bool | US8 (no id), US10 (with id) |
| `createUserAccount(username, password, fullName, email, phone, profileId)` | bool (False if the profile isn't Active or the username is taken) | US8 |
| `updateUserAccount(userId, username, fullName, email, phone, profileId)` | bool (same duplicate checks, its own username is fine) | US10 |
| `suspendUserAccount(userId)` | bool (only an Active account) | US11 |
| `searchUserAccounts(keyword)` | list of UserAccount (empty list if nothing matches) | US12 |
| `hashPassword(password)` (helper, not in a class) | str | US1, US8, test data |

**UserProfile** - `entity/userProfile.py`

| Attributes | |
|---|---|
| `profileId` int, `profileName` str, `description` str, `permissions` list of str, `status` str | |

| Method | Returns | Used in |
|---|---|---|
| `getUserProfile(profileId)` | UserProfile or None | US1, US4, US5, US6, US8, US10 |
| `isActive()` | bool | US1, US6 |
| `getAllPermissions()` | list of str | US3, US5 |
| `isProfileNameTaken(profileName, profileId=None)` | bool | US3 (no id), US5 (with id) |
| `createUserProfile(profileName, description, permissions)` | bool (False if the name is taken) | US3 |
| `updateUserProfile(profileId, profileName, description, permissions)` | bool (False if the name is taken) | US5 |
| `suspendUserProfile(profileId)` | bool (only an Active profile) | US6 |
| `searchUserProfiles(keyword)` | list of UserProfile (empty list if nothing matches) | US7, and the profile drop-down in US8 / US10 |

`ALL_PERMISSIONS` - the 8 fixed permissions: Manage user accounts, Manage user profiles, Manage company profile, Manage own IDPs, View IDP statistics, Search, view and save IDPs, Manage IDP categories, Generate reports.

**CompanyProfile** - `entity/companyProfile.py` (table `company_profile`, one row per designer - `designerId` is UNIQUE)

| Attributes | |
|---|---|
| `companyId` int, `designerId` int (the owner's userId), `companyName` str, `description` str, `services` str, `email` str, `phone` str, `address` str, `createdDate` str, `status` str, `revision` int | |

| Method | Returns | Used in |
|---|---|---|
| `getCompanyProfile(designerId)` | CompanyProfile or None | US14, US15, US16, US17, US18 |
| `createCompanyProfile(companyProfile)` | bool (False if the designer already has a row, Active or Suspended) | US14 |
| `updateCompanyProfile(companyProfile)` | bool (False if there's no Active row - it never inserts) | US16 |
| `suspendCompanyProfile(designerId, companyId, expectedRevision)` | bool (owner, id and revision must match) | US17 |
| `getSuspendedCompanyProfile(designerId)` | CompanyProfile or None | US17 (restore) |
| `restoreCompanyProfile(designerId, companyId, expectedRevision)` | bool | US17 (restore) |
| `searchCompanyInformation(designerId, keyword)` | the CompanyProfile with `matchedFields` (names of the fields whose name or value contains the keyword; empty list = no match), or None if there's no Active profile | US18 |

`companyProfile` is a CompanyProfile object the page builds from the form (owner = `session["userId"]`), not a dict.

**Who can do what** - decided at login by the profile's permissions, not its name:

| Role | Needs these permissions | Checked by |
|---|---|---|
| User Admin | Manage user accounts + Manage user profiles | `loginRequired` in `app.py` |
| Interior Designer | Manage company profile + Manage own IDPs | `InteriorDesignerLoginController` at login only (US13) |
| Platform Manager | Manage IDP categories + Generate reports | `PlatformManagerLoginController` at login only (US39) |

The account and its profile must both be Active to log in - `UserAccount.verifyCredentials(username, password, requiredPermissions)` checks the password, both statuses and the permissions in one go. The dashboards and US14 - US18 don't check the role again (logged in as a designer / manager is their precondition) - `designerLoginRequired` / `managerLoginRequired` only send someone with no session back to the log in page.

### Control

| Class | Method | Returns |
|---|---|---|
| `LoginController` | `login(username, password)` | UserAccount or None |
| `LogoutController` | `logout()` | bool |
| `CreateUserProfileController` | `getAllPermissions()` | list of str |
| | `createUserProfile(profileName, description, permissions)` | bool |
| `ViewUserProfileController` | `getUserProfile(profileId)` | UserProfile or None |
| `UpdateUserProfileController` | `getUserProfile(profileId)` | UserProfile or None |
| | `getAllPermissions()` | list of str |
| | `updateUserProfile(profileId, profileName, description, permissions)` | bool |
| `SuspendUserProfileController` | `suspendUserProfile(profileId)` | bool |
| `SearchUserProfileController` | `searchUserProfiles(keyword)` (US8 / US10 also call it with `""` for the drop-down) | list of UserProfile |
| `CreateUserAccountController` | `createUserAccount(username, password, fullName, email, phone, profileId)` | bool |
| `ViewUserAccountController` | `viewUserAccount(userId)` - also sets `self.profile` to the account's profile | UserAccount or None |
| `UpdateUserAccountController` | `getUserAccount(userId)` | UserAccount or None |
| | `updateUserAccount(userId, username, fullName, email, phone, profileId)` | bool |
| `SuspendUserAccountController` | `suspendUserAccount(userId)` | bool |
| `SearchUserAccountController` | `searchUserAccounts(keyword)` | list of UserAccount |
| `InteriorDesignerLoginController` | `login(username, password)` | UserAccount or None |
| | `isInteriorDesigner(account)` (kept only for US21 - US24 until Sprint 3 is fixed) | bool |
| | `getAuthenticatedDesigner(userId)` (kept only for US21 - US24 until Sprint 3 is fixed) | UserAccount or None |
| `CreateCompanyProfileController` | `createCompanyProfile(companyProfile)` | bool |
| `ViewCompanyProfileController` | `viewCompanyProfile(designerId)` | CompanyProfile or None |
| `UpdateCompanyProfileController` | `getCompanyProfile(designerId)` | CompanyProfile or None |
| | `updateCompanyProfile(companyProfile)` | bool |
| `DeleteCompanyProfileController` | `getCompanyProfile(designerId)` | CompanyProfile or None |
| | `deleteCompanyProfile(designerId, companyId, expectedRevision)` | bool |
| `RestoreCompanyProfileController` | `getSuspendedCompanyProfile(designerId)` | CompanyProfile or None |
| | `restoreCompanyProfile(designerId, companyId, expectedRevision)` | bool |
| `SearchCompanyInformationController` | `searchCompanyInformation(designerId, keyword)` | CompanyProfile (with `matchedFields`) or None |
| `InteriorDesignerLogoutController` | `logout()` (clears the session itself - doesn't use the US2 `LogoutController`) | bool |
| `PlatformManagerLoginController` | `login(username, password)` | UserAccount or None |

### Boundary

| Class | Methods |
|---|---|
| `LoginPage` | `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password)` -> bool, `redirectToDashboard(account)`, `displayErrorMessage(msg)` |
| `LogoutPage` | `clickLogout()`, `displayLoginPage(msg)` |
| `CreateUserProfilePage` | `clickCreateUserProfile()`, `displayCreateForm(permissionList)`, `submitUserProfile(profileName, description, permissions)`, `validateInput(profileName, permissions)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `ViewUserProfilePage` | `selectUserProfile(profileId)`, `displayUserProfile(profile)`, `displayErrorMessage(msg)` |
| `UpdateUserProfilePage` | `clickUpdate(profileId)`, `displayUpdateForm(profile, permissionList)`, `submitUpdate(profileName, description, permissions)`, `validateInput(profileName, permissions)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SuspendUserProfilePage` | `clickSuspend(profileId)`, `displayConfirmation()`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchUserProfilePage` | `searchUserProfiles(keyword)`, `displayResults(profiles)`, `displayNoResultsMessage()` |
| `CreateUserAccountPage` | `clickCreateUserAccount()`, `displayCreateForm()`, `submitCreateAccount(username, password, fullName, email, phone, profileId)`, `validateInput(username, password, fullName, email, phone, profileId)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `ViewUserAccountPage` | `clickView(userId)`, `displayAccountDetails(account, profile)`, `displayErrorMessage(msg)` |
| `UpdateUserAccountPage` | `clickUpdate(userId)`, `displayUpdateForm(account)`, `submitUpdate(userId, username, fullName, email, phone, profileId)`, `validateInput(username, fullName, email, phone, profileId)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SuspendUserAccountPage` | `clickSuspend(userId)`, `displayConfirmation()`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchUserAccountPage` | `searchUserAccounts(keyword)`, `displayResults(accounts)`, `displayNoResultsMessage()` |
| `InteriorDesignerLoginPage` | `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password)` -> bool, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` |
| `CreateCompanyProfilePage` | `clickCreateCompanyProfile()`, `displayCreateForm(msg=None)`, `validateInput(companyProfile)` -> bool, `submitCompanyProfile(companyName, description, services, email, phone, address)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`. The field rules are the module function `getFieldErrors(companyProfile)`, reused by US16 |
| `ViewCompanyProfilePage` | `clickView()`, `displayCompanyProfile(profile)`, `displayErrorMessage(msg)` |
| `UpdateCompanyProfilePage` | `clickUpdate()`, `displayUpdateForm(msg=None)`, `validateInput(companyProfile)` -> bool, `submitUpdate(companyName, description, services, email, phone, address)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `DeleteCompanyProfilePage` | `clickDelete()`, `displayConfirmation(profile)`, `submitDelete(choice, companyId, revision)`, `confirmDelete(companyId, revision)`, `cancelDelete()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `RestoreCompanyProfilePage` | `submitRestore(companyId, revision)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchCompanyInformationPage` | `searchCompanyInformation(keyword)`, `displayResults(companyProfile)`, `displayNoResultsMessage()`, `displayNotFoundMessage()` |
| `InteriorDesignerLogoutPage` | `clickLogout()`, `displayLoginPage(msg)` |
| `PlatformManagerLoginPage` | `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password)` -> bool, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` |

The designer pages never take the owner from the URL or the form - `designerId` is always `session["userId"]`.

## Shared variable names

Use these names for the same things everywhere (they come from the sequence diagrams):

| Name | Meaning |
|---|---|
| `account` | a UserAccount (None if login failed) |
| `profile` | a UserProfile (None if not found) |
| `permissionList` | all 8 permissions, for the tick boxes |
| `permissions` | the permissions a profile has / that were ticked |
| `loggedOut` | result of `logout()` |
| `fieldErrors` | dict of form errors, keys `"profileName"` and `"permissions"` (US3, US5), or the company field names (US14, US16) |
| `msg` | the message passed to a display...Message() method |
| `keyword` | what was typed in the search box (US7, US12, US18) |
| `profiles` | list of UserProfile from a search (US7), or for the profile drop-down (US8, US10) |
| `accounts` | list of UserAccount from a search (US12) |
| `form` | dict of what's in the account form (US8, US10) - not `username`, because base.html already uses `{{ username }}` for "Logged in as ..." |
| `designerId` | userId of the designer who owns the company profile - always `session["userId"]` (US14 - US18) |
| `companyProfile` | the CompanyProfile the page builds from the company form (US14, US16) |
| `company` | a CompanyProfile, passed to the company templates (US14 - US17) |
| `matchedFields` | names of the company fields that matched a search (on the returned `companyProfile`, US18) |
| `revision` | the company profile's revision number, sent back by the delete box / Restore button so a stale one can't delete or restore (US17) |

**Session keys:** `session["userId"]`, `session["profileId"]`, `session["username"]` (set at login, cleared at logout). Every login clears the old session first.

**Status values:** exactly `"Active"` or `"Suspended"`

**HTML form field names:** `username`, `password`, `profileName`, `description`, `permissions` (tick boxes), `keyword` (search box), `choice` (`ok` / `cancel` in the suspend box, `delete` / `cancel` in the US17 delete box), `fullName`, `email`, `phone`, `profileId` (drop-down), `companyName`, `services`, `address`, `companyId` + `revision` (hidden, US17 delete box and Restore button)

**Templates:** `base.html` (admin pages extend this), `login.html`, `dashboard.html`, `userProfiles.html`, `createUserProfile.html`, `viewUserProfile.html`, `updateUserProfile.html`, `userAccounts.html`, `createUserAccount.html`, `viewUserAccount.html`, `updateUserAccount.html`

Sprint 2: `interiorDesignerBase.html` (designer pages extend this - header has the US19 Log out button), `interiorDesignerLogin.html`, `interiorDesignerDashboard.html`, `interiorDesignerAccessDenied.html`, `createCompanyProfile.html`, `viewCompanyProfile.html`, `companyProfileDetails.html` (the reusable company card, for later customer pages too), `companyProfileNotFound.html`, `updateCompanyProfile.html`, `deleteCompanyProfile.html`, `companyProfileDeleteError.html`, `searchCompanyInformation.html`, `platformManagerLogin.html`, `platformManagerDashboard.html`

## URLs

| URL | Method | Story |
|---|---|---|
| `/login` | GET, POST | US1 (designers and managers are sent to their own dashboard) |
| `/logout` | POST | US2 |
| `/dashboard` | GET | US1 (User Admin only - designers and managers are redirected to their own dashboard) |
| `/profiles` | GET | list page + US7 search (`/profiles?keyword=...`) |
| `/profiles/create` | GET, POST | US3 |
| `/profiles/<profileId>` | GET | US4 |
| `/profiles/<profileId>/update` | GET, POST | US5 |
| `/profiles/<profileId>/suspend` | GET (shows the "Are you sure?" box), POST (OK / Cancel) | US6 |
| `/accounts` | GET | list page + US12 search (`/accounts?keyword=...`) |
| `/accounts/create` | GET, POST | US8 |
| `/accounts/<userId>` | GET | US9 |
| `/accounts/<userId>/update` | GET, POST | US10 |
| `/accounts/<userId>/suspend` | GET (shows the confirmation box), POST (Suspend / Cancel) | US11 |
| `/designer/login` | GET, POST | US13 |
| `/designer/dashboard` | GET | US13 |
| `/designer/company/create` | GET, POST | US14 |
| `/designer/company` | GET | US15 |
| `/designer/company/update` | GET, POST | US16 |
| `/designer/company/delete` | GET (shows the confirmation box), POST (Delete / Cancel) | US17 |
| `/designer/company/restore` | POST (dashboard's Restore button) | US17 (restore) |
| `/designer/company/search` | GET (`?keyword=...`) | US18 |
| `/designer/logout` | POST | US19 |
| `/manager/login` | GET, POST | US39 |
| `/manager/dashboard` | GET | US39 |

## Messages (copy them exactly - the test cases check them)

| Constant | Text | Story |
|---|---|---|
| `MSG_EMPTY_FIELDS` | Please enter your username and password | US1 |
| `MSG_INVALID_LOGIN` | Invalid login details or account suspended | US1 |
| `MSG_LOGGED_OUT` | You have logged out successfully | US2 |
| `MSG_SESSION_ENDED` | Your session has already ended | US2 |
| `MSG_CREATED` | User profile created successfully | US3 |
| `MSG_NAME_TAKEN` | A user profile with this name already exists | US3, US5 |
| `MSG_FIX_FIELDS` | Please fix the highlighted fields | US3, US5 |
| `MSG_NAME_LENGTH` | Profile name must be 3-50 characters | US3, US5 |
| `MSG_NO_PERMISSION` | Tick at least one permission | US3, US5 |
| `MSG_NOT_FOUND` | User profile not found | US4, US5 |
| `MSG_UPDATED` | User profile updated successfully | US5 |
| `MSG_SUSPENDED` | User profile suspended successfully | US6 |
| `MSG_CANNOT_SUSPEND` | This user profile cannot be suspended | US6 |
| `MSG_NO_RESULTS` | No user profiles found | US7 |
| `MSG_CREATED` | User account created successfully | US8 |
| `MSG_REQUIRED` | Please fill in all required fields | US8, US10 |
| `MSG_INVALID` | Invalid profile or username already exists | US8, US10 |
| `MSG_NOT_FOUND` | Account not found | US9, US10 |
| `MSG_UPDATED` | User account updated successfully | US10 |
| `MSG_SUSPENDED` | User account suspended successfully | US11 |
| `MSG_CANNOT_SUSPEND` | This user account cannot be suspended | US11 |
| `MSG_NO_RESULTS` | No user accounts found | US12 |
| `MSG_EMPTY_FIELDS` | Please enter your username and password | US13, US39 |
| `MSG_INVALID_LOGIN` | Invalid login details or access unavailable | US13, US39 |
| `MSG_CREATED` | Company profile created successfully | US14 |
| `MSG_FIX_FIELDS` | Please fix the highlighted fields | US14, US16 |
| `MSG_EXISTS` | You already have a company profile | US14 |
| `MSG_NOT_FOUND` | You have not created a company profile yet | US15, US16, US17, US18 |
| `MSG_UPDATED` | Company profile updated successfully | US16 |
| `MSG_DELETED` | Company profile deleted successfully | US17 |
| `MSG_CONFIRM_AGAIN` | Please open the delete confirmation and try again | US17 |
| `MSG_FAILED` | Company profile could not be deleted. Please reopen the confirmation | US17 |
| `MSG_RESTORED` | Company profile restored successfully | US17 (restore) |
| `MSG_RESTORE_FAILED` | Company profile could not be restored. Please reopen the dashboard and try again | US17 (restore) |
| `MSG_NO_RESULTS` | No matching company information found | US18 |
| `MSG_LOGGED_OUT` | You have logged out successfully | US19 |
| `MSG_SESSION_ENDED` | Your session has already ended | US19 |

Company form field errors (from `CreateCompanyProfileController.getFieldErrors()`, US14 and US16): "This field is required", "Maximum N characters", "Company name must be 3-100 characters", "Enter a valid email address". Empty optional company fields are shown as "Not provided".

## Still to do

- GitHub Actions workflow to run `pytest` on every push
