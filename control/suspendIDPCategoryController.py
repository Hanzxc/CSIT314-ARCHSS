# Control: SuspendIDPCategoryController - UC44 Suspend IDP category (US44)

from control.platformManagerLoginController import PlatformManagerLoginController
from entity.idpCategory import IDPCategory


class SuspendIDPCategoryController:
    def canSuspendIDPCategory(self, managerId):
        return PlatformManagerLoginController().getAuthenticatedManager(managerId) is not None

    # UT44.1 to UT44.4
    def suspendIDPCategory(self, categoryId):
        category = IDPCategory().getIDPCategory(categoryId)
        if category is None:
            return False        # no such category (UT44.3)

        active = category.isActive()

        success = False
        # can't suspend something that's already suspended (UT44.2)
        if active:
            success = IDPCategory().suspendIDPCategory(categoryId)
        return success
