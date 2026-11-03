# Control: SuspendIDPCategoryController - UC44 Suspend IDP category (US44)

from entity.idpCategory import IDPCategory


class SuspendIDPCategoryController:
    # UC44 Suspend IDP category
    # the entity only changes an Active category, so a missing or already suspended one gives False
    def suspendIDPCategory(self, categoryId):
        return IDPCategory().suspendIDPCategory(categoryId)
