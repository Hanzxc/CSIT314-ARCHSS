# Control: ViewPastIDPController - UC26 View past IDPs (US26)

from entity.idp import IDP


class ViewPastIDPController:
    # UC26 View past IDPs
    # the logged-in designer's past IDPs (the page passes in session["userId"])
    def getPastIDPs(self, designerId):
        return IDP().findPastIDPsByDesignerId(designerId)

    # UC26 View past IDPs
    # one of the designer's past IDPs, or None if it isn't theirs / doesn't exist
    def getPastIDPDetails(self, designerId, idpId):
        return IDP().getPastIDPDetails(designerId, idpId)
