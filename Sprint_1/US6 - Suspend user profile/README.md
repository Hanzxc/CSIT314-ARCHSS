# US6 — Suspend user profile

> As a user admin, I want to suspend a user profile so that users in that group cannot log in.

## Behaviour

- "Suspend" is shown on the profile details page (US4) for an Active profile.
- Clicking it (`clickSuspend(profileId)`) gets the profile by borrowing US4's `ViewUserProfileController.getUserProfile(profileId)`.
  - Found → `displayConfirmation(profile)` shows a box naming the group and saying its users won't be able to log in.
  - Not found → "This user profile cannot be suspended".
- "Cancel" closes the box and nothing changes (`cancelSuspend()` → `closeConfirmation()`).
- "Suspend" in the box (`confirmSuspend()`): the page first checks it isn't the User Admin's own group (`[profileId != session profileId]`); if it is → "This user profile cannot be suspended" and the controller is never called.
- Otherwise `suspendUserProfile(profileId)` changes the status to Suspended and the details page shows "User profile suspended successfully". A profile that isn't Active any more (already suspended, or gone) → "This user profile cannot be suspended".
- Nothing is deleted - the profile and its user accounts are kept. Every login page uses `UserAccount.verifyCredentials()`, which only accepts an account whose profile is Active, so the group's users can no longer log in. Other groups are not affected.

## Who checks what

- **Boundary** (`SuspendUserProfilePage`): checks the input - the User Admin can't suspend their own group (`profileId != session profileId`) - and borrows US4's controller for the profile in the box.
- **Control** (`SuspendUserProfileController`): just calls `UserProfile.suspendUserProfile(profileId)` and returns the result - no checks.
- **Entity** (`UserProfile`): only changes an Active row to Suspended (`... WHERE profileId = ? AND status = 'Active'`); already suspended or no such id gives back False. `UserAccount` is not changed.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SuspendUserProfilePage` — `clickSuspend(profileId)`, `displayConfirmation(profile)`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/suspendUserProfilePage.py`, confirmation box in `templates/viewUserProfile.html` |
| Control `SuspendUserProfileController` — `suspendUserProfile(profileId): boolean` | `control/suspendUserProfileController.py` |
| Borrowed control `«control» (from US4) ViewUserProfileController` — `getUserProfile(profileId): UserProfile` | `control/viewUserProfileController.py` |
| Entity `UserProfile` — `getUserProfile(profileId)`, `suspendUserProfile(profileId)` | `entity/userProfile.py` (table `user_profile`) |
| Route | GET / POST `/profiles/<profileId>/suspend` → `suspendUserProfile()` in `app.py` (POST `choice=cancel` → `cancelSuspend()`) |

Messages: `MSG_SUSPENDED` "User profile suspended successfully", `MSG_CANNOT_SUSPEND` "This user profile cannot be suspended".

## Files

- `US6 Suspend user profile.drawio` — every diagram, one page each
- `US6 Suspend user profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Suspend button.png`
  - `4b Wireframe - Confirm suspend.png`
  - `4c Wireframe - Profile suspended.png`
  - `4d Wireframe - Blocked login.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us6_suspendUserProfile.py -v
```
