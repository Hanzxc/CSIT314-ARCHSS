# US23 — Delete current IDP

> As an interior designer, I want to delete a current IDP so that it is no longer shown on the platform.

## Using the feature

1. Sign in as an Interior Designer, open Current IDPs and view a project.
2. Select **Delete current IDP** to open the existing-style confirmation overlay.
3. Select **Delete current IDP** in the dialog to remove it from platform views, or **Cancel** to return without saving a deletion.
4. Successful deletion returns to Current IDPs with **Current IDP deleted successfully**. If no visible projects remain, the normal empty state appears.

The US21 optional demo records work for US23: `python -m database.seedData`, `python -m database.seedCurrentIDPData`, then `python app.py`. Sign in at `/designer/login` with `idpdemo001 / Demo@123` or `idpdemo002 / Demo@123`. Re-running that seed preserves existing suspended records rather than restoring them.

## Deletion semantics and access

US23 follows the current company-profile delete convention: the selected IDP's `status` changes from `Active` to `Suspended`. Its row, title, category, description/progress, location, owner, project type, identifier and creation date are retained. No related project, category or account is deleted. Permanent database removal and restore/reactivation are outside this story.

Only the session owner's Active Current IDP in an Active category is eligible. The owner is obtained from `session["userId"]`; posted owner, ID, status and fingerprint fields are ignored. Missing, other-owner, Past, Suspended or hidden-category targets return HTTP 404 on GET and POST without disclosing project details. A missing session redirects to designer login; invalid or revoked US13 designer access returns HTTP 403.

GET is read-only and opens a confirmation. The signed session stores the user, target ID, random confirmation token and a compact SHA-256 fingerprint of the reviewed title, category ID, description, location and creation date. The full project content is not stored in the cookie. Opening another confirmation replaces the earlier one. Both Delete and Cancel require a matching user/project token; a missing, forged, stale or cross-user/project token returns 403 while the target remains available. Unknown choices return 400.

The confirmation is consumed before deletion. The entity performs one guarded SQL UPDATE requiring the same owner, Active Current status, Active category and reviewed fingerprint. The fingerprint is recalculated inside SQLite for the write, so an intervening edit cannot be deleted using stale confirmation. Changed content returns HTTP 409 with a fresh-review prompt; newly unavailable targets return 404. After a successful delete, any pending US22 update token for that project is also removed.

The existing US21 list/preview and US22 update queries already filter Active IDPs, so the suspended project disappears and old preview/update/delete links return 404. Future customer/category listings must apply the same Active-project filter. There is no US32 customer page in this checkout yet. No database migration is needed.

## Code and diagram mapping

| Layer | File / operations |
|---|---|
| Boundary | `boundary/deleteCurrentIDPPage.py`: access, confirmation, token/choice checks, Cancel, errors and success |
| Control | `control/deleteCurrentIDPController.py`: `canDeleteCurrentIDP()`, `getCurrentIDP()`, `getSnapshot()`, `deleteCurrentIDP()` |
| Entity | `entity/idp.py`: existing retrieval plus `getSnapshot()` and `suspendCurrentIDP()` |
| Reused access | `InteriorDesignerLoginController.getAuthenticatedDesigner()` |
| Route | GET/POST `/designer/idps/current/<idpId>/delete` |
| Templates | `deleteCurrentIDP.html`, `currentIDPDeleteError.html`, Delete link in `viewCurrentIDP.html`; shared `idpDetailContent.html` |

## Document and editable diagrams

- `US23 Delete current IDP.docx` follows the retained US13 sample: assumptions, story/acceptance criteria/tasks, use case diagram/description, four wireframes, BCE diagram/responsibilities, one combined sequence diagram, 12 manual system scenarios and 31 unit cases.
- `US23 Delete current IDP.drawio` contains seven editable pages.
- `diagrams/2 Use Case Diagram.png`
- `diagrams/5 BCE Class Diagram.png`
- `diagrams/6 Sequence Diagram.png`
- `diagrams/4a Wireframe - Delete action.png`
- `diagrams/4b Wireframe - Delete confirmation.png`
- `diagrams/4c Wireframe - Deletion result.png`
- `diagrams/4d Wireframe - Deleted IDP not found.png`

Wireframes follow the actual designer header/sidebar, action colours, cards and messages. Confirmation reuses the `.overlay` and `.confirm-box` styles: a dimmed viewport, 420px dialog, red Delete action and grey Cancel. The single sequence diagram uses `ref` frames for repeated access, fingerprint and confirmation checks; `opt` covers valid Delete and `alt` the outcomes.

## Validation

Verified on 2 November 2026: **641 tests passed**, including **72 US23 checks** and all 569 previous tests. The 31 numbered US23 cases cover access, ownership, atomic stale-review checks, status-only changes, Cancel, bad/consumed/cross-user tokens, repeated deletion, existing list/update visibility, escaped text and compact cookies for maximum-length Unicode descriptions. Unit results are recorded in the Word document; manual system results remain blank.

```text
python -m pytest tests/test_us23_deleteCurrentIDP.py -q
python -m pytest -q
```
