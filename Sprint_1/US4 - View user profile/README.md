# US4 — View user profile

> As a user admin, I want to view a user profile so that I can check the group’s details and what its users can do.

## Behaviour

- "View" next to a profile on the User Profiles list (`selectUserProfile(profileId)`) gets the profile with `getUserProfile(profileId)`.
- Found → `displayUserProfile(profile)` shows the name, description, status (Active or Suspended) and every permission. Suspended profiles can still be viewed.
- Not found (e.g. a wrong link) → `displayErrorMessage("User profile not found")`. No error page.
- Viewing never changes any data. The details page links to Update (US5) and Suspend (US6).
- US6 and US9 borrow `ViewUserProfileController.getUserProfile()` when they need to show a profile.

## Who checks what

- **Boundary** (`ViewUserProfilePage`): passes the selected id on and shows the details or the not-found message.
- **Control** (`ViewUserProfileController`): just calls `UserProfile.getUserProfile(profileId)` and returns the result - no checks.
- **Entity** (`UserProfile`): reads the row; returns None if there is no profile with this id.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewUserProfilePage` — `selectUserProfile(profileId)`, `displayUserProfile(profile)`, `displayErrorMessage(msg)` | `boundary/viewUserProfilePage.py`, `templates/viewUserProfile.html` |
| Control `ViewUserProfileController` — `getUserProfile(profileId): UserProfile` | `control/viewUserProfileController.py` |
| Entity `UserProfile` — `getUserProfile(profileId): UserProfile` | `entity/userProfile.py` (table `user_profile`) |
| Route | GET `/profiles/<profileId>` → `viewUserProfile()` in `app.py` |

Messages: `MSG_NOT_FOUND` "User profile not found".

## Files

- `US4 View user profile.drawio` — every diagram, one page each
- `US4 View user profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - User Profiles page.png`
  - `4b Wireframe - User profile details.png`
  - `4c Wireframe - Profile not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us4_viewUserProfile.py -v
```
