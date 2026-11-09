# US34 – Search Saved List

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As a customer, I want to search my saved list so that I can find an IDP I saved earlier.

## Overview

- **Actor:** Customer
- **Purpose:** Allows the Customer to search previously saved IDPs using keywords to find a particular project to view again.
- **Trigger:** The Customer enters a keyword into the search bar in the saved list section.
- **Preconditions:** The Customer is logged in and has access to their saved list.
- **Postconditions:** The system displays saved IDPs matching the search keyword, and the Customer can select a matching IDP to view its details.

## Main flow

1. The Customer opens the saved list section.
2. The system displays the Customer's saved IDPs and a search bar.
3. The Customer enters a keyword into the search bar.
4. The Customer submits the search request.
5. The system searches the Customer's saved list using the entered keyword.
6. The system retrieves matching saved IDPs.
7. The system displays the search results.
8. The Customer selects an IDP from the results.
9. The system displays the selected IDP's details.

## Alternative flows

- **Empty Search:** display all saved IDPs or ask the Customer to enter a keyword.
- **No Matching Results:** display a no-results message.
- **Invalid Search Input:** display a validation message.
- **Search Failure:** display an error and allow the Customer to try again.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #193 |
| BCE and sequence diagrams | #201 |
| Wireframe | #253 |

## Test case status

The supplied Sprint 4 report contains an unfilled test-case template for US34. Add the executed test ID, procedure, test data, expected/actual output, test date, result and screenshot after testing.

**Test data:** Not specified in the supplied US34 test-case template.

**Expected output:** Based on the use case, the system displays saved IDPs matching the keyword and lets the Customer select a result to view its details.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report includes a blank test-case template; it does not provide completed test evidence for US34.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US34_SearchSavedList/
git commit -m "Add US34 – Search Saved List README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
