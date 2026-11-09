# US29 – Search Past IDPs

This folder contains the documentation and diagram assets for this user story in the CSIT314 Software Development Methodologies group project.

## User story

> As an interior designer, I want to search my past IDPs so that I can find the IDP I need to manage.

## Overview

- **Actor:** Interior Designer
- **Purpose:** Allows the designer to search previously added completed projects using keywords to find a specific IDP to manage.
- **Trigger:** The Interior Designer enters a keyword into the search bar in the Past IDPs section.
- **Preconditions:** The Interior Designer is logged in and has access to the Past IDPs section.
- **Postconditions:** The system displays past IDPs matching the search keyword, and the designer can select a matching project to view or manage.

## Main flow

1. The Interior Designer opens the Past IDPs section.
2. The system displays the designer's past IDPs and a search bar.
3. The designer enters a keyword into the search bar.
4. The designer submits the search request.
5. The system searches the designer's past IDPs using the entered keyword.
6. The system retrieves matching projects.
7. The system displays the search results.
8. The designer selects a project from the results.
9. The system displays the selected project's details.

## Alternative flows

- **Empty Search:** display all past IDPs or ask the designer to enter a keyword.
- **No Matching Results:** display a no-results message.
- **Invalid Search Input:** display an appropriate validation message.
- **Search Failure:** display an error and allow the designer to try again.

## Taiga task references

| Deliverable | Taiga Task ID |
|---|---:|
| Use case diagram and description | #191 |
| BCE and sequence diagrams | #199 |
| Wireframe | #251 |

## Test case status

Test ID 29 – Search Past IDP. The source report records Actual Output: Passed; Test Date: 02 Nov 2026.

**Test data:** Search keyword: Modern. Expected matching project: Modern 4-Room HDB Resale Transformation.

**Expected output:** The system displays past IDP records matching the keyword. If no record matches, an appropriate no-results message is displayed.

## Files in this folder

The supplied story folder contains the editable draw.io diagram and exported PNG diagram assets. The Sprint 4 report also includes the wireframe and test-case evidence.

The `.drawio` file is the editable diagram source. The `.png` files are exported diagram images. Open draw.io files using [diagrams.net](https://app.diagrams.net/).

## GitHub upload example

Run the following commands from the root of your repository. Replace the folder path if your repository uses a different location:

```bash
git add Sprint4/US29_SearchPastIDP/
git commit -m "Add US29 – Search Past IDPs README and diagrams"
git push origin main
```

After pushing, open the GitHub repository and check that this folder, its README, editable diagram and PNG exports are visible.

## Source note

This README is based on the supplied Sprint 4 report and the corresponding story folder in Sprint4.zip. Where the supplied report leaves test-case fields blank, this README identifies them as not yet documented rather than inventing results.
