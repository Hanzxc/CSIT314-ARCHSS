# Control: CreateCompanyProfileController - UC14 Create company profile (US14)

from entity.companyProfile import CompanyProfile


class CreateCompanyProfileController:
    # UC14 Create company profile
    # true if this designer already has an active company profile
    def hasCompanyProfile(self, designerId):
        return CompanyProfile().getCompanyProfile(designerId) is not None

    # UC14 Create company profile
    # the page checks the input, the entity checks for a duplicate - this just calls create
    def createCompanyProfile(self, companyProfile):
        return CompanyProfile().createCompanyProfile(companyProfile)
