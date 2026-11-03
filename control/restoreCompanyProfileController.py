# Control: RestoreCompanyProfileController - UC17 Delete company profile, restore (US17)

from entity.companyProfile import CompanyProfile


class RestoreCompanyProfileController:
    # UC17 Delete company profile, restore
    # gets the designer's deleted (suspended) profile, if they have one
    def getSuspendedCompanyProfile(self, designerId):
        return CompanyProfile().getSuspendedCompanyProfile(designerId)

    # UC17 Delete company profile, restore
    # makes the suspended profile Active again
    def restoreCompanyProfile(self, designerId, companyId, expectedRevision):
        return CompanyProfile().restoreCompanyProfile(designerId, companyId, expectedRevision)
