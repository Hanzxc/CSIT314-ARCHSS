# US10 — Update user account

> As a user admin, I want to update a user account so that the user’s details and group are correct.

## Behaviour

- "Update" on the account details page loads the account with US10's own `getUserAccount(userId)` (team decision: update stories keep their own load method).
  - Not found → `displayNotFound()` shows "Account not found".
  - Found → the page gets every user profile for the drop-down by borrowing US7's `SearchUserProfileController.searchUserProfiles("")`, then `displayUpdateForm(account, profiles)` shows the form filled in with the current details.
- The User Admin can change the username, full name, email, phone and user profile. Username, full name and user profile are required; email and phone are optional. The password, status and created date are never changed here.
- On "Save" the page trims the input, builds `account = UserAccount(userId, username, fullName, email, phone, profileId)` and checks it with `validateInput(account)`.
- A required field is missing → "Please fill in all required fields", what was typed stays in the form, and the controller is never called.
- The chosen profile is suspended, another account already has the username, or the account itself is suspended → "Invalid profile or username already exists" and nothing is saved. Keeping the account's own username is fine.
- Otherwise the changes are saved and the details page shows "User account updated successfully".
- When the form is shown again with a message, the drop-down is loaded again the same way.

## Who checks what

- **Boundary** (`UpdateUserAccountPage`): checks all the input (required fields), trims spaces, builds the `UserAccount` object and passes it on.
- **Control** (`UpdateUserAccountController`): `getUserAccount(userId)` and `updateUserAccount(account)` each just call the entity and return the result - no checks.
- **Entity** (`UserAccount`): checks the database - only an Active account is changed, the chosen profile must be Active and no other account may have the username (`isUsernameTaken(username, userId)`) - then updates the row.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `UpdateUserAccountPage` — `clickUpdate(userId)`, `displayUpdateForm(account, profiles)`, `displayNotFound()`, `submitUpdate(userId, username, fullName, email, phone, profileId)`, `validateInput(account)`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/updateUserAccountPage.py`, `templates/updateUserAccount.html` |
| Control `UpdateUserAccountController` — `getUserAccount(userId): UserAccount`, `updateUserAccount(account): boolean` | `control/updateUserAccountController.py` |
| Borrowed control `«control» (from US7) SearchUserProfileController` — `searchUserProfiles(keyword)` | `control/searchUserProfileController.py` |
| Entity `UserAccount` — `getUserAccount(userId)`, `isUsernameTaken(username, userId=None)`, `updateUserAccount(account)` | `entity/userAccount.py` |
| Entity `UserProfile` — `getUserProfile(profileId)`, `isActive()`, `searchUserProfiles(keyword)` | `entity/userProfile.py` |
| Route | GET / POST `/accounts/<userId>/update` → `updateUserAccount()` in `app.py` |

Messages: `MSG_UPDATED` "User account updated successfully", `MSG_REQUIRED` "Please fill in all required fields", `MSG_INVALID` "Invalid profile or username already exists", `MSG_NOT_FOUND` "Account not found".

## Files

- `US10 Update user account.drawio` — every diagram, one page each
- `US10 Update user account.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Update user account form.png`
  - `4b Wireframe - Update form error.png`
  - `4c Wireframe - Account updated.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us10_updateUserAccount.py -v
```
