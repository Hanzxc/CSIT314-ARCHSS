# US21 — View current IDPs

> As an interior designer, I want to view my current IDPs so that I can check how they look to customers.

UC21 is implemented in this checkout. Names and IDP attributes align with US20 on the remote `origin/add-us20-us40-45` branch as inspected on 2 November 2026. That branch has not been merged; only the prerequisite IDP/category schema and model fields are included. The editable diagrams are in `US21 View current IDPs.drawio`; matching PNG exports are in `diagrams/`.

## Implementation and validation

- Boundary: `boundary/viewCurrentIDPPage.py`; controller: `control/viewCurrentIDPController.py`; entity: `entity/idp.py`.
- GET `/designer/idps/current` lists the session owner's visible projects; GET `/designer/idps/current/<idpId>` displays one. The dashboard and sidebar link to the list.
- `templates/idpDetails.html` contains reusable customer-facing content; US32 can reuse it when the customer route is built. US32 is not implemented here.
- `initDatabase()` adds the US20-compatible prerequisite tables without deleting records. Existing company migration behaviour is retained.
- Optional demo: `python -m database.seedData`, `python -m database.seedCurrentIDPData`, then `python app.py`. Sign in as `idpdemo001 / Demo@123` or `idpdemo002 / Demo@123`. Existing demo rows are preserved when reseeding.
- Verified on 2 November 2026: **483 tests passed**, including **61 US21 tests** and 422 existing tests. Run `python -m pytest -q` or `python -m pytest tests/test_us21_viewCurrentIDPs.py -q`.

## Scope and assumptions

- A current IDP is an interior design project with `projectType = "Current"`; past projects belong to US26.
- The designer opens a list of their own current projects and selects one to view its customer-facing content. The preview contains title, category name, description and location, using the same content layout as the eventual customer view in US32. US20 currently excludes photographs; this design does too.
- Only Active IDPs in Active categories are visible. The category rule is a proposed interpretation of US44 (users can no longer see or select suspended categories); it must also be applied to the eventual US32 customer view. The IDP itself is preserved when its category is suspended.
- Ownership is the individual designer's `userId`, matching US20, rather than shared company ownership. `designerId` comes from the session, never a URL or form field. A selected `idpId` is an untrusted identifier and must be filtered by that session owner.
- Listing and viewing are read-only. Designer previews do not increment customer view statistics (US37).
- Authentication is a precondition, not an `<<include>>` relationship to login: the designer does not log in again whenever they view a project.
- Add, update, delete, search and past-IDP viewing are separate user stories. No extra dependency on having an Active company profile is introduced.

## Use case description

| Item | Description |
|---|---|
| Use case | UC21 View current IDPs |
| Primary actor | Interior Designer |
| Trigger | Designer clicks View current IDPs on the designer dashboard |
| Preconditions | Signed in; Active account and profile; authorised by the existing US13 designer check |
| Success postcondition | Own visible Current IDPs are displayed; a selected IDP displays its customer-facing details |
| Other postconditions | No IDP data or customer statistics change; other designers' IDPs are not disclosed |

Basic flow:

1. Designer clicks **View current IDPs**.
2. Boundary checks the session and obtains `designerId` from `session["userId"]`.
3. Controller uses the existing `InteriorDesignerLoginController.getAuthenticatedDesigner()` to check access. US13 verifies Active account/profile and its existing required permissions, including **Manage own IDPs**.
4. Controller requests the designer's visible Current IDPs from `IDP.getCurrentIDPs(designerId)`.
5. Entity retrieves only matching owner, Current project type, Active IDP and Active category; results are ordered by `idpId DESC`.
6. Boundary displays the list with a View action for each project.
7. Designer selects an IDP; the boundary and controller recheck access for this new request.
8. Entity retrieves that selected IDP using the same ownership and visibility rules.
9. Boundary displays the customer-facing detail content and a return-to-list action.

Alternative flows:

| Condition | Result |
|---|---|
| No session | Redirect to the existing interior designer login page; stop |
| Account/profile suspended, wrong role or insufficient permissions | Access denied, HTTP 403; stop |
| No visible Current IDPs | Display **You have no current IDPs to display**; normal empty list, HTTP 200 |
| Selected IDP missing, belongs to someone else, is Past/Suspended, or category is unavailable | Display **Current IDP not found**, HTTP 404; disclose no project details |
| Access or project visibility changes after listing | Recheck on detail request and apply the corresponding error above |

## Diagram and method mapping

| Element | Responsibilities / methods |
|---|---|
| Boundary `ViewCurrentIDPPage` | `checkAccess()`, `clickViewCurrentIDPs()`, `selectCurrentIDP(idpId)`, `displayCurrentIDPs(idps)`, `displayCurrentIDP(idp)`, `displayNoIDPsMessage()`, `displayErrorMessage(msg)` |
| Control `ViewCurrentIDPController` | `canViewCurrentIDPs(designerId)`, `viewCurrentIDPs(designerId)`, `viewCurrentIDP(designerId, idpId)` |
| Reused US13 control | `InteriorDesignerLoginController.getAuthenticatedDesigner(userId)` |
| Entity `IDP` | Proposed additions `getCurrentIDPs(designerId)` and `getCurrentIDP(designerId, idpId)` |

`IDP` retains US20's `idpId`, `designerId`, `categoryId`, `title`, `description`, `location`, `projectType`, `status` and `createdDate` attributes. `/ categoryName` denotes a derived display value obtained by joining `idp_category`, not a new stored IDP column. The controller and entity retrieval methods above are implemented by US21.

Each controller retrieval operation rechecks `canViewCurrentIDPs()` before querying. Denial raises `PermissionError`, handled by the boundary as HTTP 403 rather than an ordinary empty list. `getCurrentIDPs()` returns `[]` for no matching projects; `getCurrentIDP()` returns `None` for no matching project. The single combined sequence diagram uses `ref` bands for repeated access checks, `alt` for results and `opt` for selecting an IDP. Message 12b abbreviates the boundary's `displayErrorMessage("Current IDP not found")` response. The Word document places the combined diagram on one landscape page.

## Acceptance checks for future implementation

1. An authorised designer sees only their own Active Current IDPs in Active categories.
2. A selected project displays the same customer-facing fields/layout intended for US32.
3. An empty list displays the stated message without an error.
4. Direct detail requests for another owner, Past/Suspended projects or suspended categories return 404.
5. Missing sessions redirect to login; invalid designer access returns 403 on both list and detail requests.
6. Repeated previews leave IDP records and customer view statistics unchanged.

## Files

The four wireframes and their Word document images were refreshed on 2 November 2026 to match the actual templates and the US22 styling: dark header with Log out, Dashboard/Current IDPs sidebar, the flex card list, existing messages/buttons, and the Update current IDP link on the detail preview. The use case, BCE and combined sequence diagrams are retained.

- `US21 View current IDPs.docx` — complete story document following the retained US13 sample in `sources/document-templates/`. Includes assumptions, acceptance criteria, use case description, diagrams, four wireframes, 12 system test scenarios and 24 unit test cases. Unit results record the verified test run; manual system results remain unfilled.
- `US21 View current IDPs.drawio` — seven editable pages: use case, BCE class, one combined sequence and four wireframes.
- `diagrams/2 Use Case Diagram.png`
- `diagrams/5 BCE Class Diagram.png`
- `diagrams/6 Sequence Diagram.png`
- `diagrams/4a Wireframe - Current IDPs list.png`
- `diagrams/4b Wireframe - Current IDP details.png`
- `diagrams/4c Wireframe - No current IDPs.png`
- `diagrams/4d Wireframe - Current IDP not found.png`
