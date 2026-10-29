# US20 / US41 - US45 demo data: default IDP categories, plus a few current IDPs
# owned by the companydemo designers (from database.seedCompanyData) if they exist.
# Run after database.seedData. Re-running does not duplicate existing rows.
# run with:  python -m database.seedIDPCategoryData

from database.db import getConnection, initDatabase
from entity.idp import IDP
from entity.idpCategory import IDPCategory

DEFAULT_CATEGORIES = [
    ("Living Room", "Lounges, family rooms and TV areas"),
    ("Kitchen", "Cooking and dining spaces"),
    ("Bedroom", "Master, children's and guest bedrooms"),
    ("Bathroom", "Bathrooms, toilets and powder rooms"),
    ("Home Office", "Study rooms and work-from-home corners"),
    ("Commercial", "Offices, shops and restaurants"),
]

# title, category name, description, location
DEMO_IDPS = [
    ("Tampines HDB kitchen", "Kitchen", "Open-concept kitchen, now at the carpentry stage.", "Tampines"),
    ("Bishan condo living room", "Living Room", "Warm minimalist living room with built-in shelves.", "Bishan"),
    ("Punggol master bedroom", "Bedroom", "Walk-in wardrobe and feature wall in progress.", "Punggol"),
    ("Jurong cafe fit-out", "Commercial", "Industrial-style cafe, lighting being installed.", "Jurong East"),
]


def seedIDPCategoryData():
    initDatabase()
    created = 0
    for categoryName, description in DEFAULT_CATEGORIES:
        if not IDPCategory().isCategoryNameTaken(categoryName):
            if IDPCategory().createIDPCategory(categoryName, description):
                created += 1

    added = 0
    for number, (title, categoryName, description, location) in enumerate(DEMO_IDPS, start=1):
        conn = getConnection()
        account = conn.execute("SELECT userId FROM user_account WHERE username = ?",
                               ("companydemo" + str(number).zfill(3),)).fetchone()
        exists = conn.execute("SELECT 1 FROM idp WHERE title = ?", (title,)).fetchone()
        conn.close()
        if account is None or exists:
            continue
        category = next(c for c in IDPCategory().searchIDPCategories(categoryName)
                        if c.categoryName == categoryName)
        idpData = {"title": title, "description": description,
                   "categoryId": category.categoryId, "location": location}
        if IDP().addCurrentIDP(account["userId"], idpData):
            added += 1
    return created, added


if __name__ == "__main__":
    created, added = seedIDPCategoryData()
    print("IDP categories created:", created, "| current IDPs added:", added)
