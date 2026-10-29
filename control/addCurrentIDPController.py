# Control: AddCurrentIDPController - UC20 Add current IDP (US20)

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP
from entity.idpCategory import IDPCategory

FIELD_LIMITS = {"title": 100, "description": 2000, "location": 200}


class AddCurrentIDPController:
    # access check reused from US13 - only an active Interior Designer may add IDPs
    def canAddCurrentIDP(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    # for the category drop-down - suspended categories can't be selected (US44)
    def getActiveIDPCategories(self):
        categories = IDPCategory().getActiveIDPCategories()
        return categories

    # UT20.6 to UT20.12 - field rules, keys match the form field names
    def getFieldErrors(self, idpData):
        errors = {}
        for field, limit in FIELD_LIMITS.items():
            value = (idpData.get(field) or "").strip()
            if field in ("title", "description") and not value:
                errors[field] = "This field is required"
            elif len(value) > limit:
                errors[field] = "Maximum " + str(limit) + " characters"
        title = (idpData.get("title") or "").strip()
        if title and len(title) < 3:
            errors["title"] = "Title must be 3-100 characters"

        category = IDPCategory().getIDPCategory(idpData.get("categoryId"))
        if category is None or not category.isActive():
            errors["categoryId"] = "Choose an available category"
        return errors

    # UT20.1 to UT20.5
    def addCurrentIDP(self, designerId, idpData):
        if not self.canAddCurrentIDP(designerId) or self.getFieldErrors(idpData):
            return False
        return IDP().addCurrentIDP(designerId, idpData)
