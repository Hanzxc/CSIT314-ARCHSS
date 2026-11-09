# US26 – View Past IDPs

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As an interior designer, I want to view my past IDPs so that I can check how they look to customers.

## Overview

- **Actor:** Interior Designer
- **Purpose:** Allows the designer to view a list of completed interior design projects previously added to the platform.
- **Trigger:** The Interior Designer selects the Past IDPs option from the designer dashboard.
- **Preconditions:** The Interior Designer is logged in and has an active account and profile.
- **Postconditions:** The system displays the designer's past IDPs, and the designer can review each project's information and details.

## Main flow

1. The Interior Designer opens the designer dashboard.
2. The designer selects Past IDPs.
3. The system retrieves past IDPs belonging to the logged-in designer.
4. The system displays the list of past IDPs.
5. The designer selects a project from the list.
6. The system displays the selected project's details.
7. The designer reviews the project information.

## Alternative flows

- **No Past IDPs Available:** display a message when the designer has not added past projects.
- **Project Not Found:** display an error if the selected project cannot be retrieved.
- **Loading Failure:** display an error and allow the designer to try again.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #188 |
| BCE and sequence diagrams | #196 |
| Wireframe | #248 |

## Test case status

Test ID 26.1 – View Past IDP. The source report records Actual Output: Passed; Test Date: 02 Nov 2026.

**Test data:** Valid interior designer account; Past IDPs page; previously saved past IDP records.

**Expected output:** The Past IDPs Portfolio page is displayed with saved past IDP records and available details. If no records exist, an appropriate empty-state message is shown.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report also includes the wireframe and test-case evidence.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US26_viewPastIDP/
git commit -m "Add US26 – View Past IDPs README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
