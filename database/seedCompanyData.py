# US14 demo data: 100 company profiles, each owned by a separate demo designer.
# Run after database.seedData. Re-running does not duplicate existing profiles.

from database.db import getConnection, initDatabase
from entity.userAccount import UserAccount
from control.createCompanyProfileController import CreateCompanyProfileController
from entity.companyProfile import CompanyProfile


def seedCompanyData():
    initDatabase()
    conn = getConnection()
    profile = conn.execute("SELECT profileId FROM user_profile WHERE profileName = ?",
                           ("Interior Designer",)).fetchone()
    conn.close()
    if profile is None:
        raise RuntimeError("Run python -m database.seedData first")
    control = CreateCompanyProfileController()
    created = 0
    for number in range(1, 101):
        username = "companydemo" + str(number).zfill(3)
        if not UserAccount().isUsernameTaken(username):
            UserAccount().createUserAccount(username, "Demo@123", "Demo Designer " + str(number),
                                           username + "@example.com", "", profile["profileId"])
        conn = getConnection()
        account = conn.execute("SELECT userId FROM user_account WHERE username = ?", (username,)).fetchone()
        conn.close()
        if account and not control.hasCompanyProfile(account["userId"]):
            company = CompanyProfile(designerId=account["userId"],
                                     companyName="Demo Interiors " + str(number),
                                     description="Residential interior design company " + str(number),
                                     services="Space planning, renovation, furniture selection",
                                     email=username + "@example.com", phone="", address="")
            if control.createCompanyProfile(company):
                created += 1
    return created


if __name__ == "__main__":
    print("Company profiles created:", seedCompanyData())
