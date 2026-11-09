# US25 – Add Past IDP

This folder contains the separate documentation and diagram assets for **User Story #25 – Add Past IDP** in the CSIT314 Software Development Methodologies group project.

## User story

> As an interior designer, I want to add a past IDP so that I can show customers my completed work.

## Files

- `US25_Add_Past_IDP_Report.docx` — standalone report for US25, including the user story, use case description, B-C-E diagram, sequence diagram, wireframe reference, and test cases.
- `US25_AddPastIDP/US25 Add past IDP.drawio` — editable draw.io source file supplied for US25.
- `US25_AddPastIDP/US25_Add_Past_IDP.png` — exported B-C-E diagram.
- `US25_AddPastIDP/US25_Sequene_Add_Past_IDP.png` — exported sequence diagram.
- `US25_AddPastIDP/US25_Wireframe_Source_Page.png` — page image extracted from the supplied Sprint 4 report, showing the US25 wireframe.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #187 |
| B-C-E class diagram and sequence diagram | #195 |
| Wireframe | #247 |
| Test case documentation | #262 |

## Test cases included

- **TC25.1 – Add Past IDP (Success Path):** valid project details are submitted; the source report records the actual output as Passed on 2 Nov 2026.
- **TC25.2 – Add Past IDP (Validation Failure):** required information is missing; the source report records the actual output as Passed on 2 Nov 2026.

The test details in the report are transcribed from the supplied Sprint 4 report. Check the live application and update the evidence/screenshots if your team needs to demonstrate a fresh test run.

## Editing diagrams

1. Open [draw.io](https://app.diagrams.net/).
2. Choose **Open Existing Diagram**.
3. Select `US25 Add past IDP.drawio`.
4. Edit the diagram and export a new PNG if needed.

## Example GitHub upload

Run these commands from the root of your project repository:

```bash
git status
git add US25_Add_Past_IDP_Report.docx README.md US25_AddPastIDP/
git commit -m "Add US25 Add Past IDP report and diagrams"
git push origin main
```

If this folder is inside a parent `Sprint4/` folder, stage the relevant path instead:

```bash
git add Sprint4/US25_AddPastIDP/
git add Sprint4/US25_Add_Past_IDP_Report.docx
git commit -m "Add US25 Add Past IDP documentation"
git push origin main
```

After pushing, open the GitHub repository and confirm that the report, README, editable draw.io file and PNG exports are visible.

Do not commit passwords, API keys, database credentials or other secrets.
