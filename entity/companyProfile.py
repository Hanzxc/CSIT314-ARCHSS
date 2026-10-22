# Entity: CompanyProfile - UC14 Create company profile (US14)

import sqlite3

from database.db import getConnection

COMPANY_FIELDS = ("companyName", "description", "services", "email", "phone", "address")
COMPANY_SEARCH_LABELS = (
    ("companyName", "Company name"), ("description", "Company description"),
    ("services", "Services offered"), ("email", "Contact email"),
    ("phone", "Contact phone"), ("address", "Company address"),
)


class CompanyProfile:
    def __init__(self, companyId=None, designerId=None, companyName="", description="",
                 services="", email="", phone="", address="", createdDate=None):
        self.companyId = companyId
        self.designerId = designerId
        self.companyName = companyName
        self.description = description
        self.services = services
        self.email = email
        self.phone = phone
        self.address = address
        self.createdDate = createdDate

    def getCompanyProfile(self, designerId):
        conn = getConnection()
        row = conn.execute("SELECT * FROM company_profile WHERE designerId = ?", (designerId,)).fetchone()
        conn.close()
        if row is None:
            return None
        return CompanyProfile(**dict(row))

    def createCompanyProfile(self, designerId, companyData):
        conn = getConnection()
        try:
            values = [companyData.get(field, "").strip() for field in COMPANY_FIELDS]
            cursor = conn.execute(
                "INSERT INTO company_profile (designerId, companyName, description, services, email, phone, address) "
                "SELECT ?, ?, ?, ?, ?, ?, ? WHERE EXISTS (SELECT 1 FROM user_account WHERE userId = ?)",
                (designerId, *values, designerId))
            conn.commit()
            created = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            created = False
        finally:
            conn.close()
        return created

    # US16: update only business fields; owner, primary key and creation time stay unchanged.
    def updateCompanyProfile(self, designerId, companyData):
        conn = getConnection()
        try:
            values = [companyData.get(field, "").strip() for field in COMPANY_FIELDS]
            cursor = conn.execute(
                "UPDATE company_profile SET companyName = ?, description = ?, services = ?, "
                "email = ?, phone = ?, address = ? WHERE designerId = ?",
                (*values, designerId))
            conn.commit()
            updated = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            updated = False
        finally:
            conn.close()
        return updated

    # US17: match both owner and the specific record shown in the confirmation.
    def deleteCompanyProfile(self, designerId, companyId):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "DELETE FROM company_profile WHERE designerId = ? AND companyId = ?",
                (designerId, companyId))
            conn.commit()
            deleted = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            deleted = False
        finally:
            conn.close()
        return deleted

    # US18: search only the owner's six business fields; no wildcard interpretation.
    def searchCompanyInformation(self, designerId, keyword):
        profile = self.getCompanyProfile(designerId)
        if profile is None:
            return []
        query = (keyword or "").strip().casefold()
        results = []
        for field, label in COMPANY_SEARCH_LABELS:
            value = getattr(profile, field) or ""
            if not query or query in label.casefold() or query in value.casefold():
                results.append({"field": field, "label": label, "value": value})
        return results
