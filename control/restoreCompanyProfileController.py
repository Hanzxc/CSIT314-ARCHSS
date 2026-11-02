# Control: RestoreCompanyProfileController - UC17 Delete company profile, restore (US17)
# US17 recovery: restore only the authenticated designer's own suspended company.
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class RestoreCompanyProfileController:
    # UC17 Delete company profile, restore
    # only an active interior designer can restore their company profile
    def canRestoreCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    # UC17 Delete company profile, restore
    # gets the designer's deleted (suspended) profile, if they have one
    def getSuspendedCompanyProfile(self, designerId):
        if not self.canRestoreCompanyProfile(designerId):
            return None
        return CompanyProfile().getSuspendedCompanyProfile(designerId)

    # UC17 Delete company profile, restore
    # makes the suspended profile Active again
    def restoreCompanyProfile(self, designerId, companyId, expectedRevision):
        if not self.canRestoreCompanyProfile(designerId):
            return False
        return CompanyProfile().restoreCompanyProfile(designerId, companyId, expectedRevision)
