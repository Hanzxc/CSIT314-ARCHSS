# Entity: CompanyProfile - UC14 Create company profile (US14)

from database.db import getConnection

COMPANY_SEARCH_LABELS = (
    ("companyName", "Company name"), ("description", "Company description"),
    ("services", "Services offered"), ("email", "Contact email"),
    ("phone", "Contact phone"), ("address", "Company address"),
)


class CompanyProfile:
    # used by UC14 - UC18
    # one company profile = one row in the company_profile table
    def __init__(self, companyId=None, designerId=None, companyName="", description="",
                 services="", email="", phone="", address="", createdDate=None,
                 status="Active", revision=1):
        self.companyId = companyId
        self.designerId = designerId
        self.companyName = companyName
        self.description = description
        self.services = services
        self.email = email
        self.phone = phone
        self.address = address
        self.createdDate = createdDate
        self.status = status
        self.revision = revision

    # used by UC14 - UC18
    # returns the designer's Active profile, or None if they don't have one
    def getCompanyProfile(self, designerId):
        conn = getConnection()
        row = conn.execute("SELECT * FROM company_profile WHERE designerId = ? AND status = 'Active'", (designerId,)).fetchone()
        conn.close()
        if row is None:
            return None
        return CompanyProfile(**dict(row))

    # UC17 Delete company profile (restore)
    # returns the designer's deleted (Suspended) profile, or None
    def getSuspendedCompanyProfile(self, designerId):
        conn = getConnection()
        row = conn.execute(
            "SELECT * FROM company_profile WHERE designerId = ? AND status = 'Suspended'",
            (designerId,)).fetchone()
        conn.close()
        return CompanyProfile(**dict(row)) if row is not None else None

    # UC17 Delete company profile (restore)
    # brings back exactly the saved record, nothing from the form is accepted.
    # revision goes up so an old delete confirmation can't be reused on it
    def restoreCompanyProfile(self, designerId, companyId, expectedRevision):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE company_profile SET status = 'Active', revision = revision + 1 "
            "WHERE designerId = ? AND companyId = ? AND status = 'Suspended' AND revision = ?",
            (designerId, companyId, expectedRevision))
        conn.commit()
        conn.close()
        return cursor.rowcount == 1

    # UC14 Create company profile
    # one company profile per designer - if they already have one (even a deleted/Suspended one)
    # it's a duplicate, so don't create. otherwise insert all the fields and commit.
    # the page already checked + tidied the input, so no strip here
    def createCompanyProfile(self, companyProfile):
        conn = getConnection()
        existing = conn.execute("SELECT companyId FROM company_profile WHERE designerId = ?",
                                (companyProfile.designerId,)).fetchone()
        if existing is not None:
            conn.close()
            return False

        conn.execute(
            "INSERT INTO company_profile (designerId, companyName, description, services, email, phone, address) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (companyProfile.designerId, companyProfile.companyName, companyProfile.description,
             companyProfile.services, companyProfile.email, companyProfile.phone, companyProfile.address))
        conn.commit()
        conn.close()
        return True

    # UC16 Update company profile
    # only the six business fields change - owner, id and created date stay the same.
    # 0 rows changed means they don't have an Active profile
    def updateCompanyProfile(self, companyProfile):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE company_profile SET companyName = ?, description = ?, services = ?, "
            "email = ?, phone = ?, address = ? WHERE designerId = ? AND status = 'Active'",
            (companyProfile.companyName, companyProfile.description, companyProfile.services,
             companyProfile.email, companyProfile.phone, companyProfile.address,
             companyProfile.designerId))
        conn.commit()
        conn.close()
        return cursor.rowcount == 1

    # UC17 Delete company profile
    # the row is kept and just marked Suspended - only if it's this owner's Active record
    def suspendCompanyProfile(self, designerId, companyId, expectedRevision=None):
        sql = ("UPDATE company_profile SET status = 'Suspended' "
               "WHERE designerId = ? AND companyId = ? AND status = 'Active'")
        params = [designerId, companyId]
        if expectedRevision is not None:
            sql += " AND revision = ?"
            params.append(expectedRevision)

        conn = getConnection()
        cursor = conn.execute(sql, params)
        conn.commit()
        conn.close()
        return cursor.rowcount == 1

    # UC18 Search company information
    # only looks in the owner's six business fields, capitals don't matter
    def searchCompanyInformation(self, designerId, keyword):
        profile = self.getCompanyProfile(designerId)
        if profile is None:
            return []
        query = keyword.casefold()
        results = []
        for field, label in COMPANY_SEARCH_LABELS:
            value = getattr(profile, field) or ""
            if not query or query in label.casefold() or query in value.casefold():
                results.append({"field": field, "label": label, "value": value})
        return results
