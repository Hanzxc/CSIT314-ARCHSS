# Control: ViewCurrentIDPController - UC21 View current IDPs.
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP


class ViewCurrentIDPController:
    def canViewCurrentIDPs(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def viewCurrentIDPs(self, designerId):
        if not self.canViewCurrentIDPs(designerId):
            raise PermissionError("Designer access unavailable")
        return IDP().getCurrentIDPs(designerId)

    def viewCurrentIDP(self, designerId, idpId):
        if not self.canViewCurrentIDPs(designerId):
            raise PermissionError("Designer access unavailable")
        return IDP().getCurrentIDP(designerId, idpId)
