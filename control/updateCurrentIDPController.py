# Control: UpdateCurrentIDPController - UC22 Update a current IDP.
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP
from entity.idpCategory import IDPCategory

FIELD_LIMITS = {"title": 100, "description": 2000, "location": 200}


class UpdateCurrentIDPController:
    def canUpdateCurrentIDP(self, designerId):
        return InteriorDesignerLoginController().getAuthenticatedDesigner(designerId) is not None

    def getCurrentIDP(self, designerId, idpId):
        if not self.canUpdateCurrentIDP(designerId):
            raise PermissionError("Designer access unavailable")
        return IDP().getCurrentIDP(designerId, idpId)

    def getActiveIDPCategories(self, designerId):
        if not self.canUpdateCurrentIDP(designerId):
            raise PermissionError("Designer access unavailable")
        return IDPCategory().getActiveIDPCategories()

    def getFieldErrors(self, idpData):
        errors = {}
        for field, limit in FIELD_LIMITS.items():
            value = idpData.get(field)
            value = value.strip() if isinstance(value, str) else ""
            if field in ("title", "description") and not value:
                errors[field] = "This field is required"
            elif field == "title" and not 3 <= len(value) <= limit:
                errors[field] = "Title must be 3-100 characters"
            elif len(value) > limit:
                errors[field] = "Maximum " + str(limit) + " characters"
        try:
            categoryId = int(idpData.get("categoryId"))
        except (ValueError, TypeError):
            categoryId = None
        category = IDPCategory().getIDPCategory(categoryId)
        if category is None or not category.isActive():
            errors["categoryId"] = "Choose an available category"
        return errors

    def updateCurrentIDP(self, designerId, idpId, idpData):
        if not self.canUpdateCurrentIDP(designerId):
            raise PermissionError("Designer access unavailable")
        if self.getFieldErrors(idpData):
            return False
        cleanData = {field: idpData[field].strip() if isinstance(idpData.get(field), str) else ""
                     for field in FIELD_LIMITS}
        cleanData["categoryId"] = int(idpData["categoryId"])
        return IDP().updateCurrentIDP(designerId, idpId, cleanData)
