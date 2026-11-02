# Control: SearchCurrentIDPController - UC24 Search current IDPs.
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP


class SearchCurrentIDPController:
    def canSearchCurrentIDPs(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def searchCurrentIDPs(self, designerId, keyword):
        if not self.canSearchCurrentIDPs(designerId):
            raise PermissionError("Designer access unavailable")
        return IDP().searchCurrentIDPs(designerId, (keyword or "").strip())
