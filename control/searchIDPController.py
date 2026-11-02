"""US31: authenticated customer search of the visible IDP catalogue."""
from control.customerLoginController import CustomerLoginController
from entity.idp import IDP


class SearchIDPController:
    def getCustomer(self, customerId):
        return CustomerLoginController().getAuthenticatedCustomer(customerId)

    def searchIDPs(self, customerId, keyword):
        if self.getCustomer(customerId) is None:
            raise PermissionError("Customer access unavailable")
        return IDP().searchIDPs((keyword or "").strip())
