# US28 — Delete past IDP

> As an interior designer, I want to delete a past IDP so that it is no longer shown on the platform.

## Behaviour

- "Delete" on the past IDP's details (`clickDelete(idpId)`) loads the IDP with the controller's own loader `getPastIDP(designerId, idpId)` (`designerId = session["userId"]`). Found → `displayDeleteConfirmation(idp)`: "Delete past IDP?" - `Are you sure you want to delete <title>?`. None → "Past IDP not found" (HTTP 404). Nothing is deleted yet.
- The box posts `choice`. "Delete past IDP" (`choice == "delete"`) → `confirmDeletion(idpId)` → `deletePastIDP(designerId, idpId)`. Anything else ("Cancel") → `cancelDeletion(idpId)`, back to the details, nothing changes.
- Delete is a soft delete: the entity sets the owner's Active past IDP to `status = 'Suspended'`; the row, its details and its views / saves are kept. It disappears from the list, the details, update, search and from customers.
- Deleted → `refreshPastIDPList(MSG_DELETED)`: the past IDPs list with "Past IDP deleted successfully". Not deleted (no longer the designer's Active past IDP, e.g. already deleted) → `displayNotFoundMessage(MSG_NOT_FOUND)` "Past IDP not found" (HTTP 404) - there is no second lookup and no other error message.

## Who checks what

- **Boundary** (`PastIDPListPage`, its US28 methods): passes the session owner and the idpId from the URL on and picks the page to show - there is no typed input.
- **Control** (`DeletePastIDPController`): `getPastIDP(designerId, idpId)` (US28's own loader for the box) and `deletePastIDP(designerId, idpId)` just call the entity and return the result - no checks.
- **Entity** (`IDP`): `markPastIDPUnavailable(designerId, idpId)` updates `WHERE idpId = ? AND designerId = ? AND projectType = 'Past' AND status = 'Active'`; 0 rows → False.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `PastIDPListPage` (US28 methods) — `clickDelete(idpId)`, `displayDeleteConfirmation(idp)`, `confirmDeletion(idpId)`, `cancelDeletion(idpId)`, `refreshPastIDPList(msg)`, `displayNotFoundMessage(msg)` | `boundary/pastIDPListPage.py`, `templates/deletePastIDP.html`, `templates/pastIDPNotFound.html` |
| Control `DeletePastIDPController` — `getPastIDP(designerId, idpId): IDP`, `deletePastIDP(designerId, idpId): bool` | `control/deletePastIDPController.py` |
| Entity `IDP` — `getPastIDPDetails(designerId, idpId): IDP`, `markPastIDPUnavailable(designerId, idpId): bool` | `entity/idp.py` (table `idp`) |
| Route | GET / POST `/designer/past-idps/<idpId>/delete` (`@designerLoginRequired`) → `deletePastIDP(idpId)` in `app.py`: GET → `clickDelete`, POST `choice == "delete"` → `confirmDeletion`, otherwise `cancelDeletion` |

Messages: `MSG_DELETED` "Past IDP deleted successfully", `MSG_NOT_FOUND` "Past IDP not found".

## Files

- `US28 Delete past IDP.drawio` — every diagram, one page each
- `US28 Delete past IDP.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Confirm delete.png`
  - `4b Wireframe - Past IDP deleted.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us28_deletePastIDP.py -v
```
