# Control: RestoreCompanyProfileController - UC17-R Restore company profile (US17)

from entity.companyProfile import CompanyProfile


class RestoreCompanyProfileController:
    # UC17-R Restore company profile
    # gets the designer's deleted (suspended) profile, if they have one - US13's dashboard
    # uses it to show the Restore button
    def getSuspendedCompanyProfile(self, designerId):
        return CompanyProfile().getSuspendedCompanyProfile(designerId)

    # UC17-R Restore company profile
    # makes the suspended profile Active again (only if expectedRevision still matches)
    def restoreCompanyProfile(self, designerId, companyId, expectedRevision):
        return CompanyProfile().restoreCompanyProfile(designerId, companyId, expectedRevision)
