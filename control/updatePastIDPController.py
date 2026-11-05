# control/updatePastIDPController.py
from entity.idp import IDP

class UpdatePastIDPController:
    def __init__(self):
        self.idpEntity = IDP()

    # ADD THIS METHOD RIGHT HERE:
    def getIDPById(self, idpId):
        """Helper method to fetch single IDP record for form pre-population"""
        if hasattr(self.idpEntity, 'getIDPById'):
            return self.idpEntity.getIDPById(idpId)
        elif hasattr(self.idpEntity, 'getPastIDPById'):
            return self.idpEntity.getPastIDPById(idpId)
        else:
            return self.idpEntity.get_idp_by_id(idpId) if hasattr(self.idpEntity, 'get_idp_by_id') else None

    def updatePastIDP(self, idpId, designerId, categoryId, title, description, location=None):
        if not title or not categoryId or not description:
            return False, "Please fill in all required fields."

        title_clean = title.strip()
        desc_clean = description.strip()
        loc_clean = location.strip() if location else ""

        if len(title_clean) < 3 or len(title_clean) > 100:
            return False, "Project title must be between 3 and 100 characters."

        updated_idp = IDP(
            idpId=idpId,
            designerId=designerId,
            categoryId=int(categoryId),
            title=title_clean,
            description=desc_clean,
            location=loc_clean,
            projectType="Past",
            status="Active"
        )

        if hasattr(self.idpEntity, 'updatePastIDP'):
            success = self.idpEntity.updatePastIDP(updated_idp)
        else:
            success = self.idpEntity.update_idp(updated_idp)

        if success:
            return True, "Past IDP updated successfully."
        else:
            return False, "Failed to update Past IDP. Please try again."