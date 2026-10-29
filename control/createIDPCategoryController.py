# Control: CreateIDPCategoryController - UC41 Create IDP category (US41)

from control.platformManagerLoginController import PlatformManagerLoginController
from entity.idpCategory import IDPCategory


class CreateIDPCategoryController:
    # access check reused from US39 - only an active Platform Manager may create categories
    def canCreateIDPCategory(self, managerId):
        return PlatformManagerLoginController().getAuthenticatedManager(managerId) is not None

    # UT41.5 to UT41.8
    def createIDPCategory(self, categoryName, description):
        # the page checks this too but the controller shouldn't trust that (UT41.7)
        if not categoryName or not categoryName.strip():
            return False

        # business rule - no 2 categories with the same name (seq diagram msgs 12-13)
        nameTaken = IDPCategory().isCategoryNameTaken(categoryName)

        success = False
        if not nameTaken:
            # opt box in the seq diagram, only save when the name is free
            success = IDPCategory().createIDPCategory(categoryName, description or "")
        return success
