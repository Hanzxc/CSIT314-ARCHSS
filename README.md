# CSIT314-ARCHSS

Interior Design Platform - CSIT314 group project.
48 user stories over 5 sprints, for 4 actors: User Admin, Interior Designer, Platform Manager and Customer.

| Sprint | Stories |
|---|---|
| Sprint 1 | User Admin **US1 - US12** (log in, log out, create / view / update / suspend / search user profiles and user accounts) |
| Sprint 2 | Interior Designer **US13 - US19** (log in, create / view / update / delete / search company profile, log out) and Platform Manager **US39 - US45** (log in, log out, create / view / update / suspend / search IDP categories) |
| Sprint 3 | Interior Designer **US20 - US24** (add / view / update / delete / search current IDPs) and Customer **US30 - US32, US36** (log in, search IDPs, view an IDP, log out) |
| Sprint 4 | Interior Designer **US25 - US29** (add / view / update / delete / search past IDPs) and Customer **US33 - US35** (save an IDP, search and view the saved list) |
| Sprint 5 | Interior Designer **US37 - US38** (view and save statistics of their IDPs) and Platform Manager **US46 - US48** (daily / weekly / monthly category reports) |

Every story has its own folder `Sprint_N/USxx - <name>/` (in [Sprint_1/](Sprint_1/) to [Sprint_5/](Sprint_5/)) with the .docx write-up, the editable .drawio, the exported PNGs in `diagrams/` and a README.

## Tech we're using

| What | Tool | Why |
|---|---|---|
| Language | **Python 3.11+** | easy for everyone to read and write |
| Web pages | **Flask** | simplest way to turn our wireframes into web pages - each Boundary class is a page |
| Database | **SQLite** | built into Python, nothing to install |
| Unit tests | **pytest** | for TDD - write the test first, then the code |

## Setup

```
pip install -r requirements.txt
python -m database.seedData              # creates the database + 100 profiles / 100 accounts of test data (incl. the 4 default profiles) and 4 IDP categories
python -m database.seedCompanyData       # optional: 100 demo designers (companydemo001 ... / Demo@123), each with a company profile
python -m database.seedIDPCategoryData   # optional: 2 more IDP categories + 4 current IDPs for companydemo001 - 004 (run after seedCompanyData)
python -m database.seedCurrentIDPData    # optional: idpdemo001 / idpdemo002 (Demo@123), each with 2 current IDPs
python -m database.seedAnalyticsData     # optional: adds some IDP views and saves so the US37/38 statistics and US46-48 reports aren't all zeros; run it after the IDP seeds
python app.py                            # starts the site at http://127.0.0.1:5000
python -m pytest                         # runs all the tests
```

Run the optional seeds in this order. Every seed script is safe to run more than once - rows that already exist are skipped.

The tests never touch `database/archss.db`: `tests/conftest.py` gives every test its own fresh database in a temp folder. One story only: `python -m pytest tests/test_us21_viewCurrentIDPs.py -q`.

If you already have a `database/archss.db` from an earlier sprint you don't need to delete it - `python app.py` (and every seed script) runs `initDatabase()`, which adds any missing tables and the US17 `status` / `revision` columns without touching the existing rows.

Log in pages: User Admin `/login`, Interior Designer `/designer/login`, Customer `/customer/login`, Platform Manager `/manager/login`. Each role only logs in on its own page. After `seedData`: `admin01 / Admin@123` (User Admin), `designer1 / Pass@123` (designer), `cust001 / Cust@123` (customer). The sample accounts all use `Pass@123`, e.g. `design006` is an active designer, `cust002` an active customer and `pm005` an active manager (not every sample account can log in - some are suspended or miss a permission).

## Folder layout (B-C-E)

The actor only talks to the **boundary**, the boundary only talks to the **controller**, and the controller works with the **entity** classes. One controller per use case.

