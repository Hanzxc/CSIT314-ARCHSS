# Control: ViewIDPCategoryController - UC42 View IDP category (US42)

from control.platformManagerLoginController import PlatformManagerLoginController
from entity.idp import IDP
from entity.idpCategory import IDPCategory


class ViewIDPCategoryController:
    def canViewIDPCategory(self, managerId):
        return PlatformManagerLoginController().getAuthenticatedManager(managerId) is not None

    # UT42.5, UT42.6 - gives None back if the id doesn't exist
    def viewIDPCategory(self, categoryId):
        category = IDPCategory().getIDPCategory(categoryId)
        return category

    # UT42.7 - the IDPs grouped in this category, so the manager can check the grouping
    def getIDPsInCategory(self, categoryId):
        idps = IDP().getIDPsInCategory(categoryId)
        return idps
