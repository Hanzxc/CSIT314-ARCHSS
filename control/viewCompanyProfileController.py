# Control: ViewCompanyProfileController - UC15 View company profile (US15)

from entity.companyProfile import CompanyProfile


class ViewCompanyProfileController:
    # UC15 View company profile
    # returns the designer's own active profile, or None
    def viewCompanyProfile(self, designerId):
        return CompanyProfile().getCompanyProfile(designerId)
