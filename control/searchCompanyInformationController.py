# Control: SearchCompanyInformationController - UC18 Search company information (US18)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class SearchCompanyInformationController:
    # UC18 Search company information
    # only an active interior designer can search their company info
    def canSearchCompanyInformation(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    # UC18 Search company information
    # no point searching if they don't have a company profile yet
    def hasCompanyProfile(self, designerId):
        if not self.canSearchCompanyInformation(designerId):
            return False
        return CompanyProfile().getCompanyProfile(designerId) is not None

    # UC18 Search company information
    # searches only this designer's own profile, spaces around the keyword are ignored
    def searchCompanyInformation(self, designerId, keyword):
        if not self.canSearchCompanyInformation(designerId):
            return []
        keyword = (keyword or "").strip()
        return CompanyProfile().searchCompanyInformation(designerId, keyword)
