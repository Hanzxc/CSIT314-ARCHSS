# US24 — Search current IDPs

> As an interior designer, I want to search my current IDPs so that I can find the IDP I need to manage.

## Using the feature

1. Sign in as an Interior Designer and open **Current IDPs**.
2. Select **Search current IDPs** and enter a keyword.
3. Select **Search** to see matching project cards; **View** opens the existing US21 preview with its Update/Delete actions.
4. **Clear** resets the keyword and shows all visible own current projects. **Back to current IDPs** returns to the ordinary list.

Existing demo setup: `python -m database.seedData`, `python -m database.seedCurrentIDPData`, then `python app.py`. Sign in at `/designer/login` as `idpdemo001 / Demo@123` or `idpdemo002 / Demo@123`; try `kitchen`, `Tampines` or an empty search.

## Search rules

- Searches title, description/progress, location and joined category name. One literal substring is matched across those fields; multiple words are one phrase, not a separate query language.
- Trims the keyword and uses Unicode case folding for case-insensitive comparisons. Accents are not stripped and no separate Unicode-normalisation/fuzzy/stemming behaviour is introduced.
- `%`, `_`, quotes and backslashes are ordinary characters, not wildcards/operators. Query values are bound parameters; input is not interpolated into SQL.
- Missing/empty/whitespace-only keywords show all visible own projects. Clear makes the same empty-keyword request.
- Always limits results to `session["userId"]`, `projectType = "Current"`, Active IDPs and Active categories. Other-owner, Past, Suspended, deleted and hidden-category projects never appear.
- Results are newest first (`idpId DESC`), with one card per project even if multiple fields match. The keyword remains in the form and a result count is shown.
- A nonempty search with no matches returns HTTP 200 and **No matching current IDPs found**. An empty search with no visible projects returns HTTP 200 and **You have no current IDPs to display**.
- No arbitrary keyword length limit is introduced by US24. Searching is read-only; no IDP fields or customer statistics change.

US13 designer access is rechecked by the boundary and controller on each request. Missing sessions redirect to designer login; invalid/revoked designer access returns HTTP 403 rather than an empty result. Posted/query owner fields cannot replace the session owner. Selecting View makes a new US21 request, so access/visibility are rechecked if a result was deleted or hidden after searching. New searches reflect the latest US22 updates and US23 deletion status.

## Code and route mapping

| Layer | File / operation |
|---|---|
| Boundary | `boundary/searchCurrentIDPPage.py`: `checkAccess()`, `searchCurrentIDPs(keyword)`, `displayResults(idps)`, `displayNoResultsMessage()` |
| Control | `control/searchCurrentIDPController.py`: `canSearchCurrentIDPs(designerId)`, `searchCurrentIDPs(designerId, keyword)` |
| Entity | `entity/idp.py`: `searchCurrentIDPs(designerId, keyword)` |
| Reused access | `InteriorDesignerLoginController.getAuthenticatedDesigner()` |
| Route | GET `/designer/idps/current/search?keyword=...` |
| UI | `templates/searchCurrentIDPs.html`; shared `currentIDPCards.html` used by US21 and US24; entry link in `currentIDPs.html` |

The query extends the existing owner/visibility-filtered IDP SELECT. A connection-local SQLite function applies Python Unicode case folding; `instr()` performs literal substring matching. No schema migration or new dependency is required. Search does not implement the later customer search story.

## Document and editable diagrams

- `US24 Search current IDPs.docx`: retained US13 document format, assumptions, story/criteria/tasks, use case description, four wireframes, BCE responsibilities, one combined sequence, 12 manual system scenarios and 32 unit cases.
- `US24 Search current IDPs.drawio`: seven editable pages.
- `diagrams/2 Use Case Diagram.png`
- `diagrams/5 BCE Class Diagram.png`
- `diagrams/6 Sequence Diagram.png`
- `diagrams/4a Wireframe - Search form.png`
- `diagrams/4b Wireframe - Matching results.png`
- `diagrams/4c Wireframe - No matching results.png`
- `diagrams/4d Wireframe - No current IDPs.png`

Wireframes follow the actual designer header/sidebar, shared `.search-bar`, blue Search button, grey Clear/Back actions, existing information messages and shared project-card layout. Clear returns to the all-results view represented by wireframe 4a. The sequence is a single landscape figure; result selection continues to US21 as a referenced interaction.

## Validation

Verified on 2 November 2026: **696 tests passed**, including **55 US24 checks** and all 641 previous tests. The 32 numbered cases cover all four fields, Unicode/case/whitespace, literal symbols, empty/no results, duplicates/order, owner/visibility/access filtering, safe rendered text, read-only requests and current update/delete state. Unit results are recorded in the Word document; manual system results remain blank.

```text
python -m pytest tests/test_us24_searchCurrentIDPs.py -q
python -m pytest -q
```
