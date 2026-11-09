# US5 — Update user profile

> As a user admin, I want to update a user profile so that the group’s details and permissions stay up to date.

## Behaviour

- "Update" on the profile details page (`clickUpdate(profileId)`) loads the profile with US5's own `getUserProfile(profileId)`.
  - Not found (e.g. a wrong link) → `displayNotFound()` shows "User profile not found".
  - Found → the page gets the permission tick boxes by borrowing US3's `CreateUserProfileController.getAllPermissions()` and shows the form filled in with the current details (`displayUpdateForm(profile, permissionList)`).
- "Cancel" is a plain link back to the details page - nothing is sent or changed.
- On "Save changes" (`submitUpdate(profileName, description, permissions)`) the page trims the spaces, builds `profile = UserProfile(profileId, profileName, description, permissions)` and checks it with `validateInput(profile)` (same rules as US3: name 3-50 characters, at least one permission).
- Bad input → "Please fix the highlighted fields", the fields are highlighted, what was typed stays in the form, and the controller is never called.
- Otherwise `updateUserProfile(profile)`. The entity only changes a profile that is still Active and whose new name isn't used by a different profile (keeping its own name is fine). If it refuses → "This user profile could not be updated - the name is already used or the profile is suspended" and nothing is saved.
- Saved → the details page shows "User profile updated successfully". The status is never changed here (suspending is US6), and every account in the group gets the new permissions.

## Who checks what

- **Boundary** (`UpdateUserProfilePage`): checks all the input, trims spaces, builds the `UserProfile` object and passes it on; shows "User profile not found" when the loader returns None.
- **Control** (`UpdateUserProfileController`): `getUserProfile(profileId)` (US5's own loader) and `updateUserProfile(profile)` just call the entity and return the result - no checks. The tick-box list is US3's form data, so the page borrows US3's controller for it.
- **Entity** (`UserProfile`): checks the database - only an Active row is changed, and the new name must not be used by another profile (`isProfileNameTaken(profileName, profileId)`) - then saves the name, description and permissions.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `UpdateUserProfilePage` — `clickUpdate(profileId)`, `displayUpdateForm(profile, permissionList)`, `submitUpdate(profileName, description, permissions)`, `validateInput(profile): boolean`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)`, `displayNotFound()` | `boundary/updateUserProfilePage.py`, `templates/updateUserProfile.html` |
| Control `UpdateUserProfileController` — `getUserProfile(profileId): UserProfile`, `updateUserProfile(profile): boolean` | `control/updateUserProfileController.py` |
| Borrowed control `«control» (from US3) CreateUserProfileController` — `getAllPermissions(): List<String>` | `control/createUserProfileController.py` |
| Entity `UserProfile` — `getUserProfile(profileId)`, `getAllPermissions()`, `isProfileNameTaken(profileName, profileId)`, `updateUserProfile(profile)` | `entity/userProfile.py` (table `user_profile`) |
| Route | GET / POST `/profiles/<profileId>/update` → `updateUserProfile()` in `app.py` |

Messages: `MSG_UPDATED` "User profile updated successfully", `MSG_CANNOT_UPDATE` "This user profile could not be updated - the name is already used or the profile is suspended", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NAME_LENGTH` "Profile name must be 3-50 characters", `MSG_NO_PERMISSION` "Tick at least one permission", `MSG_NOT_FOUND` "User profile not found".

## Files

- `US5 Update user profile.drawio` — every diagram, one page each
- `US5 Update user profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - User profile details.png`
  - `4b Wireframe - Update user profile form.png`
  - `4c Wireframe - Update form error.png`
  - `4d Wireframe - Profile updated.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us5_updateUserProfile.py -v
```
