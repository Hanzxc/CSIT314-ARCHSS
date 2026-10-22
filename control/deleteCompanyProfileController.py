# Control: DeleteCompanyProfileController - UC17 Delete company profile (US17)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class DeleteCompanyProfileController:
    def canDeleteCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def getCompanyProfile(self, designerId):
        if not self.canDeleteCompanyProfile(designerId):
            return None
        return CompanyProfile().getCompanyProfile(designerId)

    def deleteCompanyProfile(self, designerId, companyId):
        if not self.canDeleteCompanyProfile(designerId):
            return False
        return CompanyProfile().deleteCompanyProfile(designerId, companyId)
