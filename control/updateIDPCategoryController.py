# Control: UpdateIDPCategoryController - UC43 Update IDP category (US43)

from entity.idpCategory import IDPCategory


class UpdateIDPCategoryController:
    # UC43 Update IDP category
    # gets the category's current details to fill in the form
    def getIDPCategory(self, categoryId):
        return IDPCategory().getIDPCategory(categoryId)

    # UC43 Update IDP category
    # the page checks the input, the entity checks for a duplicate name - this just calls update
    def updateIDPCategory(self, idpCategory):
        return IDPCategory().updateIDPCategory(idpCategory)
