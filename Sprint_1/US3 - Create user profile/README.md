# US3 — Create user profile

> As a user admin, I want to create a user profile so that I can set up a user group and choose what its users can do.

## Behaviour

- "Create user profile" on the User Profiles page (`clickCreateUserProfile()`) gets the platform's fixed permission list with `getAllPermissions()` and shows the form (`displayCreateForm(permissionList)`): profile name, description and one tick box per permission.
- "Cancel" is a plain link back to the User Profiles list - nothing is sent or saved.
- On "Create" (`submitUserProfile(profileName, description, permissions)`) the page trims the spaces, builds `profile = UserProfile(profileName, description, permissions)` and checks it with `validateInput(profile)`: the name must be 3-50 characters and at least one permission must be ticked.
- Bad input → "Please fix the highlighted fields", the bad fields are highlighted ("Profile name must be 3-50 characters", "Tick at least one permission"), what was typed stays in the form, and the controller is never called.
- Otherwise `createUserProfile(profile)` → the entity refuses a name another profile already uses (capitals ignored, so "cUSTOMER" counts as "Customer") → "A user profile with this name already exists".
- Saved → the new profile is Active and the User Profiles list shows "User profile created successfully". The description is optional.

## Who checks what

- **Boundary** (`CreateUserProfilePage`): checks all the input (name length, at least one permission), trims spaces, builds the `UserProfile` object and passes it on.
- **Control** (`CreateUserProfileController`): `getAllPermissions()` for the tick boxes (US3's own form data) and `createUserProfile(profile)`; both just call the entity and return the result - no checks.
- **Entity** (`UserProfile`): checks the database - the name must not be used by another profile (`isProfileNameTaken(profileName)`) - then inserts the row as Active.
- Precondition: logged in as a User Admin (UC1). `loginRequired` in `app.py` only sends someone with no session to `/login`; the use case doesn't check the role again.

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `CreateUserProfilePage` — `clickCreateUserProfile()`, `displayCreateForm(permissionList)`, `submitUserProfile(profileName, description, permissions)`, `validateInput(profile): boolean`, `displaySuccessMessage(msg)`, `displayErrorMessage(msg)` | `boundary/createUserProfilePage.py`, `templates/createUserProfile.html` |
| Control `CreateUserProfileController` — `getAllPermissions(): List<String>`, `createUserProfile(profile): boolean` | `control/createUserProfileController.py` |
| Entity `UserProfile` — `getAllPermissions()`, `isProfileNameTaken(profileName)`, `createUserProfile(profile)` | `entity/userProfile.py` (table `user_profile`) |
| Route | GET / POST `/profiles/create` → `createUserProfile()` in `app.py` |

Messages: `MSG_CREATED` "User profile created successfully", `MSG_NAME_TAKEN` "A user profile with this name already exists", `MSG_FIX_FIELDS` "Please fix the highlighted fields", `MSG_NAME_LENGTH` "Profile name must be 3-50 characters", `MSG_NO_PERMISSION` "Tick at least one permission".

## Files

- `US3 Create user profile.drawio` — every diagram, one page each
- `US3 Create user profile.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - User Profiles page.png`
  - `4b Wireframe - Create user profile form.png`
  - `4c Wireframe - Create form errors.png`
  - `4d Wireframe - Profile created.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us3_createUserProfile.py -v
```
