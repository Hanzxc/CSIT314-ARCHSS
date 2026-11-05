# Control: saveIDPController - UC33 Save / Bookmark IDP
from entity.savedIDP import SavedIDP

class SaveIDPController:
    def __init__(self):
        self.savedEntity = SavedIDP()

    def toggleSaveIDP(self, customerId, idpId):
        # Validation checks
        if not customerId or not idpId:
            return False, False, "Invalid user session or project ID."

        # Delegate toggle action to Entity layer
        is_saved = self.savedEntity.toggleSaveIDP(customerId, int(idpId))

        if is_saved:
            return True, True, "IDP saved to your favourites."
        else:
            return True, False, "IDP removed from your saved list."