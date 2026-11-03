# Control: SearchCompanyInformationController - UC18 Search company information (US18)

from entity.companyProfile import CompanyProfile


class SearchCompanyInformationController:
    # UC18 Search company information
    # no point searching if they don't have a company profile yet
    def hasCompanyProfile(self, designerId):
        return CompanyProfile().getCompanyProfile(designerId) is not None

    # UC18 Search company information
    # searches only this designer's own profile, the page already trimmed the keyword
    def searchCompanyInformation(self, designerId, keyword):
        return CompanyProfile().searchCompanyInformation(designerId, keyword)
