# Control: DeleteCompanyProfileController - UC17 Delete company profile (US17)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class DeleteCompanyProfileController:
    # UC17 Delete company profile
    # only an active interior designer can delete their company profile
    def canDeleteCompanyProfile(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    # UC17 Delete company profile
    # gets the designer's own profile, so the page can ask "are you sure?"
    def getCompanyProfile(self, designerId):
        if not self.canDeleteCompanyProfile(designerId):
            return None
        return CompanyProfile().getCompanyProfile(designerId)

    # UC17 Delete company profile
    # "deleting" really just suspends it, so it can be restored later
    def deleteCompanyProfile(self, designerId, companyId, expectedRevision=None):
        if not self.canDeleteCompanyProfile(designerId):
            return False
        return CompanyProfile().suspendCompanyProfile(designerId, companyId, expectedRevision)
