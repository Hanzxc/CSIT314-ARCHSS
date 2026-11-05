# User Stories 37, 38, 46, 47 and 48

## What changed
- US37: /designer/idps/statistics/views, counts actual visits to IDP details.
- US38: /designer/idps/statistics/saves, shows distinct customers currently saving each designer-owned IDP.
- US46: /manager/reports/daily?date=YYYY-MM-DD
- US47: /manager/reports/weekly?date=YYYY-MM-DD (Monday to Sunday)
- US48: /manager/reports/monthly?date=YYYY-MM-DD
- /idps and /idps/<id> public listing/detail route to capture view events until the Customer viewing story is merged.
- Uses the existing `idp`, `saved_idp`, `idp_category`, `user_account` tables.
- One added `idp_view` table in `database/schema.sql`. Run `initDatabase()` or `python app.py` before using.

## How to run
1. Install dependencies: `python -m pip install -r requirements.txt`
2. Initialize or seed as you ordinarily do (`python -m database.seedData`).
3. Start: `python app.py`
4. Open the designer and manager dashboards. New links appear in the sidebars.
5. To create real view counts, open an active IDP through `/idps`.
6. Saves are based on entries your teammate's US33 implementation adds to `saved_idp`.

## Important integration caveats
- This repository has no customer-facing detail-view route or customer-facing login.
  `/idps` and `/idps/<id>` are standalone interim viewer routes and currently public.
  Integrate the `record_project_view()` call into the actual IDP detail page when available.
  The viewer counts page loads, not unique humans, and refreshes count as additional views.
- US38 is **current bookmarks** only. If customers unsave projects, saved_idp deletes
  the row. Past save events cannot be reconstructed from this table.
- US46-48 show views during the chosen period and **currently existing saves that
  were created during that period**. These are not lifetime engagement or historical
  unsave records. Rankings are based on views, followed by saves.
- All reporting timestamps use SQLite UTC CURRENT_TIMESTAMP. The selected date
  is consequently interpreted as a UTC day/week/month, not Singapore local time.
- Category 'Active IDPs' means the currently active portfolio count, not projects
  created during that period. Suspended categories remain visible for reporting.
- Both statistics and manager reports check the authenticated user's role against
  existing login controllers, rather than blindly trusting session contents.
- Do not claim integration or manual UI tests passed until they are run on the team's environment.

## Changed files
- app.py
- database/schema.sql
- entity/idpAnalytics.py
- control/idpAnalyticsController.py
- boundary/idpAnalyticsPage.py
- templates/idpStatistics.html, idpCategoryReport.html, idpGallery.html, idpDetails.html
- templates/interiorDesignerBase.html, interiorDesignerDashboard.html
- templates/platformManagerBase.html, platformManagerDashboard.html
- static/style.css
- tests/test_us37_38_46_47_48.py
