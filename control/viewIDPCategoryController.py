# Control: ViewIDPCategoryController - UC42 View IDP category (US42)

from entity.idpCategory import IDPCategory


class ViewIDPCategoryController:
    # UC42 View IDP category
    # gives None back if the id doesn't exist
    def viewIDPCategory(self, categoryId):
        return IDPCategory().getIDPCategory(categoryId)

    # UC42 View IDP category
    # the IDPs grouped in this category, so the manager can check the grouping
    def getIDPsInCategory(self, categoryId):
        return IDPCategory().getIDPsInCategory(categoryId)
