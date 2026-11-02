# US22 — Update current IDP

> As an interior designer, I want to update a current IDP so that customers can see its latest progress.

## Using the feature

1. Sign in as an Interior Designer and open **Current IDPs**.
2. View a project, then select **Update current IDP**.
3. Edit the prefilled fields and select **Save changes**. The updated preview appears with **Current IDP updated successfully**.
4. **Cancel** returns to the preview without saving.

The existing optional demo setup works for US22: `python -m database.seedData`, `python -m database.seedCurrentIDPData`, then `python app.py`. Sign in at `/designer/login` as `idpdemo001 / Demo@123` or `idpdemo002 / Demo@123`. Both own current projects. US20's add form is still on its separate branch; US22 does not require merging it.

## Behaviour and scope

| Editable field | Rules |
|---|---|
| `title` | Required, 3–100 characters after trimming |
| `categoryId` | Must identify an existing Active category |
| `description` | Required, 1–2000 characters after trimming; includes latest project progress |
| `location` | Optional, at most 200 characters after trimming |

Ownership is obtained from `session["userId"]`. The selected URL `idpId` is filtered by that owner, `projectType = "Current"`, `status = "Active"`, and an Active source category. No additional company-profile prerequisite is imposed. Missing, other-owner, Past, Suspended or hidden-category projects return HTTP 404 for both form display and submission.

US13 access is rechecked on every request and again in controller operations. A missing session redirects to designer login; invalid/inactive designer access returns HTTP 403. The form contains a hidden token scoped to the signed-in user and IDP. Missing, forged, stale, cross-project/cross-user or already-consumed tokens return 403 without saving. Reopen the form to obtain a new token. Loading another form for the same project invalidates its earlier form token.

Invalid fields return the form with **Please fix the highlighted fields**, inline field errors and retained input. The category selector lists only Active categories. The entity's conditional SQL UPDATE also checks ownership, project visibility and Active source/destination categories at the write itself. If a destination category becomes unavailable during submission, the form reports its category error. A source that becomes unavailable returns 404. Other unsuccessful updates show a retry message.

Only the four fields above can change. `idpId`, `designerId`, `projectType`, `status` and `createdDate` are preserved; forged posted metadata is ignored. No extra progress-percentage, image-upload, edit-history or completion workflow is introduced. Later valid edits replace earlier values; optimistic version-conflict detection is outside this story. The reusable `idpDetailContent.html` partial shows the saved fields in the US21 preview and can be used by the future US32 customer route.

## Code and route mapping

| Layer | File and operations |
|---|---|
| Boundary | `boundary/updateCurrentIDPPage.py`: access, prefill, input/token checks, errors and success redirect |
| Control | `control/updateCurrentIDPController.py`: designer access, category/field validation and save delegation |
| Entity | `entity/idp.py`: existing `getCurrentIDP()` plus `updateCurrentIDP()` |
| Entity | `entity/idpCategory.py`: US20-compatible category fields and active-category retrieval |
| Reused control | `InteriorDesignerLoginController.getAuthenticatedDesigner()` |
| Route | GET/POST `/designer/idps/current/<idpId>/update` |
| UI | `templates/updateCurrentIDP.html`, `templates/currentIDPUpdateError.html`, update link in `templates/viewCurrentIDP.html` |

US22 uses the tables already introduced for US21 and requires no schema migration. Names and field limits follow the US20 feature branch. Existing records and previous user stories are retained.

## Diagrams and document

- `US22 Update current IDP.docx` follows the retained US13 sample in `sources/document-templates/`: assumptions, user story/criteria/tasks, use case diagram/description, four wireframes, BCE diagram/responsibilities, one combined sequence, 12 manual system scenarios and 30 unit cases.
- `US22 Update current IDP.drawio` contains seven editable pages.
- `diagrams/2 Use Case Diagram.png`
- `diagrams/4a Wireframe - Update action.png`
- `diagrams/4b Wireframe - Prefilled update form.png`
- `diagrams/4c Wireframe - Validation errors.png`
- `diagrams/4d Wireframe - Updated preview.png`
- `diagrams/5 BCE Class Diagram.png`
- `diagrams/6 Sequence Diagram.png`

The wireframes follow the actual designer templates and shared CSS: dark header, Dashboard/Current IDPs sidebar, Active navigation styling, 600px form, required labels, category selector, highlighted errors, Save changes and Cancel. No new navigation design is introduced. The sequence remains a single diagram on one landscape document page; `ref` frames summarise reused access/category/validation interactions.

## Validation

Verified on 2 November 2026: **569 tests passed**, including **86 US22 checks** and all 483 previous tests. The 30 numbered US22 test functions expand through parametrisation to cover field boundaries, owner/visibility filtering, category changes during saving, immutable fields, escaped text, Cancel, token scope/replay and access revocation. Unit results are recorded in the Word document; manual system result cells remain blank.

```text
python -m pytest tests/test_us22_updateCurrentIDP.py -q
python -m pytest -q
```
