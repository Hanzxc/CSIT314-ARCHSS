# Control: CreateCompanyProfileController - UC14 Create company profile (US14)

import re

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile

FIELD_LIMITS = {"companyName": 100, "description": 2000, "services": 1000,
                "email": 254, "phone": 30, "address": 300}


class CreateCompanyProfileController:
    # UC14 Create company profile
    # only an active interior designer can make a company profile
    def canCreateCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    # UC14 Create company profile
    # true if this designer already has an active company profile
    def hasCompanyProfile(self, designerId):
        return CompanyProfile().getCompanyProfile(designerId) is not None

    # UC14 Create company profile
    # checks every field (required ones, max lengths, email format) and returns the errors
    def getFieldErrors(self, companyData):
        errors = {}
        for field, limit in FIELD_LIMITS.items():
            value = companyData.get(field, "").strip()
            if field in ("companyName", "description", "services") and not value:
                errors[field] = "This field is required"
            elif len(value) > limit:
                errors[field] = "Maximum " + str(limit) + " characters"
        name = companyData.get("companyName", "").strip()
        if name and len(name) < 3:
            errors["companyName"] = "Company name must be 3-100 characters"
        email = companyData.get("email", "").strip()
        if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            errors["email"] = "Enter a valid email address"
        return errors

    # UC14 Create company profile
    # saves the profile, but only if the designer is allowed, the input is ok and they don't have one yet
    def createCompanyProfile(self, designerId, companyData):
        if not self.canCreateCompanyProfile(designerId) or self.getFieldErrors(companyData):
            return False
        if self.hasCompanyProfile(designerId):
            return False
        return CompanyProfile().createCompanyProfile(designerId, companyData)
