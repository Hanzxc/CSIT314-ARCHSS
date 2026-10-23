# US14 - Create Company Profile

Updated company-profile lifecycle amendment, applied together after US13-19 and US39.

## Behaviour
Create saves a new Active profile. If the designer already has a Suspended row, creation reuses it with the newly submitted business details, changes status to Active, and increments revision. Existing Active profiles still reject duplicate creation. IDs, owner and createdDate are retained on reactivation. Validation and access checks are unchanged.

The shared CompanyProfile entity contains status (Active/Suspended) and revision (activation version). Status is system-controlled; it is not an editable creation field. getCompanyProfile() returns only Active profiles. Reactivation is the recommended option (a): it uses the newly submitted details, not an automatic recovery of all old field values. A suspended row is preserved until explicitly reactivated, but reactivation replaces its business details; this is not a full historical audit/version archive.

## Code and database
Full replacement source files are supplied in the amendment ZIP, with an exact list in its root README and CHANGED-FILES.txt. Replace file contents; do not append complete versions below old code. app.py and login code do not change in this amendment. Existing routes and Delete wording remain.

Start with python app.py. database.db.initDatabase() automatically adds missing status/revision columns to an existing database, keeps all existing rows, and can run repeatedly. Existing companies become Active with revision 1. Keep your own database/archss.db; the package contains no database file. US15/16/18 changes use the shared active-only entity behaviour, with regression tests in each story's test file.

## Tests and browser checks
Run python -m pytest tests -q from the repository root. Verified amendment with Restore: 422 tests pass, including existing admin/designer/manager tests and the new suspension, reactivation and migration checks. Test data uses the existing isolated conftest.py fixture; browser-created records are not used by pytest.

In the running website, log in as an Active Interior Designer, create a company, view its Active status, update/search it, open Delete and try Cancel, then confirm Delete. The dashboard offers Restore company profile for its own Suspended record. The old view/update/search URLs must return 404 while suspended. Restore returns the same saved record to Active with all business details unchanged. The existing explicit US14 creation route can still reactivate using newly entered details, but the normal suspended-dashboard action is Restore. User account/login are kept. A fresh confirmation works; an old consumed or earlier-activation confirmation cannot suspend the reactivated company.

## Diagrams
The PNG use case/BCE/sequence diagrams and labelled wireframes use the existing story format. The draw.io file is editable. Only story-relevant entity methods are shown; status/revision are included. US14 explains insertion versus reactivation. US17 shows suspension and the revision guard. US15/16/18 document Active-only access. Images are diagram/wireframe exports rather than browser screenshots. Written use case descriptions and written test case tables remain deferred.


## Own-dashboard Restore extension (US17)
The existing designer dashboard now checks for its own Suspended company and shows a Restore company profile POST button instead of Create in that state. It shows status only, not a list of company records. Active companies show View; designers with no company row show Create. A fresh signed-session confirmation is prepared when the dashboard opens. The Restore boundary reads the owner/record/revision from that confirmation, never from posted owner or company fields. Restore rechecks account/profile/permissions, changes only status/revision, clears stale delete confirmation, and redirects to the existing company view with Company profile restored successfully. Invalid/reused confirmations redirect to the dashboard with an error and no business-data changes. Logging out clears the session; reopening the dashboard after login prepares a fresh Restore button.

This is implemented by RestoreCompanyProfilePage, RestoreCompanyProfileController and the shared Company's getSuspendedCompanyProfile()/restoreCompanyProfile() methods, plus POST /designer/company/restore in app.py. It adds no suspended-company listing page. The new tests/test_us17_restoreCompanyProfile.py contains 25 simple pytest functions. All 422 tests pass. US17's single sequence canvas covers Delete followed by the own-dashboard Restore interaction; BCE/use case diagrams and restored/error wireframes agree with the implementation. The US13 login flow, US19 logout and US39 manager login retain their existing behaviour; the shared designer dashboard is integrated through InteriorDesignerLoginPage.openDashboard().
