# Control: UpdateCompanyProfileController - UC16 Update company profile (US16)

from entity.companyProfile import CompanyProfile


class UpdateCompanyProfileController:
    # UC16 Update company profile
    # gets the designer's current details to fill in the form
    def getCompanyProfile(self, designerId):
        return CompanyProfile().getCompanyProfile(designerId)

    # UC16 Update company profile
    # the page checks the input - this just calls update
    def updateCompanyProfile(self, companyProfile):
        return CompanyProfile().updateCompanyProfile(companyProfile)
