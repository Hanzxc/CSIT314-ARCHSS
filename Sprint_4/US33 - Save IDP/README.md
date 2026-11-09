# US33 – Save IDP

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As a customer, I want to save an IDP so that I can look at it again later.

## Overview

- **Actor:** Customer
- **Purpose:** Allows a customer to save an interior design project to their saved list for easy access later.
- **Trigger:** The Customer clicks the Save option on an IDP details page.
- **Preconditions:** The Customer is logged in; the selected IDP exists and is available on the platform; and the Customer has permission to save IDPs.
- **Postconditions:** The selected IDP is added to the Customer's saved list, recorded under the Customer's account, and can be accessed later.

## Main flow

1. The Customer browses the available IDPs.
2. The Customer selects an IDP of interest.
3. The system displays the selected IDP's details.
4. The Customer clicks Save.
5. The system checks whether the IDP is already in the Customer's saved list.
6. The system adds the selected IDP to the Customer's saved list.
7. The system updates the saved list.
8. The system displays a successful confirmation message.
9. The Save option changes to indicate that the IDP has been saved.

## Alternative flows

- **IDP Already Saved:** inform the Customer that the project has already been saved and do not create a duplicate.
- **Customer Not Logged In:** request the Customer to log in before saving.
- **IDP Not Available:** display an error if the selected IDP is no longer available.
- **Saving Failure:** display an error and allow the Customer to try again.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #192 |
| BCE and sequence diagrams | #200 |
| Wireframe | #252 |

## Test case status

The supplied Sprint 4 report contains an unfilled test-case template for US33. Add the executed test ID, procedure, test data, expected/actual output, test date, result and screenshot after testing.

**Test data:** Not specified in the supplied US33 test-case template.

**Expected output:** Based on the use case, the selected IDP is added to the Customer's saved list, the list is updated, a confirmation is shown and the Save option indicates the saved state.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report includes a blank test-case template; it does not provide completed test evidence for US33.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US33_SaveIDP/
git commit -m "Add US33 – Save IDP README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
