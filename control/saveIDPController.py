# Control: SaveIDPController - UC33 Save IDP (US33)

from entity.savedIDP import SavedIDP


class SaveIDPController:
    # UC33 Save IDP
    # true if the IDP is already in the customer's saved list (alt flow A1)
    def checkAlreadySaved(self, customerId, idpId):
        return SavedIDP().exists(customerId, idpId)

    # UC33 Save IDP
    # adds it to the saved list - the entity refuses duplicates and IDPs customers can't see
    def saveIDP(self, customerId, idpId):
        return SavedIDP().createSavedRecord(customerId, idpId)