**Who checks what** (from the lecturer's feedback):

| Layer | Its job |
|---|---|
| Boundary | checks **all** the input (required fields, lengths, email format, valid date, the admin not suspending themselves) and trims spaces before passing anything on |
| Control | just calls the entity and returns the result straight back - no checking, no `success` variable |
| Entity | checks the database state (username / profile name / category name taken, profile or category not Active, company profile already exists, IDP already saved or not visible, only suspending Active rows), then inserts / updates and commits. No `.strip()` here |

Being logged in as the right role is the **precondition** of every use case after log in, so no page, controller or entity checks the role. `app.py` has one small route decorator per role - `loginRequired` (User Admin pages), `designerLoginRequired`, `customerLoginRequired` and `managerLoginRequired` - and all it does is redirect someone with no session to that role's login page, so a page doesn't crash when nobody is logged in. The four log out routes have no decorator (with no session you just get "Your session has already ended").

```
CSIT314-ARCHSS/
├── app.py                      Flask app - links each URL to its boundary class, + the 4 route decorators
├── requirements.txt            flask, pytest
├── pytest.ini                  lets the tests import our folders
├── boundary/                   pages (what the user sees) - one *Page.py per use case, see "Boundary" below
├── control/                    one *Controller.py per use case (just calls the entity), see "Control" below
├── entity/                     reads and writes the database
│   ├── userAccount.py          US1, US8 - US12 (and every log in)
│   ├── userProfile.py          US3 - US7
│   ├── companyProfile.py       US14 - US18
│   ├── idpCategory.py          US41 - US45 (and the category drop-downs)
│   ├── idp.py                  US20 - US29, US31, US32
│   ├── savedIDP.py             US33 - US35
│   └── idpAnalytics.py         US37, US38, US46 - US48
├── database/
│   ├── schema.sql              user_profile, user_account, company_profile, idp_category, idp, saved_idp, idp_view
│   ├── db.py                   getConnection(), initDatabase()
│   ├── seedData.py             default + sample profiles and accounts, 4 IDP categories
│   ├── seedCompanyData.py      100 demo designers with company profiles
│   ├── seedIDPCategoryData.py  2 more IDP categories + demo current IDPs
│   ├── seedCurrentIDPData.py   2 demo designers with current IDPs
│   └── seedAnalyticsData.py    demo IDP views and saves (US37, US38, US46 - US48)
├── templates/                  HTML pages, from the wireframes (see "Templates" below)
├── static/                     style.css shared by every page
├── tests/                      one test file per user story (UT cases from the docs) + conftest.py
├── user stories/               userstories.txt - the 48 user stories
├── Sprint_1/                   US1 - US12
├── Sprint_2/                   US13 - US19, US39 - US45
├── Sprint_3/                   US20 - US24, US30 - US32, US36
├── Sprint_4/                   US25 - US29, US33 - US35
└── Sprint_5/                   US37, US38, US46 - US48
    └── USxx - <name>/          one folder per story
        ├── USxx <name>.docx        the write-up
        ├── USxx <name>.drawio      the editable diagrams and wireframes
        ├── diagrams/               the exported PNGs
        └── README.md
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
| Database tables | snake_case | `user_account`, `idp_category` |
| Database columns | camelCase, same as the attribute | `profileName` |
| Test files / functions | `test_us<N>_...py` / `test_ut<N>_<M>_...` (unit), `test_tc<N>_<M>_...` (system test through the Flask test client) | `test_ut1_1_verifyCredentials_correct` |

Controllers inside a page are always called `self.<controllerName>` e.g. `self.loginController`. A controller borrowed from another story is just created where it's needed, e.g. `SearchIDPCategoryController().searchIDPCategories("")`.

## Classes and functions

### Entity

**UserAccount** - `entity/userAccount.py`

| Attributes | |
|---|---|
| `userId` int, `username` str, `password` str (sha256 hash), `fullName` str, `email` str, `phone` str, `profileId` int, `status` str, `createdDate` str | |

| Method | Returns | Used in |
|---|---|---|
| `verifyCredentials(username, password, requiredPermissions)` | UserAccount or None (right password, Active account, Active profile that has all the permissions) | US1, US13, US30, US39 |
| `isActive()` | bool | inside `verifyCredentials` |
| `getUserAccount(userId)` | UserAccount or None | US9, US10, US11 |
| `isUsernameTaken(username, userId=None)` | bool | US8 (no id), US10 (with id) |
| `createUserAccount(account)` | bool (False if the profile isn't Active or the username is taken) | US8 |
| `updateUserAccount(account)` | bool (same checks, its own username is fine, only an Active account) | US10 |
| `suspendUserAccount(userId)` | bool (only an Active account) | US11 |
| `searchUserAccounts(keyword)` | list of UserAccount (username, full name or email; empty list if nothing matches) | US12 |
| `hashPassword(password)` (helper, not in a class) | str | US1, US8, test data |

**UserProfile** - `entity/userProfile.py`

| Attributes | |
|---|---|
| `profileId` int, `profileName` str, `description` str, `permissions` list of str, `status` str | |

| Method | Returns | Used in |
|---|---|---|
| `getUserProfile(profileId)` | UserProfile or None | US4, US5, US6, US8, US9, US10 |
| `isActive()` | bool | US8, US10 (inside the account entity) |
| `getAllPermissions()` | list of str | US3, US5 |
| `isProfileNameTaken(profileName, profileId=None)` | bool | US3 (no id), US5 (with id) |
| `createUserProfile(profile)` | bool (False if the name is taken) | US3 |
| `updateUserProfile(profile)` | bool (False if the name is taken or the profile isn't Active) | US5 |
| `suspendUserProfile(profileId)` | bool (only an Active profile) | US6 |
| `searchUserProfiles(keyword)` | list of UserProfile (name or description; empty list if nothing matches) | US7, and the profile drop-down in US8 / US10 |

`ALL_PERMISSIONS` - the 8 fixed permissions: Manage user accounts, Manage user profiles, Manage company profile, Manage own IDPs, View IDP statistics, Search, view and save IDPs, Manage IDP categories, Generate reports.

**CompanyProfile** - `entity/companyProfile.py` (table `company_profile`, one row per designer - `designerId` is UNIQUE)

| Attributes | |
|---|---|
| `companyId` int, `designerId` int (the owner's userId), `companyName` str, `description` str, `services` str, `email` str, `phone` str, `address` str, `createdDate` str, `status` str, `revision` int, `matchedFields` list of str (US18 only, not a column) | |

| Method | Returns | Used in |
|---|---|---|
| `getCompanyProfile(designerId)` | CompanyProfile or None (the Active one) | US13 dashboard, US15, US16, US17, US32 |
| `createCompanyProfile(companyProfile)` | bool (False if the designer already has a row, Active or Suspended) | US14 |
| `updateCompanyProfile(companyProfile)` | bool (False if there's no Active row - it never inserts) | US16 |
| `suspendCompanyProfile(designerId, companyId, expectedRevision)` | bool (owner, id and revision must match) | US17 |
| `getSuspendedCompanyProfile(designerId)` | CompanyProfile or None | US13 dashboard, US17 (restore) |
| `restoreCompanyProfile(designerId, companyId, expectedRevision)` | bool | US17 (restore) |
| `searchCompanyInformation(designerId, keyword)` | the CompanyProfile with `matchedFields` (names of the fields whose name or value contains the keyword; empty list = no match), or None if there's no Active profile | US18 |

`companyProfile` is a CompanyProfile object the page builds from the form (owner = `session["userId"]`), not a dict.

**IDPCategory** - `entity/idpCategory.py` (table `idp_category`, `categoryName` is UNIQUE, capitals don't matter)

| Attributes | |
|---|---|
| `categoryId` int, `categoryName` str, `description` str, `status` str, `createdDate` str | |

| Method | Returns | Used in |
|---|---|---|
| `getIDPCategory(categoryId)` | IDPCategory or None | US42, US43, US44 |
| `isActive()` | bool | category drop-down in US20, US22, US25, US27 (only Active ones are shown) |
| `isCategoryNameTaken(categoryName, categoryId=None)` | bool | US41 (no id), US43 (with id) |
| `createIDPCategory(idpCategory)` | bool (False if the name is taken) | US41 |
| `updateIDPCategory(idpCategory)` | bool (False if the name is taken or the category isn't Active) | US43 |
| `suspendIDPCategory(categoryId)` | bool (only an Active category; its IDPs are kept) | US44 |
| `searchIDPCategories(keyword)` | list of IDPCategory (name or description, suspended ones included) | US45, and the category drop-down in US20, US22, US25, US27 |
| `getIDPsInCategory(categoryId)` | list of IDP (the Active IDPs in it) | US42 |

**IDP** - `entity/idp.py` (table `idp` - current and past IDPs are the same table, `projectType` is `"Current"` or `"Past"`)

| Attributes | |
|---|---|
| `idpId` int, `designerId` int (the owner's userId), `categoryId` int, `title` str, `description` str, `location` str, `projectType` str, `status` str, `createdDate` str, `categoryName` str (joined from `idp_category`, not a column) | |

| Method | Returns | Used in |
|---|---|---|
| `addCurrentIDP(idp)` | bool (False if the category isn't Active) | US20 |
| `getCurrentIDPs(designerId)` | list of IDP (own Active current IDPs in Active categories, newest first) | US21 |
| `getCurrentIDP(designerId, idpId)` | IDP or None | US21, US22, US23 |
| `updateCurrentIDP(idp)` | bool (own Active current IDP, old and new category both Active) | US22 |
| `suspendCurrentIDP(designerId, idpId)` | bool | US23 |
| `searchCurrentIDPs(designerId, keyword)` | list of IDP (title, description, location or category) | US24 |
| `createPastIDP(idp)` | bool (False if the category isn't Active) | US25 |
| `findPastIDPsByDesignerId(designerId)` | list of IDP (own Active past IDPs, newest first) | US26 |
| `getPastIDPDetails(designerId, idpId)` | IDP or None | US26, US27, US28 |
| `updatePastIDPDetails(idp)` | bool (own Active past IDP, new category Active) | US27 |
| `markPastIDPUnavailable(designerId, idpId)` | bool | US28 |
| `searchByKeywordAndDesigner(keyword, designerId)` | list of IDP (title, description, location or category) | US29 |
| `searchIDPs(keyword)` | list of IDP (every designer's Active IDPs, current and past, in Active categories) | US31 |
| `viewIDP(idpId, countView)` | IDP or None - when it's found and `countView` is True it also adds one `idp_view` row | US32 |

**SavedIDP** - `entity/savedIDP.py` (table `saved_idp`, UNIQUE `customerId` + `idpId`)

| Attributes | |
|---|---|
| `savedId` int, `customerId` int (the customer's userId), `idpId` int, `savedDate` str | |

| Method | Returns | Used in |
|---|---|---|
| `createSavedRecord(customerId, idpId)` | bool (False if it's already saved or customers can't see the IDP) | US33 |
| `getSavedRecords(customerId)` | list of IDP (most recently saved first) | US35 |
| `searchSavedRecords(customerId, keyword)` | list of IDP (title, description, location or category) | US34 |

There is no remove / unsave. "Manage my saved IDPs" (US30) means save, view and search the saved list.

**IDPAnalytics** - `entity/idpAnalytics.py` (reads `idp`, `idp_category`, `idp_view` and `saved_idp`)

| Attributes | |
|---|---|
| `idpId`, `title`, `projectType`, `categoryId`, `categoryName`, `status`, `views` int, `saves` int, `totalIDPs` int, `startDate` date, `endDate` date, `categories` list of IDPAnalytics | |

| Method | Returns | Used in |
|---|---|---|
| `getViewStatistics(designerId)` | list of IDPAnalytics (each of the designer's Active IDPs with `views`, 0 if never viewed) | US37 |
| `getSaveStatistics(designerId)` | list of IDPAnalytics (each Active IDP with `saves` = how many customers saved it) | US38 |
| `getDailyReport(selectedDate)` | IDPAnalytics (`startDate` = `endDate` = that day, plus `categories`) | US46 |
| `getWeeklyReport(selectedDate)` | IDPAnalytics (the Monday - Sunday week that day is in) | US47 |
| `getMonthlyReport(selectedDate)` | IDPAnalytics (1st to last day of that month) | US48 |
| `getCategoryReport(startDate, endDate)` | list of IDPAnalytics, one per category with `totalIDPs`, `views`, `saves` (most viewed first) | US46 - US48 |

A view is one `idp_view` row (added by US32 `IDP.viewIDP`), a save is one `saved_idp` row (US33). The database stores UTC times, so the reports compare local dates.

**Who can do what** - decided at login by the profile's permissions, not its name:

| Role | Logs in at | Needs these permissions | Checked by | Route decorator |
|---|---|---|---|---|
| User Admin | US1 `/login` | Manage user accounts + Manage user profiles | `LoginController` | `loginRequired` |
| Interior Designer | US13 `/designer/login` | Manage company profile + Manage own IDPs | `InteriorDesignerLoginController` | `designerLoginRequired` |
| Customer | US30 `/customer/login` | Search, view and save IDPs | `CustomerLoginController` | `customerLoginRequired` |
| Platform Manager | US39 `/manager/login` | Manage IDP categories + Generate reports | `PlatformManagerLoginController` | `managerLoginRequired` |

Each `login()` is one call to `UserAccount.verifyCredentials(username, password, requiredPermissions)`, which checks the password, that the account and its profile are both Active, and the permissions in one go. Being logged in as that role is the precondition of all the role's other stories - the decorator only sends someone with no session to that role's login page. Each role has its own log out story and controller (US2, US19, US36, US40); they all just clear the session.

### Control

| US | Class | Method | Returns |
|---|---|---|---|
| 1 | `LoginController` | `login(username, password)` | UserAccount or None |
| 2 | `LogoutController` | `logout()` | bool (False if there was no session) |
| 3 | `CreateUserProfileController` | `getAllPermissions()` (US5 uses it too) | list of str |
| | | `createUserProfile(profile)` | bool |
| 4 | `ViewUserProfileController` | `getUserProfile(profileId)` (US6 and US9 use it too) | UserProfile or None |
| 5 | `UpdateUserProfileController` | `getUserProfile(profileId)` | UserProfile or None |
| | | `updateUserProfile(profile)` | bool |
| 6 | `SuspendUserProfileController` | `suspendUserProfile(profileId)` | bool |
| 7 | `SearchUserProfileController` | `searchUserProfiles(keyword)` (US8 / US10 call it with `""` for the drop-down) | list of UserProfile |
| 8 | `CreateUserAccountController` | `createUserAccount(account)` | bool |
| 9 | `ViewUserAccountController` | `viewUserAccount(userId)` (US11 uses it too) | UserAccount or None |
| 10 | `UpdateUserAccountController` | `getUserAccount(userId)` | UserAccount or None |
| | | `updateUserAccount(account)` | bool |
| 11 | `SuspendUserAccountController` | `suspendUserAccount(userId)` | bool |
| 12 | `SearchUserAccountController` | `searchUserAccounts(keyword)` | list of UserAccount |
| 13 | `InteriorDesignerLoginController` | `login(username, password)` | UserAccount or None |
| 14 | `CreateCompanyProfileController` | `createCompanyProfile(companyProfile)` | bool |
| 15 | `ViewCompanyProfileController` | `viewCompanyProfile(designerId)` (the US13 dashboard and US32 use it too) | CompanyProfile or None |
| 16 | `UpdateCompanyProfileController` | `getCompanyProfile(designerId)` | CompanyProfile or None |
| | | `updateCompanyProfile(companyProfile)` | bool |
| 17 | `DeleteCompanyProfileController` | `getCompanyProfile(designerId)` | CompanyProfile or None |
| | | `deleteCompanyProfile(designerId, companyId, expectedRevision)` | bool |
| 17 (restore) | `RestoreCompanyProfileController` | `getSuspendedCompanyProfile(designerId)` (the US13 dashboard uses it) | CompanyProfile or None |
| | | `restoreCompanyProfile(designerId, companyId, expectedRevision)` | bool |
| 18 | `SearchCompanyInformationController` | `searchCompanyInformation(designerId, keyword)` | CompanyProfile (with `matchedFields`) or None |
| 19 | `InteriorDesignerLogoutController` | `logout()` | bool |
| 20 | `AddCurrentIDPController` | `addCurrentIDP(idp)` | bool |
| 21 | `ViewCurrentIDPController` | `viewCurrentIDPs(designerId)` | list of IDP |
| | | `viewCurrentIDP(designerId, idpId)` | IDP or None |
| 22 | `UpdateCurrentIDPController` | `getCurrentIDP(designerId, idpId)` | IDP or None |
| | | `updateCurrentIDP(idp)` | bool |
| 23 | `DeleteCurrentIDPController` | `getCurrentIDP(designerId, idpId)` | IDP or None |
| | | `deleteCurrentIDP(designerId, idpId)` | bool |
| 24 | `SearchCurrentIDPController` | `searchCurrentIDPs(designerId, keyword)` | list of IDP |
| 25 | `AddPastIDPController` | `addPastIDP(idp)` | bool |
| 26 | `ViewPastIDPController` | `getPastIDPs(designerId)` | list of IDP |
| | | `getPastIDPDetails(designerId, idpId)` | IDP or None |
| 27 | `UpdatePastIDPController` | `getPastIDP(designerId, idpId)` | IDP or None |
| | | `updatePastIDP(idp)` | bool |
| 28 | `DeletePastIDPController` | `getPastIDP(designerId, idpId)` | IDP or None |
| | | `deletePastIDP(designerId, idpId)` | bool |
| 29 | `SearchPastIDPController` | `searchPastIDPs(designerId, keyword)` | list of IDP |
| 30 | `CustomerLoginController` | `login(username, password)` | UserAccount or None |
| 31 | `SearchIDPController` | `searchIDPs(keyword)` | list of IDP |
| 32 | `ViewIDPController` | `viewIDP(idpId, countView)` | IDP or None |
| 33 | `SaveIDPController` | `saveIDP(customerId, idpId)` | bool |
| 34 | `SearchSavedListController` | `searchSavedList(customerId, keyword)` | list of IDP |
| 35 | `ViewSavedListController` | `getSavedList(customerId)` | list of IDP |
| 36 | `CustomerLogoutController` | `logout()` | bool |
| 37 | `ViewIDPViewStatisticsController` | `getViewStatistics(designerId)` | list of IDPAnalytics |
| 38 | `ViewIDPSaveStatisticsController` | `getSaveStatistics(designerId)` | list of IDPAnalytics |
| 39 | `PlatformManagerLoginController` | `login(username, password)` | UserAccount or None |
| 40 | `PlatformManagerLogoutController` | `logout()` | bool |
| 41 | `CreateIDPCategoryController` | `createIDPCategory(idpCategory)` | bool |
| 42 | `ViewIDPCategoryController` | `viewIDPCategory(categoryId)` (US44 uses it too) | IDPCategory or None |
| | | `getIDPsInCategory(categoryId)` | list of IDP |
| 43 | `UpdateIDPCategoryController` | `getIDPCategory(categoryId)` | IDPCategory or None |
| | | `updateIDPCategory(idpCategory)` | bool |
| 44 | `SuspendIDPCategoryController` | `suspendIDPCategory(categoryId)` | bool |
| 45 | `SearchIDPCategoryController` | `searchIDPCategories(keyword)` (US20, US22, US25, US27 call it with `""` for the category drop-down) | list of IDPCategory |
| 46 | `GenerateDailyReportController` | `generateDailyReport(selectedDate)` | IDPAnalytics |
| 47 | `GenerateWeeklyReportController` | `generateWeeklyReport(selectedDate)` | IDPAnalytics |
| 48 | `GenerateMonthlyReportController` | `generateMonthlyReport(selectedDate)` | IDPAnalytics |

### Boundary

| Class | US | Methods |
|---|---|---|
| `LoginPage` | 1 | `openLoginPage()`, `displayLoginForm()`, `submitLogin(username, password)`, `validateInput(username, password)` -> bool, `redirectToDashboard(account)`, `displayErrorMessage(msg)` |
| `LogoutPage` | 2 | `clickLogout()`, `displayLoginPage(msg)` |
| `CreateUserProfilePage` | 3 | `clickCreateUserProfile()`, `displayCreateForm(permissionList, msg=None)`, `submitUserProfile(profileName, description, permissions)`, `validateInput(profile)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `ViewUserProfilePage` | 4 | `selectUserProfile(profileId)`, `displayUserProfile(profile)`, `displayErrorMessage(msg)` |
| `UpdateUserProfilePage` | 5 | `clickUpdate(profileId)`, `displayUpdateForm(profile, permissionList, msg=None)`, `submitUpdate(profileName, description, permissions)`, `validateInput(profile)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFound()` |
| `SuspendUserProfilePage` | 6 | `clickSuspend(profileId)`, `displayConfirmation(profile)`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchUserProfilePage` | 7 | `searchUserProfiles(keyword)`, `displayResults(profiles)`, `displayNoResultsMessage()` |
| `CreateUserAccountPage` | 8 | `clickCreateUserAccount()`, `displayCreateForm(profiles, msg=None)`, `submitCreateAccount(username, password, fullName, email, phone, profileId)`, `validateInput(account)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `ViewUserAccountPage` | 9 | `clickView(userId)`, `displayAccountDetails(account, profile)`, `displayErrorMessage(msg)` |
| `UpdateUserAccountPage` | 10 | `clickUpdate(userId)`, `displayUpdateForm(account, profiles, msg=None)`, `submitUpdate(userId, username, fullName, email, phone, profileId)`, `validateInput(account)` -> bool, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFound()` |
| `SuspendUserAccountPage` | 11 | `clickSuspend(userId)`, `displayConfirmation(account)`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchUserAccountPage` | 12 | `searchUserAccounts(keyword)`, `displayResults(accounts)`, `displayNoResultsMessage()` |
| `InteriorDesignerLoginPage` | 13 | `openLoginPage()`, `displayLoginForm()`, `validateInput(username, password)` -> bool, `submitLogin(username, password)`, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` |
| `CreateCompanyProfilePage` | 14 | `clickCreateCompanyProfile()`, `displayCreateForm(msg=None)`, `validateInput(companyProfile)` -> bool, `submitCompanyProfile(companyName, description, services, email, phone, address)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`. The field rules are the module function `getFieldErrors(companyProfile)`, reused by US16 |
| `ViewCompanyProfilePage` | 15 | `clickView()`, `displayCompanyProfile(profile)`, `displayErrorMessage(msg)` |
| `UpdateCompanyProfilePage` | 16 | `clickUpdate()`, `displayUpdateForm(msg=None)`, `validateInput(companyProfile)` -> bool, `submitUpdate(companyName, description, services, email, phone, address)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `DeleteCompanyProfilePage` | 17 | `clickDelete()`, `displayConfirmation(profile)`, `submitDelete(choice, companyId, revision)`, `confirmDelete(companyId, revision)`, `cancelDelete()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `RestoreCompanyProfilePage` | 17 (restore) | `submitRestore(companyId, revision)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchCompanyInformationPage` | 18 | `searchCompanyInformation(keyword)`, `displayResults(companyProfile)`, `displayNoResultsMessage()`, `displayNotFoundMessage()` |
| `InteriorDesignerLogoutPage` | 19 | `clickLogout()`, `displayLoginPage(msg)` |
| `AddCurrentIDPPage` | 20 | `clickAddCurrentIDP()`, `getAvailableCategories()`, `displayAddForm(msg=None)`, `validateInput(idp)` -> bool, `submitCurrentIDP(title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `ViewCurrentIDPPage` | 21 | `clickViewCurrentIDPs()`, `selectCurrentIDP(idpId)`, `displayCurrentIDPs(idps)`, `displayCurrentIDP(idp)`, `displayNoIDPsMessage()`, `displayNotFoundMessage()` |
| `UpdateCurrentIDPPage` | 22 | `clickUpdate(idpId)`, `displayUpdateForm(msg=None)`, `getAvailableCategories()`, `validateInput(idp)` -> bool, `submitUpdate(idpId, title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `DeleteCurrentIDPPage` | 23 | `clickDelete(idpId)`, `displayConfirmation(idp)`, `submitDelete(idpId, choice)`, `confirmDelete(idpId)`, `cancelDelete(idpId)`, `displaySuccessMessage(msg)`, `displayNotFoundMessage()` |
| `SearchCurrentIDPPage` | 24 | `searchCurrentIDPs(keyword)`, `displayResults(idps)`, `displayNoResultsMessage()` |
| `AddPastIDPPage` | 25 | `openAddPastIDPForm()`, `getAvailableCategories()`, `displayPastIDPForm(msg=None)`, `validateInput(idp)` -> bool, `submitPastIDP(title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `PastIDPListPage` | 26, 28 | `openPastIDPs()`, `displayPastIDPList(pastIDPs)`, `displayEmptyMessage(msg)`, `selectPastIDP(idpId)`, `displayPastIDPDetails(idp)`, `displayNotFoundMessage(msg)`, `clickDelete(idpId)`, `displayDeleteConfirmation(idp)`, `confirmDeletion(idpId)`, `cancelDeletion(idpId)`, `refreshPastIDPList(msg)` |
| `EditPastIDPPage` | 27 | `openEditForm(idpId)`, `getAvailableCategories()`, `displayEditForm(msg=None)`, `validateInput(idp)` -> bool, `submitUpdatedDetails(idpId, title, categoryId, description, location)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage(msg)` |
| `PastIDPSearchPage` | 29 | `validateKeyword(keyword)` -> error msg or None, `submitSearch(keyword)`, `displaySearchResults(results)`, `displayNoResultsMessage(msg)`, `displayErrorMessage(msg)` |
| `CustomerLoginPage` | 30 | `openLoginPage()`, `displayLoginForm()`, `validateInput(username, password)` -> bool, `submitLogin(username, password)`, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` |
| `SearchIDPPage` | 31 | `searchIDPs(keyword)`, `displayResults(idps)`, `displayNoResultsMessage()` |
| `ViewIDPPage` | 32 | `selectIDP(idpId, keyword, saved=False)`, `displayIDP(idp, companyProfile)`, `displayNotFoundMessage()` |
| `IDPDetailsPage` | 33 | `clickSave(idpId)`, `displaySavedState(idpId, msg)`, `displayErrorMessage(idpId, msg)` |
| `SavedListPage` | 34, 35 | `openSavedList()`, `displaySavedProjects(savedIDPs)`, `displayEmptyMessage(msg)`, `validateKeyword(keyword)` -> error msg or None, `submitSearch(keyword)`, `displaySearchResults(results)`, `displayNoResultsMessage(msg)`, `displayErrorMessage(msg)` |
| `CustomerLogoutPage` | 36 | `clickLogout()`, `displayLoginPage(msg)` |
| `ViewIDPViewStatisticsPage` | 37 | `clickViewIDPViews()`, `displayStatistics(statistics)`, `displayNoIDPsMessage(msg)` |
| `ViewIDPSaveStatisticsPage` | 38 | `clickViewIDPSaves()`, `displayStatistics(statistics)`, `displayNoIDPsMessage(msg)` |
| `PlatformManagerLoginPage` | 39 | `openLoginPage()`, `displayLoginForm()`, `validateInput(username, password)` -> bool, `submitLogin(username, password)`, `redirectToDashboard(account)`, `displayErrorMessage(msg)`, `openDashboard()` |
| `PlatformManagerLogoutPage` | 40 | `clickLogout()`, `displayLoginPage(msg)` |
| `CreateIDPCategoryPage` | 41 | `clickCreateIDPCategory()`, `displayCreateForm(msg=None)`, `validateInput(idpCategory)` -> bool, `submitIDPCategory(categoryName, description)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`. The field rules are the module function `getFieldErrors(idpCategory)`, reused by US43 |
| `ViewIDPCategoryPage` | 42 | `selectIDPCategory(categoryId)`, `displayIDPCategory(idpCategory, idps)`, `displayErrorMessage(msg)` |
| `UpdateIDPCategoryPage` | 43 | `clickUpdate(categoryId)`, `displayUpdateForm(msg=None)`, `validateInput(idpCategory)` -> bool, `submitUpdate(categoryName, description)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFoundMessage()` |
| `SuspendIDPCategoryPage` | 44 | `clickSuspend(categoryId)`, `displayConfirmation(idpCategory)`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` |
| `SearchIDPCategoryPage` | 45 | `searchIDPCategories(keyword)`, `displayResults(categories)`, `displayNoResultsMessage()` |
| `GenerateDailyReportPage` | 46 | `clickGenerateDailyReport()`, `displayReportForm(report=None, errorMessage=None, infoMessage=None)`, `validateDate(selectedDate)` -> error msg or None, `submitDate(selectedDate)`, `displayReport(report, msg=None)`, `displayErrorMessage(msg)` |
| `GenerateWeeklyReportPage` | 47 | same as US46, with `clickGenerateWeeklyReport()` |
| `GenerateMonthlyReportPage` | 48 | same as US46, with `clickGenerateMonthlyReport()` |

Pages that also use another story's controller: US5 (`CreateUserProfileController` for the tick boxes), US6 (`ViewUserProfileController`), US8 / US10 (`SearchUserProfileController` for the drop-down), US9 (`ViewUserProfileController`), US11 (`ViewUserAccountController`), US13 dashboard (`ViewCompanyProfileController`, `RestoreCompanyProfileController`), US20 / US22 / US25 / US27 (`SearchIDPCategoryController` for the drop-down), US32 (`ViewCompanyProfileController` for the designer's company), US44 (`ViewIDPCategoryController`).

The designer pages never take the owner from the URL or the form - `designerId` is always `session["userId"]`. Same for the customer pages and `customerId`.

## Shared variable names

Use these names for the same things everywhere (they come from the sequence diagrams):

| Name | Meaning |
|---|---|
| `account` | a UserAccount (None if login failed), also the one the page builds from the account form (US8, US10) |
| `profile` | a UserProfile (None if not found), also the one the page builds from the profile form (US3, US5) |
| `permissionList` | all 8 permissions, for the tick boxes |
| `permissions` | the permissions a profile has / that were ticked |
| `loggedOut` | result of `logout()` (US2, US19, US36, US40) |
| `fieldErrors` | dict of form errors, keys = the form field names (US3, US5, US8, US10, US14, US16, US20, US22, US25, US27, US41, US43) |
| `msg` | the message passed to a display...Message() method |
| `keyword` | what was typed in the search box (US7, US12, US18, US24, US29, US31, US34, US45) |
| `profiles` | list of UserProfile from a search (US7), or for the profile drop-down (US8, US10) |
| `accounts` | list of UserAccount from a search (US12) |
| `form` | the account form's UserAccount, as passed to the template (US8, US10) - not `username`, so it can't clash with the header's "Logged in as ..." names |
| `designerId` | userId of the logged-in designer - always `session["userId"]` (US13 - US29, US37, US38) |
| `customerId` | userId of the logged-in customer - always `session["userId"]` (US33 - US35) |
| `companyProfile` | the CompanyProfile the page builds from the company form (US14, US16), the search result (US18), or the designer's company on the US32 page |
| `company` | a CompanyProfile, passed to the company templates (US14 - US17) |
| `matchedFields` | names of the company fields that matched a search (on the returned `companyProfile`, US18) |
| `revision` | the company profile's revision number, sent back by the delete box / Restore button so a stale one can't delete or restore (US17) |
| `idpCategory` | an IDPCategory, also the one the page builds from the category form (US41 - US44) |
| `categories` | list of IDPCategory from a search (US45), or the Active ones for the category drop-down (US20, US22, US25, US27) |
| `idp` | an IDP (None if not found), also the one the page builds from the IDP form (US20 - US28, US32) |
| `idps` | list of IDP (US21, US24, US31, US42) |
| `pastIDPs` | the designer's past IDPs (US26) |
| `results` | list of IDP from a past IDP search (US29) or a saved list search (US34) |
| `savedIDPs` | the IDPs in the customer's saved list (US35) |
| `countView` | True if opening the IDP adds a view, False after the `?saved=1` redirect from US33's Save (US32) |
| `saved` | result of `saveIDP()` (US33) |
| `statistics` | list of IDPAnalytics, one per IDP with its `views` or `saves` (US37, US38) |
| `selectedDate` | the date the manager picked (`YYYY-MM-DD` in the box, a date object after `validateDate`) (US46 - US48) |
| `report` | an IDPAnalytics with `startDate`, `endDate` and `categories` (US46 - US48) |
| `created` / `updated` / `suspended` / `deleted` / `restored` | the bool a create / update / suspend / delete / restore controller call returns |

**Session keys:** `session["userId"]`, `session["profileId"]`, `session["username"]` (set at login, cleared at logout). Every login clears the old session first.

**Status values:** exactly `"Active"` or `"Suspended"`. "Delete" (US17, US23, US28) never removes the row, it sets `status` to `"Suspended"`. Only US17 has a restore. A suspended category hides its IDPs from customers and from the designer's current IDP pages.

**HTML form field names:** `username`, `password`, `profileName`, `description`, `permissions` (tick boxes), `keyword` (search box), `choice` (`ok` / `cancel` in the US6, US11 and US44 suspend box, `delete` / `cancel` in the US17, US23 and US28 delete box), `fullName`, `email`, `phone`, `profileId` (drop-down), `companyName`, `services`, `address`, `companyId` + `revision` (hidden, US17 delete box and Restore button), `title`, `categoryId` (drop-down), `location`, `categoryName`, `date` (US46 - US48 date box)

**Templates:**

- Sprint 1 (User Admin): `base.html` (admin pages extend this), `login.html`, `dashboard.html`, `userProfiles.html`, `createUserProfile.html`, `viewUserProfile.html`, `updateUserProfile.html`, `userAccounts.html`, `createUserAccount.html`, `viewUserAccount.html`, `updateUserAccount.html`
- Sprint 2 (designer): `interiorDesignerBase.html` (designer pages extend this - header has the US19 Log out button), `interiorDesignerLogin.html`, `interiorDesignerDashboard.html`, `createCompanyProfile.html`, `viewCompanyProfile.html`, `companyProfileDetails.html` (the reusable company card), `companyProfileNotFound.html`, `updateCompanyProfile.html`, `deleteCompanyProfile.html`, `companyProfileDeleteError.html`, `searchCompanyInformation.html`
- Sprint 2 (manager): `platformManagerBase.html` (manager pages extend this - header has the US40 Log out button), `platformManagerLogin.html`, `platformManagerDashboard.html`, `idpCategories.html`, `createIDPCategory.html`, `viewIDPCategory.html`, `updateIDPCategory.html`
- Sprint 3: `addCurrentIDP.html`, `currentIDPs.html`, `currentIDPCards.html` (reusable cards, US21 + US24), `viewCurrentIDP.html`, `idpDetailContent.html` (reusable IDP details, designer preview + customer page), `currentIDPNotFound.html`, `updateCurrentIDP.html`, `deleteCurrentIDP.html`, `searchCurrentIDPs.html`, `customerBase.html` (customer pages extend this - header has the US36 Log out button), `customerLogin.html`, `customerDashboard.html`, `customerSearchIDPs.html`, `customerViewIDP.html`, `customerIDPNotFound.html`
- Sprint 4: `addPastIDP.html`, `pastIDPs.html`, `viewPastIDP.html`, `editPastIDP.html`, `deletePastIDP.html`, `pastIDPNotFound.html`, `savedList.html`
- Sprint 5: `idpStatistics.html` (US37 + US38), `idpCategoryReport.html` (US46 - US48)

## URLs

Decorators: `/dashboard`, `/profiles...` and `/accounts...` use `loginRequired`, `/designer/...` uses `designerLoginRequired`, `/customer/...` uses `customerLoginRequired`, `/manager/...` uses `managerLoginRequired`. The login pages and the four log out routes have none.

| URL | Method | Story |
|---|---|---|
| `/` | GET | sends you to `/login` |
| `/login` | GET, POST | US1 (User Admins only - the other roles have their own login page) |
| `/dashboard` | GET | US1 (User Admin dashboard) |
| `/logout` | POST | US2 |
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
| `/designer/dashboard` | GET | US13 (shows a Restore button if the company profile was deleted) |
| `/designer/company/create` | GET, POST | US14 |
| `/designer/company` | GET | US15 |
| `/designer/company/update` | GET, POST | US16 |
| `/designer/company/delete` | GET (shows the confirmation box), POST (Delete / Cancel) | US17 |
| `/designer/company/restore` | POST (dashboard's Restore button) | US17 (restore) |
| `/designer/company/search` | GET (`?keyword=...`) | US18 |
| `/designer/logout` | POST | US19 |
| `/designer/idps/add` | GET, POST | US20 |
| `/designer/idps/current` | GET | US21 (own Active current IDPs in Active categories) |
| `/designer/idps/current/<idpId>` | GET | US21 (one IDP's preview, 404 if it's not one of yours) |
| `/designer/idps/current/<idpId>/update` | GET, POST | US22 |
| `/designer/idps/current/<idpId>/delete` | GET (shows the confirmation box), POST (Delete / Cancel) | US23 |
| `/designer/idps/current/search` | GET (`?keyword=...`) | US24 |
| `/designer/past-idps/add` | GET, POST | US25 |
| `/designer/past-idps` | GET | US26 |
| `/designer/past-idps/<idpId>` | GET | US26 (one past IDP's details) |
| `/designer/past-idps/<idpId>/edit` | GET, POST | US27 |
| `/designer/past-idps/<idpId>/delete` | GET (shows the confirmation box), POST (Delete / Cancel) | US28 |
| `/designer/past-idps/search` | GET (`?keyword=...`) | US29 |
| `/designer/idps/statistics/views` | GET | US37 |
| `/designer/idps/statistics/saves` | GET | US38 |
| `/customer/login` | GET, POST | US30 |
| `/customer/dashboard` | GET | US30 |
| `/customer/idps/search` | GET (`?keyword=...`, empty = every visible IDP) | US31 |
| `/customer/idps/<idpId>` | GET | US32 (adds one view; `?saved=1` after a US33 Save isn't counted) |
| `/customer/idps/<idpId>/save` | POST (Save button on the US32 page) | US33 (then back to `/customer/idps/<idpId>?saved=1`) |
| `/customer/saved-list` | GET | US35 |
| `/customer/saved-list/search` | GET (`?keyword=...`) | US34 |
| `/customer/logout` | POST | US36 |
| `/manager/login` | GET, POST | US39 |
| `/manager/dashboard` | GET | US39 |
| `/manager/logout` | POST | US40 |
| `/manager/categories` | GET | list page + US45 search (`/manager/categories?keyword=...`) |
| `/manager/categories/create` | GET, POST | US41 |
| `/manager/categories/<categoryId>` | GET | US42 (the category and its IDPs) |
| `/manager/categories/<categoryId>/update` | GET, POST | US43 |
| `/manager/categories/<categoryId>/suspend` | GET (shows the "Are you sure?" box), POST (OK / Cancel) | US44 |
| `/manager/reports/daily` | GET (no `?date=` = just the date box, `?date=YYYY-MM-DD` = the report) | US46 |
| `/manager/reports/weekly` | GET (same, `?date=...`) | US47 |
| `/manager/reports/monthly` | GET (same, `?date=...`) | US48 |

## Messages (copy them exactly - the test cases check them)

| Constant | Text | Story |
|---|---|---|
| `MSG_EMPTY_FIELDS` | Please enter your username and password | US1, US13, US30, US39 |
| `MSG_INVALID_LOGIN` | Invalid login details or account suspended | US1 |
| `MSG_INVALID_LOGIN` | Invalid login details or access unavailable | US13, US30, US39 |
| `MSG_LOGGED_OUT` | You have logged out successfully | US2, US19, US36, US40 |
| `MSG_SESSION_ENDED` | Your session has already ended | US2, US19, US36, US40 |
| `MSG_CREATED` | User profile created successfully | US3 |
| `MSG_NAME_TAKEN` | A user profile with this name already exists | US3 |
| `MSG_FIX_FIELDS` | Please fix the highlighted fields | US3, US5, US14, US16, US20, US22, US41, US43 |
| `MSG_NAME_LENGTH` | Profile name must be 3-50 characters | US3, US5 |
| `MSG_NO_PERMISSION` | Tick at least one permission | US3, US5 |
| `MSG_NOT_FOUND` | User profile not found | US4, US5 |
| `MSG_UPDATED` | User profile updated successfully | US5 |
| `MSG_CANNOT_UPDATE` | This user profile could not be updated - the name is already used or the profile is suspended | US5 |
| `MSG_SUSPENDED` | User profile suspended successfully | US6 |
| `MSG_CANNOT_SUSPEND` | This user profile cannot be suspended | US6 |
| `MSG_NO_RESULTS` | No user profiles found | US7 |
| `MSG_CREATED` | User account created successfully | US8 |
| `MSG_REQUIRED` | Please fill in all required fields | US8, US10 |
| `MSG_INVALID` | Invalid profile or username already exists | US8, US10 |
| `MSG_FIELD_REQUIRED` | This field is required | US8, US10, US20, US22, US25, US27 (under the empty box) |
| `MSG_NOT_FOUND` | Account not found | US9, US10 |
| `MSG_UPDATED` | User account updated successfully | US10 |
| `MSG_SUSPENDED` | User account suspended successfully | US11 |
| `MSG_CANNOT_SUSPEND` | This user account cannot be suspended | US11 |
| `MSG_NO_RESULTS` | No user accounts found | US12 |
| `MSG_CREATED` | Company profile created successfully | US14 |
| `MSG_EXISTS` | You already have a company profile | US14 |
| `MSG_NOT_FOUND` | You have not created a company profile yet | US15, US16, US17, US18 |
| `MSG_UPDATED` | Company profile updated successfully | US16 |
| `MSG_DELETED` | Company profile deleted successfully | US17 |
| `MSG_CONFIRM_AGAIN` | Please open the delete confirmation and try again | US17 |
| `MSG_FAILED` | Company profile could not be deleted. Please reopen the confirmation | US17 |
| `MSG_RESTORED` | Company profile restored successfully | US17 (restore) |
| `MSG_RESTORE_FAILED` | Company profile could not be restored. Please reopen the dashboard and try again | US17 (restore) |
| `MSG_NO_RESULTS` | No matching company information found | US18 |
| `MSG_ADDED` | Current IDP added successfully | US20 |
| `MSG_NO_CATEGORIES` | No IDP categories are available yet. Please try again later | US20, US25 |
| `MSG_FAILED` | Current IDP could not be added. Please try again | US20 |
| `MSG_TITLE_LENGTH` | Title must be 3-100 characters | US20, US22, US25, US27 |
| `MSG_CHOOSE_CATEGORY` | Choose an available category | US20, US22, US25, US27 |
| `MSG_NO_IDPS` | You have no current IDPs to display | US21, US24 |
| `MSG_NOT_FOUND` | Current IDP not found | US21, US22, US23 |
| `MSG_UPDATED` | Current IDP updated successfully | US22 |
| `MSG_DELETED` | Current IDP deleted successfully | US23 |
| `MSG_NO_RESULTS` | No matching current IDPs found | US24 |
| `MSG_ADDED` | Past IDP added successfully | US25 |
| `MSG_FIX_FIELDS` | Please fill in all required fields | US25, US27 |
| `MSG_FAILED` | Past IDP could not be added. Please try again | US25 |
| `MSG_NO_PAST_IDPS` | You have no past IDPs yet | US26 |
| `MSG_NOT_FOUND` | Past IDP not found | US26, US27, US28 |
| `MSG_UPDATED` | Past IDP updated successfully | US27 |
| `MSG_FAILED` | Past IDP could not be updated. Please try again | US27 |
| `MSG_DELETED` | Past IDP deleted successfully | US28 |
| `MSG_NO_RESULTS` | No past IDPs match your search | US29 |
| `MSG_KEYWORD_TOO_LONG` | The keyword can be at most 100 characters | US29, US34 |
| `MSG_NO_RESULTS` | No matching IDPs found | US31 |
| `MSG_NO_IDPS` | No IDPs are currently available | US31 |
| `MSG_SAVED` | IDP saved to your saved list | US33 |
| `MSG_NOT_SAVED` | This IDP is already in your saved list or is no longer available | US33 |
| `MSG_NO_RESULTS` | No saved IDPs match your search | US34 |
| `MSG_NO_SAVED` | You have not saved any IDPs yet | US35 |
| `MSG_NO_IDPS` | You don't have any active IDPs yet, so there are no views to show | US37 |
| `MSG_NO_IDPS` | You don't have any active IDPs yet, so there are no saves to show | US38 |
| `MSG_CREATED` | IDP category created successfully | US41 |
| `MSG_NAME_TAKEN` | An IDP category with this name already exists | US41 |
| `MSG_NAME_LENGTH` | Category name must be 3-50 characters | US41, US43 |
| `MSG_DESCRIPTION_LENGTH` | Description must be 500 characters or fewer | US41, US43 |
| `MSG_NOT_FOUND` | IDP category not found | US42, US43 |
| `MSG_NO_IDPS` | No IDPs are in this category yet | US42 |
| `MSG_UPDATED` | IDP category updated successfully | US43 |
| `MSG_CANNOT_UPDATE` | This IDP category could not be updated - the name is already used or the category is suspended | US43 |
| `MSG_SUSPENDED` | IDP category suspended successfully | US44 |
| `MSG_CANNOT_SUSPEND` | This IDP category cannot be suspended | US44 |
| `MSG_NO_RESULTS` | No IDP categories found | US45 |
| `MSG_INVALID_DATE` | Please choose a valid date | US46, US47, US48 |
| `MSG_FUTURE_DATE` | The date can't be in the future | US46, US47, US48 |
| `MSG_NO_ACTIVITY` | No IDPs were viewed or saved in this period | US46, US47, US48 |

Company form field errors (from `getFieldErrors(companyProfile)` in `boundary/createCompanyProfilePage.py`, US14 and US16): "This field is required", "Maximum N characters", "Company name must be 3-100 characters", "Enter a valid email address". Empty optional company fields are shown as "Not provided". The IDP forms (US20, US22, US25, US27) also use "Maximum N characters" for a field that's too long.

## Known limitations (school project)

- No CSRF tokens on the forms
- `app.secret_key` is still a placeholder (`"change-this-later"`)
- `app.py` runs with `app.run(debug=True)`
- No CI workflow - run `python -m pytest` yourself before pushing
