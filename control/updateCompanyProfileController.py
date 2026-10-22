# Control: UpdateCompanyProfileController - UC16 Update company profile (US16)

from control.createCompanyProfileController import CreateCompanyProfileController
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class UpdateCompanyProfileController:
    def canUpdateCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def getCompanyProfile(self, designerId):
        if not self.canUpdateCompanyProfile(designerId):
            return None
        return CompanyProfile().getCompanyProfile(designerId)

    def getFieldErrors(self, companyData):
        # Keep the same field rules as US14 instead of defining different rules for editing.
        return CreateCompanyProfileController().getFieldErrors(companyData)

    def updateCompanyProfile(self, designerId, companyData):
        if not self.canUpdateCompanyProfile(designerId) or self.getFieldErrors(companyData):
            return False
        return CompanyProfile().updateCompanyProfile(designerId, companyData)
