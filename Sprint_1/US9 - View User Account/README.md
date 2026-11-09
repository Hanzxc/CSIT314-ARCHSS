# US9 — View user account

> As a user admin, I want to view a user account so that I can check the user’s details, group, and account status.

## Behaviour

- The User Admin clicks "View" on an account in the accounts list or the search results (US12), so the userId comes from the link.
- The page asks its controller for the account: `viewUserAccount(userId)` is one call to `UserAccount.getUserAccount(userId)` and returns the account, or None.
- Account found → the page gets the account's user profile (group name) by borrowing US4's `ViewUserProfileController.getUserProfile(account.profileId)`, then `displayAccountDetails(account, profile)` shows the username, full name, email, phone, user profile, status and created date.
- Account not found → "Account not found" and a link back to the list.
- The password is never shown, not even the hash. Suspended accounts can still be viewed. Viewing never changes any data.
- The details page has the Update (US10) and Suspend (US11) buttons. Suspend only shows for an Active account that isn't the User Admin's own.

## Who checks what

- **Boundary** (`ViewUserAccountPage`): takes the userId from the link, decides what to show (`[account != None]` / `[account == None]`) and borrows US4's controller for the profile. There is no typed input.
- **Control** (`ViewUserAccountController`): just calls the entity and returns the account - one call, one return, no profile lookup.
- **Entity** (`UserAccount`): reads the row and returns a `UserAccount`, or None.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewUserAccountPage` — `clickView(userId)`, `displayAccountDetails(account, profile)`, `displayErrorMessage(msg)` | `boundary/viewUserAccountPage.py`, `templates/viewUserAccount.html` |
| Control `ViewUserAccountController` — `viewUserAccount(userId): UserAccount` | `control/viewUserAccountController.py` |
| Borrowed control `«control» (from US4) ViewUserProfileController` — `getUserProfile(profileId): UserProfile` | `control/viewUserProfileController.py` |
| Entity `UserAccount` — `getUserAccount(userId): UserAccount` | `entity/userAccount.py` |
| Entity `UserProfile` — `getUserProfile(profileId): UserProfile` | `entity/userProfile.py` |
| Route | GET `/accounts/<userId>` → `viewUserAccount()` in `app.py` |

Message: `MSG_NOT_FOUND` "Account not found".

## Files

- `US9 View user account.drawio` — every diagram, one page each
- `US9 View user account.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - User account details.png`
  - `4b Wireframe - Account not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us9_viewUserAccount.py -v
```
