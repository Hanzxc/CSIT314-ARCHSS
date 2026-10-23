# US17 recovery: restore only the authenticated designer's own suspended company.
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class RestoreCompanyProfileController:
    def canRestoreCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def getSuspendedCompanyProfile(self, designerId):
        if not self.canRestoreCompanyProfile(designerId):
            return None
        return CompanyProfile().getSuspendedCompanyProfile(designerId)

    def restoreCompanyProfile(self, designerId, companyId, expectedRevision):
        if not self.canRestoreCompanyProfile(designerId):
            return False
        return CompanyProfile().restoreCompanyProfile(designerId, companyId, expectedRevision)
