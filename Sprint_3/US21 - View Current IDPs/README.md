# US21 — View current IDPs

> As an interior designer, I want to view my current IDPs so that I can check how they look to customers.

## Behaviour

- "View current IDPs" on the dashboard (`clickViewCurrentIDPs()`) calls `viewCurrentIDPs(designerId)` with `designerId = session["userId"]`, which returns `IDP().getCurrentIDPs(designerId)`.
- The list only has the designer's own Active Current IDPs whose category is Active, newest first, each with a "View" link (`displayCurrentIDPs(idps)`). None → "You have no current IDPs to display" (`displayNoIDPsMessage()`).
- "View" (`selectCurrentIDP(idpId)`) calls `viewCurrentIDP(designerId, idpId)`, which returns `IDP().getCurrentIDP(designerId, idpId)`. Found → `displayCurrentIDP(idp)`: title, category, description and location as customers see them (an empty location is left out), with Update (US22), Delete (US23) and Back to list.
- None (missing, someone else's, Past, Suspended or in a Suspended category) → `displayNotFoundMessage()`: "Current IDP not found" (HTTP 404) with no details.
- A designerId or userId added to the URL is ignored. Viewing changes nothing and isn't counted as a customer view (US32).

## Who checks what

- **Boundary** (`ViewCurrentIDPPage`): takes designerId from the session and shows what the controller returns. No typed input to check.
- **Control** (`ViewCurrentIDPController`): `viewCurrentIDPs(designerId)` and `viewCurrentIDP(designerId, idpId)` just call the entity and return the result - no checks.
- **Entity** (`IDP`): only returns the owner's Active Current IDPs whose category is Active (`projectType = 'Current' AND status = 'Active'`, category Active), with the joined `categoryName` for display.
- Precondition: logged in as an interior designer (UC13). `designerLoginRequired` in `app.py` only sends someone with no session to `/designer/login`; the use case doesn't check the designer again (no `InteriorDesignerLoginController`).

## Diagram/code mapping

| Diagram element | Code |
|---|---|
| Boundary `ViewCurrentIDPPage` — `clickViewCurrentIDPs()`, `selectCurrentIDP(idpId)`, `displayCurrentIDPs(idps)`, `displayCurrentIDP(idp)`, `displayNoIDPsMessage()`, `displayNotFoundMessage()` | `boundary/viewCurrentIDPPage.py`, `templates/currentIDPs.html`, `templates/viewCurrentIDP.html`, `templates/currentIDPNotFound.html` |
| Control `ViewCurrentIDPController` — `viewCurrentIDPs(designerId): list`, `viewCurrentIDP(designerId, idpId): IDP \| None` | `control/viewCurrentIDPController.py` |
| Entity `IDP` — `getCurrentIDPs(designerId): list`, `getCurrentIDP(designerId, idpId): IDP \| None` | `entity/idp.py` (table `idp`, joined with `idp_category`) |
| Route | GET `/designer/idps/current` → `viewCurrentIDPs()` and GET `/designer/idps/current/<idpId>` → `viewCurrentIDP(idpId)` (both `@designerLoginRequired`) in `app.py` |

Messages: `MSG_NO_IDPS` "You have no current IDPs to display", `MSG_NOT_FOUND` "Current IDP not found".

## Files

- `US21 View current IDPs.drawio` — every diagram, one page each
- `US21 View current IDPs.docx` — user story, use case description, diagrams, wireframes and test cases
- `diagrams/`
  - `2 Use Case Diagram.png`
  - `4a Wireframe - Current IDPs list.png`
  - `4b Wireframe - Current IDP details.png`
  - `4c Wireframe - No current IDPs.png`
  - `4d Wireframe - Current IDP not found.png`
  - `5 BCE Class Diagram.png`
  - `6 Sequence Diagram.png`

## Tests

```
python -m pytest tests/test_us21_viewCurrentIDPs.py -v
```
