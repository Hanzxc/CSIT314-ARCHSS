# US12 — Search user account

> As a user admin, I want to search for user accounts so that I can find the user I need to manage.

## Behaviour

- The User Accounts page (`/accounts`) has a search box and a "Search" button. The same page is the account list: an empty search shows every account.
- The search looks at each account's username, full name and email. Capitals don't matter ("CHLOE" finds "Chloe Ng").
- The page trims the keyword first, so "  chloe  " works like "chloe" and a keyword of just spaces counts as empty.
- Each result shows the username, full name, email, status and a "View" link (US9 View user account).
- Suspended accounts are included in the results, with their status.
- Nothing matches → "No user accounts found", and the User Admin can try another keyword.
- Searching never changes any data.

## Who checks what

- **Boundary** (`SearchUserAccountPage`): trims the keyword, then shows the results or the "no results" message.
- **Control** (`SearchUserAccountController`): just calls the entity and returns the list - no checks.
- **Entity** (`UserAccount`): searches the username, full name and email (capitals ignored) and returns the matching accounts. It doesn't trim or change anything.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SearchUserAccountPage` — `searchUserAccounts(keyword)`, `displayResults(accounts)`, `displayNoResultsMessage()` | `boundary/searchUserAccountPage.py`, `templates/userAccounts.html` |
| Control `SearchUserAccountController` — `searchUserAccounts(keyword): List<UserAccount>` | `control/searchUserAccountController.py` |
| Entity `UserAccount` — `searchUserAccounts(keyword): List<UserAccount>` | `entity/userAccount.py` |
| Route | GET `/accounts?keyword=...` → `accounts()` in `app.py` |

## Files

- `US12 Search user account.drawio` — every diagram, one page each
- `US12 Search user account.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Search results.png`
  - `4b Wireframe - No results.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us12_searchUserAccounts.py -v
```
