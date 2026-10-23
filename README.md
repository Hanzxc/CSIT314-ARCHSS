# CSIT314-ARCHSS

Interior Design Platform - CSIT314 group project.
Sprint 1 covers the User Admin's user stories **US1 - US12** (log in, log out, create / view / update / suspend / search user profiles and user accounts).
Sprint 2 covers the Interior Designer's stories **US13 - US19** (log in, create / view / update / delete / search company profile, log out) and the Platform Manager's **US39** (log in).
The design docs (one .docx write-up per story) and diagrams for each story are in [Sprint_1/](Sprint_1/) and [Sprint_2/](Sprint_2/).

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

If you already have a `database/archss.db` from Sprint 1 you don't need to delete it - `python app.py` adds the new `company_profile` table on startup.

Log in pages: User Admin `/login`, Interior Designer `/designer/login`, Platform Manager `/manager/login`. The shared `/login` also sends designers and managers to their own dashboard. The sample accounts from `seedData` use the password `Pass@123` (e.g. `design006` is an active designer, `pm005` an active manager).

## Folder layout (B-C-E)

The actor only talks to the **boundary**, the boundary only talks to the **controller**, and the controller works with the **entity** classes. One controller per use case.

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
│   ├── searchCompanyInformationPage.py US18
│   ├── interiorDesignerLogoutPage.py   US19
│   └── platformManagerLoginPage.py     US39 (also the manager dashboard)
├── control/                    one controller per use case (business rules)
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
│   ├── interiorDesignerLoginController.py    US13 (its access check is reused by US14 - US18)
│   ├── createCompanyProfileController.py     US14
│   ├── viewCompanyProfileController.py       US15
│   ├── updateCompanyProfileController.py     US16
│   ├── deleteCompanyProfileController.py     US17
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
| `createUserAccount(username, password, fullName, email, phone, profileId)` | bool | US8 |
| `updateUserAccount(userId, username, fullName, email, phone, profileId)` | bool | US10 |
| `suspendUserAccount(userId)` | bool | US11 |
| `searchUserAccounts(keyword)` | list of UserAccount (empty list if nothing matches) | US12 |
| `hashPassword(password)` (helper, not in a class) | str | US1, US8, test data |

**UserProfile** - `entity/userProfile.py`

| Attributes | |
|---|---|
| `profileId` int, `profileName` str, `description` str, `permissions` list of str, `status` str | |

| Method | Returns | Used in |
|---|---|---|
| `getUserProfile(profileId)` | UserProfile or None | US1, US4, US5, US6 |
| `isActive()` | bool | US1, US6 |
| `getAllPermissions()` | list of str | US3, US5 |
| `isProfileNameTaken(profileName, profileId=None)` | bool | US3 (no id), US5 (with id) |
| `createUserProfile(profileName, description, permissions)` | bool | US3 |
| `updateUserProfile(profileId, profileName, description, permissions)` | bool | US5 |
| `suspendUserProfile(profileId)` | bool | US6 |
| `searchUserProfiles(keyword)` | list of UserProfile (empty list if nothing matches) | US7 |

`ALL_PERMISSIONS` - the 8 fixed permissions: Manage user accounts, Manage user profiles, Manage company profile, Manage own IDPs, View IDP statistics, Search, view and save IDPs, Manage IDP categories, Generate reports.

**CompanyProfile** - `entity/companyProfile.py` (table `company_profile`, one row per designer - `designerId` is UNIQUE)

