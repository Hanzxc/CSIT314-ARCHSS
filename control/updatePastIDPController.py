# Control: UpdatePastIDPController - UC27 Update past IDP (US27)

from entity.idp import IDP


class UpdatePastIDPController:
    # UC27 Update past IDP
    # the past IDP to fill the edit form with, or None if it isn't the designer's
    def getPastIDP(self, designerId, idpId):
        return IDP().getPastIDPDetails(designerId, idpId)

    # UC27 Update past IDP
    # the page checks the input, the entity only updates the owner's Active past IDP - this just calls update
    def updatePastIDP(self, idp):
        return IDP().updatePastIDPDetails(idp)
