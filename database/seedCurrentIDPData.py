# Optional US21 demo records. Run after: python -m database.seedData
# Re-running preserves existing records, including their current visibility/status.
from database.db import getConnection, initDatabase
from entity.userAccount import UserAccount


def seedCurrentIDPData():
    initDatabase()
    conn = getConnection()
    try:
        profile = conn.execute("SELECT profileId FROM user_profile WHERE profileName = ?",
                               ("Interior Designer",)).fetchone()
    finally:
        conn.close()
    if profile is None:
        raise RuntimeError("Run python -m database.seedData first")

    for username in ("idpdemo001", "idpdemo002"):
        if not UserAccount().isUsernameTaken(username):
            newAccount = UserAccount(username=username, password="Demo@123", fullName="IDP Demo Designer " + username[-3:],
                                     email=username + "@example.com", phone="", profileId=profile["profileId"])
            UserAccount().createUserAccount(newAccount)

    conn = getConnection()
    created = 0
    try:
        for name in ("Living Room", "Kitchen"):
            conn.execute("INSERT INTO idp_category (categoryName) SELECT ? "
                         "WHERE NOT EXISTS (SELECT 1 FROM idp_category WHERE categoryName=?)", (name, name))
        examples = [("Warm Minimalist Apartment", "Living Room", "Tampines"),
                    ("Modern Kitchen Renovation", "Kitchen", "Bedok")]
        for username in ("idpdemo001", "idpdemo002"):
            owner = conn.execute("SELECT userId FROM user_account WHERE username=?", (username,)).fetchone()
            for title, name, location in examples:
                category = conn.execute("SELECT categoryId FROM idp_category WHERE categoryName=?", (name,)).fetchone()
                cursor = conn.execute(
                    "INSERT INTO idp (designerId, categoryId, title, description, location) "
                    "SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS "
                    "(SELECT 1 FROM idp WHERE designerId=? AND title=?)",
                    (owner["userId"], category["categoryId"], title,
                     "Natural wood finishes, neutral colours and practical storage. Work is in progress.",
                     location, owner["userId"], title))
                created += cursor.rowcount
        conn.commit()
    finally:
        conn.close()
    return created


if __name__ == "__main__":
    print("Current IDPs created:", seedCurrentIDPData())
    print("Designer login: idpdemo001 / Demo@123 (or idpdemo002 / Demo@123)")
