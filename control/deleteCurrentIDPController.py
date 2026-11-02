# Control: DeleteCurrentIDPController - UC23 Delete current IDP.
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP


class DeleteCurrentIDPController:
    def canDeleteCurrentIDP(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def getCurrentIDP(self, designerId, idpId):
        if not self.canDeleteCurrentIDP(designerId):
            raise PermissionError("Designer access unavailable")
        return IDP().getCurrentIDP(designerId, idpId)

    def deleteCurrentIDP(self, designerId, idpId, expectedSnapshot=None):
        if not self.canDeleteCurrentIDP(designerId):
            raise PermissionError("Designer access unavailable")
        return IDP().suspendCurrentIDP(designerId, idpId, expectedSnapshot)

    def getSnapshot(self, idp):
        return idp.getSnapshot()
