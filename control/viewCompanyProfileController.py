# Control: ViewCompanyProfileController - UC15 View company profile (US15)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class ViewCompanyProfileController:
    def canViewCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def viewCompanyProfile(self, designerId):
        if not self.canViewCompanyProfile(designerId):
            return None
        return CompanyProfile().getCompanyProfile(designerId)
