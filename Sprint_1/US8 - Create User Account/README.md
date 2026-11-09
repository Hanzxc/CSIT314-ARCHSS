# US8 — Create user account

> As a user admin, I want to create a user account so that a new user can join the system.

## Behaviour

- "Create user account" on the User Accounts page opens the create form. The page first gets every user profile for the drop-down by borrowing US7's `SearchUserProfileController.searchUserProfiles("")`, then shows the form.
- The form has username, password, full name, email, phone and user profile. Username, password, full name and user profile are required; email and phone are optional.
- On "Create" the page trims the input (not the password), builds `account = UserAccount(username, password, fullName, email, phone, profileId)` and checks it with `validateInput(account)`.
- A required field is missing → "Please fill in all required fields", what was typed stays in the form, and the controller is never called.
- The chosen profile is suspended (or doesn't exist) or the username is already used (capitals ignored) → "Invalid profile or username already exists" and nothing is saved.
- Otherwise the account is saved as Active with a hashed password, and the User Accounts list shows "User account created successfully". The new user can log in straight away (US1).
- When the form is shown again with a message, the drop-down is loaded again the same way.

## Who checks what

- **Boundary** (`CreateUserAccountPage`): checks all the input (required fields), trims spaces (not the password), builds the `UserAccount` object and passes it on.
- **Control** (`CreateUserAccountController`): just calls `UserAccount.createUserAccount(account)` and returns the result - no checks.
- **Entity** (`UserAccount`): checks the database - the chosen profile must exist and be Active, the username must not be taken - then inserts the row (status Active, password hashed).
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `CreateUserAccountPage` — `clickCreateUserAccount()`, `displayCreateForm(profiles)`, `submitCreateAccount(username, password, fullName, email, phone, profileId)`, `validateInput(account)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/createUserAccountPage.py`, `templates/createUserAccount.html` |
| Control `CreateUserAccountController` — `createUserAccount(account): boolean` | `control/createUserAccountController.py` |
| Borrowed control `«control» (from US7) SearchUserProfileController` — `searchUserProfiles(keyword)` | `control/searchUserProfileController.py` |
| Entity `UserAccount` — `isUsernameTaken(username, userId=None)`, `createUserAccount(account)` | `entity/userAccount.py` |
| Entity `UserProfile` — `getUserProfile(profileId)`, `isActive()`, `searchUserProfiles(keyword)` | `entity/userProfile.py` |
| Route | GET / POST `/accounts/create` → `createUserAccount()` in `app.py` |

Messages: `MSG_CREATED` "User account created successfully", `MSG_REQUIRED` "Please fill in all required fields", `MSG_INVALID` "Invalid profile or username already exists".

## Files

- `US8 Create user account.drawio` — every diagram, one page each
- `US8 Create user account.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Create user account form.png`
  - `4b Wireframe - Create form errors.png`
  - `4c Wireframe - Account created.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us8_createUserAccount.py -v
```
