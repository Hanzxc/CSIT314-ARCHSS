# US7 — Search user profiles

> As a user admin, I want to search for user profiles so that I can find the group I need to manage.

## Behaviour

- The User Profiles page (`/profiles`) has a search box and a "Search" button. The same page is the profile list: an empty search shows every profile.
- The search looks at each profile's name and description. Capitals don't matter ("dESIGNER" finds "Interior Designer").
- The page trims the keyword first, so "  Customer  " works like "Customer" and a keyword of just spaces counts as empty.
- Each result shows the profile name, description, status and a "View" link (US4 View user profile).
- Suspended profiles are included in the results, with their status.
- Nothing matches → "No user profiles found", and the User Admin can try another keyword.
- Searching never changes any data.
- US8 Create user account and US10 Update user account borrow this story's `SearchUserProfileController.searchUserProfiles("")` for their profile drop-down.

## Who checks what

- **Boundary** (`SearchUserProfilePage`): trims the keyword, then shows the results or the "no results" message.
- **Control** (`SearchUserProfileController`): just calls the entity and returns the list - no checks.
- **Entity** (`UserProfile`): searches the name and description (capitals ignored) and returns the matching profiles. It doesn't trim or change anything.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `SearchUserProfilePage` — `searchUserProfiles(keyword)`, `displayResults(profiles)`, `displayNoResultsMessage()` | `boundary/searchUserProfilePage.py`, `templates/userProfiles.html` |
| Control `SearchUserProfileController` — `searchUserProfiles(keyword): List<UserProfile>` | `control/searchUserProfileController.py` |
| Entity `UserProfile` — `searchUserProfiles(keyword): List<UserProfile>` | `entity/userProfile.py` |
| Route | GET `/profiles?keyword=...` → `profiles()` in `app.py` |

## Files

- `US7 Search user profiles.drawio` — every diagram, one page each
- `US7 Search user profiles.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Search results.png`
  - `4b Wireframe - No results.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us7_searchUserProfiles.py -v
```
