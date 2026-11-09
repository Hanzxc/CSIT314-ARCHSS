# Control: UpdateCurrentIDPController - UC22 Update current IDP (US22)
# precondition: the designer is already logged in (US13), so there's no access check here.
# the field rules are the page's, and the category list is US45's (the page borrows that controller)

from entity.idp import IDP


class UpdateCurrentIDPController:
    # UC22 Update current IDP
    # US22's own loader for the form - None if it isn't the designer's Active Current IDP
    def getCurrentIDP(self, designerId, idpId):
        return IDP().getCurrentIDP(designerId, idpId)

    # UC22 Update current IDP
    # the page has already checked the input - the entity only updates the owner's Active row
    def updateCurrentIDP(self, idp):
        return IDP().updateCurrentIDP(idp)
