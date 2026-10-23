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

    def getCompanyProfile(self, designerId):
        conn = getConnection()
        row = conn.execute("SELECT * FROM company_profile WHERE designerId = ? AND status = 'Active'", (designerId,)).fetchone()
        conn.close()
        if row is None:
            return None
        return CompanyProfile(**dict(row))

    def getSuspendedCompanyProfile(self, designerId):
        conn = getConnection()
        row = conn.execute(
            "SELECT * FROM company_profile WHERE designerId = ? AND status = 'Suspended'",
            (designerId,)).fetchone()
        conn.close()
        return CompanyProfile(**dict(row)) if row is not None else None

    def restoreCompanyProfile(self, designerId, companyId, expectedRevision):
        # Restore exactly the saved record; no submitted business fields are accepted.
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE company_profile SET status = 'Active', revision = revision + 1 "
                "WHERE designerId = ? AND companyId = ? AND status = 'Suspended' AND revision = ?",
                (designerId, companyId, expectedRevision))
            conn.commit()
            restored = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            restored = False
        finally:
            conn.close()
        return restored

    def createCompanyProfile(self, designerId, companyData):
        conn = getConnection()
        try:
            values = [companyData.get(field, "").strip() for field in COMPANY_FIELDS]
            # One row per owner. Reactivation preserves its ID and creation date.
            # A single atomic UPSERT prevents duplicate active profiles.
            cursor = conn.execute(
                "INSERT INTO company_profile (designerId, companyName, description, services, email, phone, address) "
                "SELECT ?, ?, ?, ?, ?, ?, ? WHERE EXISTS (SELECT 1 FROM user_account WHERE userId = ?) "
                "ON CONFLICT(designerId) DO UPDATE SET companyName = excluded.companyName, "
                "description = excluded.description, services = excluded.services, email = excluded.email, "
                "phone = excluded.phone, address = excluded.address, status = 'Active', "
                "revision = company_profile.revision + 1 WHERE company_profile.status = 'Suspended'",
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
                "email = ?, phone = ?, address = ? WHERE designerId = ? AND status = 'Active'",
                (*values, designerId))
            conn.commit()
            updated = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            updated = False
        finally:
            conn.close()
        return updated

    # US17: preserve the row and suspend only an active, exact owner/record match.
    def suspendCompanyProfile(self, designerId, companyId, expectedRevision=None):
        conn = getConnection()
        try:
            sql = ("UPDATE company_profile SET status = 'Suspended' "
                   "WHERE designerId = ? AND companyId = ? AND status = 'Active'")
            params = [designerId, companyId]
            if expectedRevision is not None:
                sql += " AND revision = ?"
                params.append(expectedRevision)
            cursor = conn.execute(sql, params)
            conn.commit()
            suspended = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            suspended = False
        finally:
            conn.close()
        return suspended

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
