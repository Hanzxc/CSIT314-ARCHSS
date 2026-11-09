# Control: SearchCompanyInformationController - UC18 Search company information (US18)

from entity.companyProfile import CompanyProfile


class SearchCompanyInformationController:
    # UC18 Search company information
    # searches only this designer's own profile, the page already trimmed the keyword.
    # gives back None (no profile) or the CompanyProfile with its matchedFields
    def searchCompanyInformation(self, designerId, keyword):
        return CompanyProfile().searchCompanyInformation(designerId, keyword)
