# Control: CreateIDPCategoryController - UC41 Create IDP category (US41)

from entity.idpCategory import IDPCategory


class CreateIDPCategoryController:
    # UC41 Create IDP category
    # the page checks the input, the entity checks for a duplicate name - this just calls create
    def createIDPCategory(self, idpCategory):
        return IDPCategory().createIDPCategory(idpCategory)
