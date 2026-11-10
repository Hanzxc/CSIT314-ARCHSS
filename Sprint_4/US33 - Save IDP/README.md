# US33 — Save IDP

> As a customer, I want to save an IDP so that I can look at it again later.

## Behaviour

- The Save IDP button is on the US32 View IDP page (`ViewIDPPage`) and is always shown (the button has no "Saved" state). Clicking it posts to `/customer/idps/<idpId>/save` (wireframe 4a).
- `clickSave(idpId)` → `saveIDP(customerId, idpId)` (controller, `customerId = session["userId"]`) → `SavedIDP.createSavedRecord(customerId, idpId)` → `saved`.
- `createSavedRecord()` only inserts the `saved_idp` row when the IDP is Active and its category is Active, and `UNIQUE(customerId, idpId)` stops a duplicate. It returns True when a row was added, otherwise False. Nothing is checked before this call.
- `[saved == True]` → `displaySavedState(idpId, MSG_SAVED)`: "IDP saved to your saved list" (wireframe 4b).
- `[saved == False]` → `displayErrorMessage(idpId, MSG_NOT_SAVED)`: "This IDP is already in your saved list or is no longer available" (wireframe 4c). Nothing is added.
- Both results send an HTTP 302 to `/customer/idps/<idpId>?saved=1`. US32 shows the IDP again without counting that reload as a view, so the view statistics (US37) only count real visits.
- Current and Past IDPs can both be saved. A saved IDP is listed in Saved IDPs (US35) and can be searched there (US34). There is no remove / unsave.

## Who checks what

- **Boundary** (`IDPDetailsPage`): there is no typed input - it takes `idpId` from the URL and `customerId` from the session, calls the controller and shows one of the two messages.
- **Control** (`SaveIDPController`): `saveIDP(customerId, idpId)` just calls `SavedIDP().createSavedRecord(customerId, idpId)` and returns `saved` - no checks.
- **Entity** (`SavedIDP`): refuses a duplicate (UNIQUE customerId + idpId) and an IDP customers can't see (Suspended IDP or Suspended category), otherwise inserts the row and commits.
- Precondition: logged in as a Customer (UC30). `customerLoginRequired` in `app.py` only sends someone with no session to `/customer/login`. The role isn't checked again (no `CustomerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `IDPDetailsPage` — attribute `saveIDPController`; `clickSave(idpId)`, `displaySavedState(idpId, msg)`, `displayErrorMessage(idpId, msg)` | `boundary/idpDetailsPage.py` (the button is in `templates/customerViewIDP.html`) |
| Control `SaveIDPController` — `saveIDP(customerId, idpId): bool` | `control/saveIDPController.py` |
| Entity `SavedIDP` — attributes `savedId`, `customerId`, `idpId`, `savedDate`; `createSavedRecord(customerId, idpId): bool` | `entity/savedIDP.py` (table `saved_idp`) |
| Route | POST `/customer/idps/<idpId>/save` (`@customerLoginRequired`) → `saveIDP(idpId)` in `app.py`; it redirects to GET `/customer/idps/<idpId>?saved=1` (US32) |

Messages: `MSG_SAVED` "IDP saved to your saved list", `MSG_NOT_SAVED` "This IDP is already in your saved list or is no longer available".

## Files

- `US33 Save IDP.drawio` — every diagram, one page each
- `US33 Save IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Save button.png`
  - `4b Wireframe - IDP saved.png`
  - `4c Wireframe - Already saved.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us33_saveIDP.py -v
```
