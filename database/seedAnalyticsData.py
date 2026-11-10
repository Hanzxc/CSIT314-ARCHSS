# Optional US37 / US38 / US46 - US48 demo data: IDP views and saves, so the statistics pages and the
# daily / weekly / monthly reports don't show all zeros in a fresh demo.
# Run after database.seedData and the IDP seeds (seedIDPCategoryData / seedCurrentIDPData).
# Re-running doesn't add more: views are skipped if the table already has some, and saves can't duplicate.
# run with:  python -m database.seedAnalyticsData

import random
from datetime import datetime, timedelta, timezone

from database.db import getConnection, initDatabase

DAYS_BACK = 60      # views / saves are spread over the last 60 days (so every report period has some)


def seedAnalyticsData():
    initDatabase()
    rng = random.Random(314)          # same numbers every time
    saveRng = random.Random(315)      # own generator, so a re-run picks the same saves (then ignored)
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)   # the DB stores UTC
    conn = getConnection()
    views = 0
    saves = 0
    try:
        # only IDPs customers can actually see (Active IDP in an Active category), like US32 / US33
        idps = [row["idpId"] for row in conn.execute(
            "SELECT idp.idpId FROM idp JOIN idp_category c ON c.categoryId = idp.categoryId "
            "WHERE idp.status = 'Active' AND c.status = 'Active' ORDER BY idp.idpId")]
        customers = [row["userId"] for row in conn.execute(
            "SELECT a.userId FROM user_account a JOIN user_profile p ON p.profileId = a.profileId "
            "WHERE p.profileName = 'Customer' AND a.status = 'Active' ORDER BY a.userId")]
        if not idps:
            raise RuntimeError("No IDPs yet - run python -m database.seedIDPCategoryData or seedCurrentIDPData first")

        # views only go in once - if the table already has some, a re-run skips them all
        if not conn.execute("SELECT 1 FROM idp_view LIMIT 1").fetchone():
            for idpId in idps:
                for _ in range(rng.randint(0, 15)):
                    viewedAt = now - timedelta(days=rng.randint(0, DAYS_BACK), minutes=rng.randint(0, 600))
                    conn.execute("INSERT INTO idp_view (idpId, viewedAt) VALUES (?, ?)",
                                 (idpId, viewedAt.strftime("%Y-%m-%d %H:%M:%S")))
                    views += 1

        for customerId in customers[:20]:
            for idpId in saveRng.sample(idps, min(len(idps), saveRng.randint(0, 3))):
                savedDate = now - timedelta(days=saveRng.randint(0, DAYS_BACK), minutes=saveRng.randint(0, 600))
                cursor = conn.execute("INSERT OR IGNORE INTO saved_idp (customerId, idpId, savedDate) VALUES (?, ?, ?)",
                                      (customerId, idpId, savedDate.strftime("%Y-%m-%d %H:%M:%S")))
                saves += cursor.rowcount
        conn.commit()
    finally:
        conn.close()
    return views, saves


if __name__ == "__main__":
    views, saves = seedAnalyticsData()
    print("IDP views added:", views, "| saves added:", saves)
    print("See them as a designer (IDP statistics) or a platform manager (Reports, e.g. pm005 / Pass@123)")
