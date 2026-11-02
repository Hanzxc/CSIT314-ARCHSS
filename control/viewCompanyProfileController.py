# Control: ViewCompanyProfileController - UC15 View company profile (US15)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class ViewCompanyProfileController:
    # UC15 View company profile
    # only an active interior designer can view their company profile
    def canViewCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    # UC15 View company profile
    # returns the designer's own active profile, or None
    def viewCompanyProfile(self, designerId):
        if not self.canViewCompanyProfile(designerId):
            return None
        return CompanyProfile().getCompanyProfile(designerId)
