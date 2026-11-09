# US27 – Update Past IDP

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As an interior designer, I want to update a past IDP so that its details are correct.

## Overview

- **Actor:** Interior Designer
- **Purpose:** Allows the designer to update information for a previously added completed project so that its details remain correct and up to date.
- **Trigger:** The Interior Designer selects the Update option for an existing past IDP.
- **Preconditions:** The Interior Designer is logged in, has an active account, and the selected Past IDP exists and belongs to the logged-in designer.
- **Postconditions:** The Past IDP is updated successfully, the revised information is stored, and customers can view the latest project details.

## Main flow

1. The Interior Designer opens the Past IDPs section.
2. The system displays the designer's past projects.
3. The designer selects the project to update.
4. The system displays the selected project's existing information.
5. The designer clicks Update.
6. The system displays the update form with existing information.
7. The designer modifies the required project details.
8. The designer submits the updated information.
9. The system validates the updated information.
10. The system saves the changes.
11. The system displays a successful update confirmation.
12. The system displays the updated project information.

## Alternative flows

- **Invalid Information:** display validation messages.
- **Missing Required Information:** ask the designer to complete required fields.
- **Cancel Update:** return to project details without saving changes.
- **Project Not Found:** display an error if the selected project no longer exists.
- **Update Failure:** display an error and allow the designer to retry.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #189 |
| BCE and sequence diagrams | #197 |
| Wireframe | #249 |

## Test case status

Test ID 27.1 – Update Past IDPs. The source report records Actual Output: Passed; Test Date: 02 Nov 2025 (as written in the supplied report).

**Test data:** Existing project: Modern 4-Room HDB Resale Transformation. Updated title shown in evidence: Condominium 1-bedroom studio; Category: Kitchen; Location: Bugis; Description: near mrt.

**Expected output:** The system saves the revised details, displays a success message and shows the updated project in the Past IDPs Portfolio.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report also includes the wireframe and test-case evidence.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US27_UpdatePastIDP/
git commit -m "Add US27 – Update Past IDP README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
