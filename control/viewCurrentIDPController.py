# Control: ViewCurrentIDPController - UC21 View current IDPs (US21)
# precondition: the designer is already logged in (US13), so there's no access check here

from entity.idp import IDP


class ViewCurrentIDPController:
    # UC21 View current IDPs
    # the owner's Active Current IDPs (in Active categories), newest first
    def viewCurrentIDPs(self, designerId):
        return IDP().getCurrentIDPs(designerId)

    # UC21 View current IDPs
    # one of the owner's current IDPs, or None if it isn't theirs / isn't available
    def viewCurrentIDP(self, designerId, idpId):
        return IDP().getCurrentIDP(designerId, idpId)
