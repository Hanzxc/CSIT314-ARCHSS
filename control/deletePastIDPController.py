# Control: DeletePastIDPController - UC28 Delete past IDP (US28)

from entity.idp import IDP


class DeletePastIDPController:
    # UC28 Delete past IDP
    # the past IDP shown in the "are you sure?" box, or None if it isn't the designer's
    def getPastIDP(self, designerId, idpId):
        return IDP().getPastIDPDetails(designerId, idpId)

    # UC28 Delete past IDP
    # the entity marks it unavailable (status Suspended) - true if it was deleted
    def deletePastIDP(self, designerId, idpId):
        return IDP().markPastIDPUnavailable(designerId, idpId)
