# US26 — View past IDPs

> As an interior designer, I want to view my past IDPs so that I can check how they look to customers.

## Behaviour

- "Past IDPs" in the side menu or "View past IDPs" on the dashboard (`openPastIDPs()`) calls `getPastIDPs(designerId)` with `designerId = session["userId"]`.
- Some past IDPs → `displayPastIDPList(pastIDPs)`: the designer's own Active past IDPs, newest first, each with its category, location and "View". None → `displayEmptyMessage(MSG_NO_PAST_IDPS)` "You have no past IDPs yet".
- "View" (`selectPastIDP(idpId)`) calls `getPastIDPDetails(designerId, idpId)`. Found → `displayPastIDPDetails(idp)`: title, category, location and description as customers see them, with Update (US27), Delete (US28) and "Back to past IDPs". None (missing, someone else's, Current or deleted) → `displayNotFoundMessage(MSG_NOT_FOUND)` "Past IDP not found" (HTTP 404), no details.
- Viewing changes nothing and isn't counted as a customer view (US32, US37). The list page also has "+ Add past IDP" (US25) and the search bar (US29).

## Who checks what

- **Boundary** (`PastIDPListPage`): takes the designer from the session (and idpId from the URL) and picks what to show - there is no typed input.
- **Control** (`ViewPastIDPController`): `getPastIDPs(designerId)` and `getPastIDPDetails(designerId, idpId)` just call the entity and return the result - no checks.
- **Entity** (`IDP`): `findPastIDPsByDesignerId(designerId)` and `getPastIDPDetails(designerId, idpId)` only return the owner's rows with `projectType = 'Past' AND status = 'Active'`, with the category name joined.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `PastIDPListPage` — `openPastIDPs()`, `displayPastIDPList(pastIDPs)`, `displayEmptyMessage(msg)`, `selectPastIDP(idpId)`, `displayPastIDPDetails(idp)`, `displayNotFoundMessage(msg)` | `boundary/pastIDPListPage.py`, `templates/pastIDPs.html`, `templates/viewPastIDP.html`, `templates/pastIDPNotFound.html` |
| Control `ViewPastIDPController` — `getPastIDPs(designerId): list`, `getPastIDPDetails(designerId, idpId): IDP` | `control/viewPastIDPController.py` |
| Entity `IDP` — `findPastIDPsByDesignerId(designerId): list`, `getPastIDPDetails(designerId, idpId): IDP` | `entity/idp.py` (table `idp`) |
| Route | GET `/designer/past-idps` → `pastIDPs()` and GET `/designer/past-idps/<idpId>` → `viewPastIDP(idpId)` in `app.py` (both `@designerLoginRequired`) |

Messages: `MSG_NO_PAST_IDPS` "You have no past IDPs yet", `MSG_NOT_FOUND` "Past IDP not found".

## Files

- `US26 View past IDPs.drawio` — every diagram, one page each
- `US26 View past IDPs.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Past IDPs list.png`
  - `4b Wireframe - Past IDP details.png`
  - `4c Wireframe - No past IDPs yet.png`
  - `4d Wireframe - Past IDP not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us26_viewPastIDPs.py -v
```
