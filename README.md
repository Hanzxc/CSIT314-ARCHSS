# CSIT314-ARCHSS

Interior Design Platform - CSIT314 group project.
Sprint 1 covers the User Admin's user stories **US1 - US6** (log in, log out, create / view / update / suspend user profile).
Sprint 2 starts with **US7** (search user profiles).
The design docs and diagrams for each story are in [Sprint_1/](Sprint_1/) and [Sprint_2/](Sprint_2/).

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
python -m database.seedData   # creates the database + 100 profiles / 100 accounts of test data
python app.py          # starts the site at http://127.0.0.1:5000
pytest                 # runs all the unit tests
```

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
│   └── searchUserProfilePage.py        US7
├── control/                    one controller per use case (business rules)
│   ├── loginController.py              US1
│   ├── logoutController.py             US2
│   ├── createUserProfileController.py  US3
│   ├── viewUserProfileController.py    US4
│   ├── updateUserProfileController.py  US5
│   ├── suspendUserProfileController.py US6
│   └── searchUserProfileController.py  US7
├── entity/                     reads and writes the database
│   ├── userAccount.py
│   └── userProfile.py
├── database/
│   ├── schema.sql              user_profile + user_account tables
│   └── db.py                   getConnection(), initDatabase()
├── templates/                  HTML pages, from the wireframes (base.html = shared header + menu)
├── static/                     style.css shared by every page
├── tests/                      one test file per user story (UT cases from the docs)
├── Sprint_1/                   US1-US6 docs + diagrams
└── Sprint_2/                   US7 docs + diagrams
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
| `isActive()` | bool | US1 |
| `hashPassword(password)` (helper, not in a class) | str | US1, test data |

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
| `fieldErrors` | dict of form errors, keys `"profileName"` and `"permissions"` |
| `msg` | the message passed to a display...Message() method |
| `keyword` | what was typed in the search box (US7) |
| `profiles` | list of UserProfile from a search (US7) |

**Session keys:** `session["userId"]`, `session["profileId"]`, `session["username"]` (set at login, cleared at logout)

**Status values:** exactly `"Active"` or `"Suspended"`

**HTML form field names:** `username`, `password`, `profileName`, `description`, `permissions` (tick boxes), `keyword` (search box), `choice` (`ok` / `cancel` in the suspend box)

**Templates:** `base.html` (admin pages extend this), `login.html`, `dashboard.html`, `userProfiles.html`, `createUserProfile.html`, `viewUserProfile.html`, `updateUserProfile.html`

## URLs

| URL | Method | Story |
|---|---|---|
| `/login` | GET, POST | US1 |
| `/logout` | POST | US2 |
| `/dashboard` | GET | US1 |
| `/profiles` | GET | list page + US7 search (`/profiles?keyword=...`) |
| `/profiles/create` | GET, POST | US3 |
| `/profiles/<profileId>` | GET | US4 |
| `/profiles/<profileId>/update` | GET, POST | US5 |
| `/profiles/<profileId>/suspend` | GET (shows the "Are you sure?" box), POST (OK / Cancel) | US6 |

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

## Still to do

- GitHub Actions workflow to run `pytest` on every push
