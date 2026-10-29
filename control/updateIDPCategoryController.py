# Control: UpdateIDPCategoryController - UC43 Update IDP category (US43)

from control.platformManagerLoginController import PlatformManagerLoginController
from entity.idpCategory import IDPCategory


class UpdateIDPCategoryController:
    def canUpdateIDPCategory(self, managerId):
        return PlatformManagerLoginController().getAuthenticatedManager(managerId) is not None

    # loads the current details into the form
    def getIDPCategory(self, categoryId):
        return IDPCategory().getIDPCategory(categoryId)

    # UT43.3 to UT43.8
    def updateIDPCategory(self, categoryId, categoryName, description):
        # same as create - don't rely on the page having checked it (UT43.6)
        if not categoryName or not categoryName.strip():
            return False

        # pass categoryId in so it doesn't count its OWN name as taken (seq diagram msgs 16-17)
        nameTaken = IDPCategory().isCategoryNameTaken(categoryName, categoryId)

        success = False
        if not nameTaken:
            # comes back False if categoryId doesn't exist (UT43.5)
            success = IDPCategory().updateIDPCategory(categoryId, categoryName, description or "")
        return success
