# Control: DeleteCurrentIDPController - UC23 Delete current IDP (US23)
# precondition: the designer is already logged in (US13), so there's no access check here

from entity.idp import IDP


class DeleteCurrentIDPController:
    # UC23 Delete current IDP
    # US23's own loader for the confirmation box - None if it isn't the designer's Active Current IDP
    def getCurrentIDP(self, designerId, idpId):
        return IDP().getCurrentIDP(designerId, idpId)

    # UC23 Delete current IDP
    # soft delete - the entity only suspends the owner's Active Current IDP
    def deleteCurrentIDP(self, designerId, idpId):
        return IDP().suspendCurrentIDP(designerId, idpId)
