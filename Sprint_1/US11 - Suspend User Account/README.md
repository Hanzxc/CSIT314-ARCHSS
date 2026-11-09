# US11 — Suspend user account

> As a user admin, I want to suspend a user account so that the user cannot log in.

## Behaviour

- "Suspend" is shown on the account details page (US9) only for an Active account that isn't the User Admin's own.
- Clicking it gets the account by borrowing US9's `ViewUserAccountController.viewUserAccount(userId)`.
  - Found → `displayConfirmation(account)` shows a box naming the account (e.g. "cust001 (Chloe Ng)") and saying the user won't be able to log in.
  - Not found → "This user account cannot be suspended".
- "Cancel" closes the box and nothing changes (`cancelSuspend()` → `closeConfirmation()`).
- "Suspend" in the box (`confirmSuspend()`): the page first checks it isn't the User Admin's own account (`[userId != session userId]`); if it is → "This user account cannot be suspended" and the controller is never called.
- Otherwise the status changes to Suspended and the details page shows "User account suspended successfully". An account that isn't Active any more (already suspended, or gone) → "This user account cannot be suspended".
- Nothing is deleted. Log in (US1) only lets Active accounts in, so the suspended user gets "Invalid login details or account suspended". Other users are not affected.

## Who checks what

- **Boundary** (`SuspendUserAccountPage`): checks the input - the User Admin can't suspend their own account (`userId != session userId`) - and borrows US9's controller for the account in the box.
- **Control** (`SuspendUserAccountController`): just calls `UserAccount.suspendUserAccount(userId)` and returns the result - no checks.
- **Entity** (`UserAccount`): only changes an Active row to Suspended (`... WHERE userId = ? AND status = 'Active'`); already suspended or no such id gives back False.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SuspendUserAccountPage` — `clickSuspend(userId)`, `displayConfirmation(account)`, `confirmSuspend()`, `cancelSuspend()`, `closeConfirmation()`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/suspendUserAccountPage.py`, confirmation box in `templates/viewUserAccount.html` |
| Control `SuspendUserAccountController` — `suspendUserAccount(userId): boolean` | `control/suspendUserAccountController.py` |
| Borrowed control `«control» (from US9) ViewUserAccountController` — `viewUserAccount(userId): UserAccount` | `control/viewUserAccountController.py` |
| Entity `UserAccount` — `getUserAccount(userId)`, `suspendUserAccount(userId)` | `entity/userAccount.py` |
| Route | GET / POST `/accounts/<userId>/suspend` → `suspendUserAccount()` in `app.py` (POST `choice=cancel` → `cancelSuspend()`) |

Messages: `MSG_SUSPENDED` "User account suspended successfully", `MSG_CANNOT_SUSPEND` "This user account cannot be suspended".

## Files

- `US11 Suspend user account.drawio` — every diagram, one page each
- `US11 Suspend user account.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Suspend button.png`
  - `4b Wireframe - Confirm suspend.png`
  - `4c Wireframe - Account suspended.png`
  - `4d Wireframe - Blocked login.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us11_suspendUserAccount.py -v
```
