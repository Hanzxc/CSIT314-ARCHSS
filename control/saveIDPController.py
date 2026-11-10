# Control: SaveIDPController - UC33 Save IDP (US33)

from entity.savedIDP import SavedIDP


class SaveIDPController:
    # UC33 Save IDP
    # adds it to the saved list - the entity refuses duplicates and IDPs customers can't see
    def saveIDP(self, customerId, idpId):
        return SavedIDP().createSavedRecord(customerId, idpId)
