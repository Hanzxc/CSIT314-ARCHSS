# US23 — Delete current IDP

> As an interior designer, I want to delete a current IDP so that it is no longer shown on the platform.

## Behaviour

- "Delete current IDP" on the preview (`clickDelete(idpId)`) loads the IDP with the controller's own loader `getCurrentIDP(designerId, idpId)` (`designerId = session["userId"]`).
- Found → `displayConfirmation(idp)`: a box "Are you sure you want to delete <title>?" with Delete and Cancel - nothing is deleted yet. None → "Current IDP not found" (HTTP 404, `displayNotFoundMessage()`).
- The box posts `choice` (`submitDelete(idpId, choice)`): `"delete"` → `confirmDelete(idpId)` → `deleteCurrentIDP(designerId, idpId)` → `IDP.suspendCurrentIDP(designerId, idpId)`; `"cancel"` → `cancelDelete(idpId)` → back to the preview, nothing changes.
- Delete is a soft delete: the owner's Active Current IDP (in an Active category) gets status Suspended and its details are kept. It then no longer shows in the list, preview, update, search or to customers.
- Deleted → Current IDPs with "Current IDP deleted successfully". Not deleted (already deleted, or its category suspended) → "Current IDP not found" (HTTP 404).
- There is no confirmation token, nothing is kept in the session and the details aren't compared - the entity's check is enough. There is no restore in this story.

## Who checks what

- **Boundary** (`DeleteCurrentIDPPage`): takes the owner from the session and the idpId from the URL, picks the branch from `choice`. No typed input to check.
- **Control** (`DeleteCurrentIDPController`): `getCurrentIDP(designerId, idpId)` (US23's own loader for the box) and `deleteCurrentIDP(designerId, idpId)` just call the entity and return the result - no checks.
- **Entity** (`IDP`): `suspendCurrentIDP(designerId, idpId)` sets `status = 'Suspended'` `WHERE idpId = ? AND designerId = ? AND projectType = 'Current' AND status = 'Active'` and the category is Active; 0 rows → False.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `DeleteCurrentIDPPage` — `clickDelete(idpId)`, `displayConfirmation(idp)`, `submitDelete(idpId, choice)`, `confirmDelete(idpId)`, `cancelDelete(idpId)`, `displaySuccessMessage(msg)`, `displayNotFoundMessage()` | `boundary/deleteCurrentIDPPage.py`, `templates/deleteCurrentIDP.html`, `templates/currentIDPNotFound.html` |
| Control `DeleteCurrentIDPController` — `getCurrentIDP(designerId, idpId): IDP \| None`, `deleteCurrentIDP(designerId, idpId): bool` | `control/deleteCurrentIDPController.py` |
| Entity `IDP` — `getCurrentIDP(designerId, idpId): IDP \| None`, `suspendCurrentIDP(designerId, idpId): bool` | `entity/idp.py` (table `idp`) |
| Route | GET / POST `/designer/idps/current/<idpId>/delete` (`@designerLoginRequired`) → `deleteCurrentIDP(idpId)` in `app.py`; POST passes `choice` |

Messages: `MSG_DELETED` "Current IDP deleted successfully", `MSG_NOT_FOUND` "Current IDP not found".

## Files

- `US23 Delete current IDP.drawio` — every diagram, one page each
- `US23 Delete current IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Delete action.png`
  - `4b Wireframe - Delete confirmation.png`
  - `4c Wireframe - Deletion result.png`
  - `4d Wireframe - Deleted IDP not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us23_deleteCurrentIDP.py -v
```