| Attributes | |
|---|---|
| `companyId` int, `designerId` int (the owner's userId), `companyName` str, `description` str, `services` str, `email` str, `phone` str, `address` str, `createdDate` str | |

| Method | Returns | Used in |
|---|---|---|
| `getCompanyProfile(designerId)` | CompanyProfile or None | US14, US15, US16, US17, US18 |
| `createCompanyProfile(designerId, companyData)` | bool | US14 |
| `updateCompanyProfile(designerId, companyData)` | bool (False if there's no row - it never inserts) | US16 |
| `deleteCompanyProfile(designerId, companyId)` | bool (both must match) | US17 |
| `searchCompanyInformation(designerId, keyword)` | list of dicts `{"field", "label", "value"}` | US18 |

`companyData` is a dict with the keys `companyName`, `description`, `services`, `email`, `phone`, `address`.

**Who can do what** - access is decided by the profile's permissions, not its name, and is checked again from the database on every page:

| Role | Needs these permissions | Checked by |
|---|---|---|
| User Admin | Manage user accounts + Manage user profiles | `loginRequired` in `app.py` |
| Interior Designer | Manage company profile + Manage own IDPs | `InteriorDesignerLoginController.getAuthenticatedDesigner(userId)` |
| Platform Manager | Manage IDP categories + Generate reports | `PlatformManagerLoginController.getAuthenticatedManager(userId)` |

The account and its profile must both be Active. A designer or manager who opens a User Admin page gets HTTP 403, and so does anyone who opens a designer or manager page without the right permissions. Someone who isn't logged in is sent to that role's login page.

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
| `SuspendUserProfileController` | `suspendUserProfile(profileId, adminProfileId)` | bool |
| `SearchUserProfileController` | `searchUserProfiles(keyword)` | list of UserProfile |
| `CreateUserAccountController` | `getAllUserProfiles()` (for the drop-down) | list of UserProfile |
| | `createUserAccount(username, password, fullName, email, phone, profileId)` | bool |
| `ViewUserAccountController` | `viewUserAccount(userId)` - also sets `self.profile` to the account's profile | UserAccount or None |
| `UpdateUserAccountController` | `getUserAccount(userId)` | UserAccount or None |
| | `getAllUserProfiles()` (for the drop-down) | list of UserProfile |
| | `updateUserAccount(userId, username, fullName, email, phone, profileId)` | bool |
| `SuspendUserAccountController` | `suspendUserAccount(userId, adminUserId)` | bool |
| `SearchUserAccountController` | `searchUserAccounts(keyword)` | list of UserAccount |
| `InteriorDesignerLoginController` | `login(username, password)` | UserAccount or None |
| | `isInteriorDesigner(account)` | bool |
| | `getAuthenticatedDesigner(userId)` (access check used by US14 - US18) | UserAccount or None |
| `CreateCompanyProfileController` | `canCreateCompanyProfile(designerId)` | bool |
| | `hasCompanyProfile(designerId)` | bool |
| | `getFieldErrors(companyData)` (field rules, reused by US16) | dict |
| | `createCompanyProfile(designerId, companyData)` | bool |
| `ViewCompanyProfileController` | `canViewCompanyProfile(designerId)` | bool |
| | `viewCompanyProfile(designerId)` | CompanyProfile or None |
| `UpdateCompanyProfileController` | `canUpdateCompanyProfile(designerId)` | bool |
| | `getCompanyProfile(designerId)` | CompanyProfile or None |
| | `getFieldErrors(companyData)` | dict |
| | `updateCompanyProfile(designerId, companyData)` | bool |
| `DeleteCompanyProfileController` | `canDeleteCompanyProfile(designerId)` | bool |
| | `getCompanyProfile(designerId)` | CompanyProfile or None |
| | `deleteCompanyProfile(designerId, companyId)` | bool |
| `SearchCompanyInformationController` | `canSearchCompanyInformation(designerId)` | bool |
| | `hasCompanyProfile(designerId)` | bool |
| | `searchCompanyInformation(designerId, keyword)` | list of dicts |
| `InteriorDesignerLogoutController` | `logout()` (calls the US2 `LogoutController`, then clears the whole session) | bool |
| `PlatformManagerLoginController` | `login(username, password)` | UserAccount or None |
| | `isPlatformManager(account)` | bool |
| | `getAuthenticatedManager(userId)` | UserAccount or None |

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
| `CreateCompanyProfilePage` | `checkAccess()`, `clickCreateCompanyProfile()`, `displayCreateForm(msg=None)`, `validateInput(companyData)` -> bool, `submitCompanyProfile(companyData)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `ViewCompanyProfilePage` | `checkAccess()`, `clickView()`, `displayCompanyProfile(profile)`, `displayErrorMessage(msg)` |
| `UpdateCompanyProfilePage` | `checkAccess()`, `clickUpdate()`, `displayUpdateForm(msg=None)`, `validateInput(companyData)` -> bool, `submitUpdate(companyData)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `DeleteCompanyProfilePage` | `checkAccess()`, `clickDelete()`, `displayConfirmation(profile)`, `submitDelete(choice, companyId, confirmationToken)`, `confirmDelete(companyId, confirmationToken)`, `cancelDelete()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `SearchCompanyInformationPage` | `checkAccess()`, `searchCompanyInformation(keyword)`, `displayResults(results)`, `displayNoResultsMessage()`, `displayNotFoundMessage()` |
| `InteriorDesignerLogoutPage` | `clickLogout()`, `displayLoginPage(msg)` |
| `PlatformManagerLoginPage` | `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password)` -> bool, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` |

The designer pages never take the owner from the URL or the form - `designerId` is always `session["userId"]`.

## Shared variable names

Use these names for the same things everywhere (they come from the sequence diagrams):

| Name | Meaning |
|---|---|
| `account` | a UserAccount (None if login failed) |
| `profile` | a UserProfile (None if not found) |
| `accountActive` / `profileActive` | result of `isActive()` in login |
| `permissionList` | all 8 permissions, for the tick boxes |
| `permissions` | the permissions a profile has / that were ticked |
| `nameTaken` | result of `isProfileNameTaken()` |
| `success` | what a controller returns to the page (True / False) |
| `loggedOut` | result of `logout()` |
| `adminProfileId` | profileId of the admin who is logged in |
| `fieldErrors` | dict of form errors, keys `"profileName"` and `"permissions"` (US3, US5), or the company field names (US14, US16) |
| `msg` | the message passed to a display...Message() method |
| `keyword` | what was typed in the search box (US7, US12, US18) |
| `profiles` | list of UserProfile from a search (US7), or for the profile drop-down (US8, US10) |
| `accounts` | list of UserAccount from a search (US12) |
| `adminUserId` | userId of the admin who is logged in (US11) |
| `usernameTaken` | result of `isUsernameTaken()` (US8, US10) |
| `form` | dict of what's in the account form (US8, US10) - not `username`, because base.html already uses `{{ username }}` for "Logged in as ..." |
| `designerId` | userId of the designer who owns the company profile - always `session["userId"]` (US14 - US18) |
| `companyData` | dict of what's in the company form (US14, US16) |
| `company` | a CompanyProfile, passed to the company templates (US15 - US17) |
| `results` | list of matching company fields from a search (US18) |
| `confirmationToken` | random token that proves the delete box was opened (US17) |

**Session keys:** `session["userId"]`, `session["profileId"]`, `session["username"]` (set at login, cleared at logout). US17 also uses `session["companyDeleteConfirmation"]` (`designerId`, `companyId`, `token`) while the delete box is open. Every login clears the old session first.

**Status values:** exactly `"Active"` or `"Suspended"`

**HTML form field names:** `username`, `password`, `profileName`, `description`, `permissions` (tick boxes), `keyword` (search box), `choice` (`ok` / `cancel` in the suspend box, `delete` / `cancel` in the US17 delete box), `fullName`, `email`, `phone`, `profileId` (drop-down), `companyName`, `services`, `address`, `companyId` + `confirmationToken` (hidden, US17)

**Templates:** `base.html` (admin pages extend this), `login.html`, `dashboard.html`, `userProfiles.html`, `createUserProfile.html`, `viewUserProfile.html`, `updateUserProfile.html`, `userAccounts.html`, `createUserAccount.html`, `viewUserAccount.html`, `updateUserAccount.html`

Sprint 2: `interiorDesignerBase.html` (designer pages extend this - header has the US19 Log out button), `interiorDesignerLogin.html`, `interiorDesignerDashboard.html`, `interiorDesignerAccessDenied.html`, `createCompanyProfile.html`, `viewCompanyProfile.html`, `companyProfileDetails.html` (the reusable company card, for later customer pages too), `companyProfileNotFound.html`, `updateCompanyProfile.html`, `deleteCompanyProfile.html`, `companyProfileDeleteError.html`, `searchCompanyInformation.html`, `platformManagerLogin.html`, `platformManagerDashboard.html`, `platformManagerAccessDenied.html`

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
| `MSG_FAILED` | Company profile could not be created. Please try again | US14 |
| `MSG_NOT_FOUND` | You have not created a company profile yet | US15, US16, US17, US18 |
| `MSG_UPDATED` | Company profile updated successfully | US16 |
| `MSG_FAILED` | Company profile could not be updated. Please try again | US16 |
| `MSG_DELETED` | Company profile deleted successfully | US17 |
| `MSG_CONFIRM_AGAIN` | Please open the delete confirmation and try again | US17 |
| `MSG_FAILED` | Company profile could not be deleted. Please reopen the confirmation | US17 |
| `MSG_NO_RESULTS` | No matching company information found | US18 |
| `MSG_LOGGED_OUT` | You have logged out successfully | US19 |
| `MSG_SESSION_ENDED` | Your session has already ended | US19 |

Company form field errors (from `CreateCompanyProfileController.getFieldErrors()`, US14 and US16): "This field is required", "Maximum N characters", "Company name must be 3-100 characters", "Enter a valid email address". Empty optional company fields are shown as "Not provided".

## Still to do

- GitHub Actions workflow to run `pytest` on every push
