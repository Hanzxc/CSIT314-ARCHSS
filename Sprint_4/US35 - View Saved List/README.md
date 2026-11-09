# US35 – View Saved List

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As a customer, I want to view my saved list so that I can see all the IDPs I have saved.

## Overview

- **Actor:** Customer
- **Purpose:** Allows the Customer to view all previously saved interior design projects in one place and access projects of interest.
- **Trigger:** The Customer selects the Saved List option from the customer dashboard or navigation menu.
- **Preconditions:** The Customer is logged in and has access to the saved list section.
- **Postconditions:** The system displays the Customer's saved IDPs, and the Customer can select a saved project to view its details.

## Main flow

1. The Customer opens the customer dashboard.
2. The Customer selects Saved List.
3. The system retrieves saved IDPs associated with the Customer's account.
4. The system displays the saved projects.
5. The Customer browses the saved IDPs.
6. The Customer selects a project from the list.
7. The system retrieves the selected project's information.
8. The system displays the project's details.
9. The Customer reviews the selected IDP.

## Alternative flows

- **Empty Saved List:** display a message if the Customer has not saved any IDPs.
- **Saved IDP No Longer Available:** indicate that the project cannot currently be viewed.
- **Project Not Found:** display an error if the selected IDP cannot be retrieved.
- **Loading Failure:** display an error and allow the Customer to try again.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #194 (use case description shows #143) |
| BCE and sequence diagrams | #202 |
| Wireframe | #254 |

## Test case status

The supplied Sprint 4 report contains an unfilled test-case template for US35. Add the executed test ID, procedure, test data, expected/actual output, test date, result and screenshot after testing.

**Test data:** Not specified in the supplied US35 test-case template.

**Expected output:** Based on the use case, the system displays the Customer's saved IDPs and allows the Customer to select a saved project to view its details.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report includes a blank test-case template; it does not provide completed test evidence for US35.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US35_ViewSavedList/
git commit -m "Add US35 – View Saved List README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
