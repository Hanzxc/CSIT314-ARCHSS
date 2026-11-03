# Control: DeleteCompanyProfileController - UC17 Delete company profile (US17)

from entity.companyProfile import CompanyProfile


class DeleteCompanyProfileController:
    # UC17 Delete company profile
    # gets the designer's own profile, so the page can ask "are you sure?"
    def getCompanyProfile(self, designerId):
        return CompanyProfile().getCompanyProfile(designerId)

    # UC17 Delete company profile
    # "deleting" really just suspends it, so it can be restored later
    def deleteCompanyProfile(self, designerId, companyId, expectedRevision=None):
        return CompanyProfile().suspendCompanyProfile(designerId, companyId, expectedRevision)
