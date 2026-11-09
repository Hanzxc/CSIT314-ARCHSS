# US28 – Delete Past IDP

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As an interior designer, I want to delete a past IDP so that it is no longer shown on the platform.

## Overview

- **Actor:** Interior Designer
- **Purpose:** Allows the designer to remove a previously added completed project from the platform so customers can no longer view it.
- **Trigger:** The Interior Designer selects the Delete option for an existing past IDP.
- **Preconditions:** The Interior Designer is logged in, has an active account, and the selected Past IDP exists and belongs to the designer.
- **Postconditions:** The selected Past IDP is deleted or made unavailable for public viewing, and is no longer displayed to customers.

## Main flow

1. The Interior Designer opens the Past IDPs section.
2. The system displays the designer's past projects.
3. The designer selects the project to delete.
4. The system displays the selected project's details.
5. The designer selects Delete.
6. The system displays a confirmation message.
7. The designer confirms the deletion.
8. The system processes the deletion request.
9. The system removes the project from publicly displayed Past IDPs.
10. The system displays a successful deletion confirmation.
11. The system refreshes the Past IDPs list.

## Alternative flows

- **Deletion Cancelled:** return to project details without deleting the project.
- **Project Not Found:** display an error if the selected project cannot be found.
- **Deletion Failure:** display an error and allow the designer to try again.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #190 |
| BCE and sequence diagrams | #198 |
| Wireframe | #250 |

## Test case status

Test ID 28 – Delete Past IDP. The source report records Actual Output: Passed; Test Date: 02 Nov 2026.

**Test data:** Project to delete: Modern 4-Room HDB Resale Transformation. Action: select Delete, then confirm with OK.

**Expected output:** The system asks for confirmation. After confirmation, the selected past IDP is deleted, a success message appears and the project is removed from the portfolio.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report also includes the wireframe and test-case evidence.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US28_DeletePastIDP/
git commit -m "Add US28 – Delete Past IDP README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
