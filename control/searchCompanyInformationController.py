# Control: SearchCompanyInformationController - UC18 Search company information (US18)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.companyProfile import CompanyProfile


class SearchCompanyInformationController:
    def canSearchCompanyInformation(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def hasCompanyProfile(self, designerId):
        if not self.canSearchCompanyInformation(designerId):
            return False
        return CompanyProfile().getCompanyProfile(designerId) is not None

    def searchCompanyInformation(self, designerId, keyword):
        if not self.canSearchCompanyInformation(designerId):
            return []
        keyword = (keyword or "").strip()
        return CompanyProfile().searchCompanyInformation(designerId, keyword)
