"""US32: customer detail view and the designer's public company information."""
from control.customerLoginController import CustomerLoginController
from entity.companyProfile import CompanyProfile
from entity.idp import IDP
from entity.savedIDP import SavedIDP


class ViewIDPController:
    def getCustomer(self, customerId):
        return CustomerLoginController().getAuthenticatedCustomer(customerId)

    def viewIDP(self, customerId, idpId):
        if self.getCustomer(customerId) is None:
            raise PermissionError("Customer access unavailable")
        idp = IDP().getIDP(idpId)
        if idp is None:
            return None
        return {"idp": idp,
                "companyProfile": CompanyProfile().getCompanyProfile(idp.designerId),
                "isSaved": SavedIDP().isSaved(customerId, idp.idpId)}
