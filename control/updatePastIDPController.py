# Control: updatePastIDPController - UC27 Update Past IDP
from entity.idp import IDP

class UpdatePastIDPController:
    def __init__(self):
        self.idpEntity = IDP()

    def getIDPForEdit(self, idpId, designerId):
        idp_data = self.idpEntity.getIDPById(idpId)
        # Verify that IDP exists, is 'Past', and belongs to the requesting designer
        if idp_data and idp_data['designerId'] == designerId and idp_data['projectType'] == 'Past':
            return idp_data
        return None

    def updatePastIDP(self, idpId, designerId, categoryId, title, description, location=None):
        if not title or not categoryId or not description:
            return False, "Please fill in all required fields."
            
        title_clean = title.strip()
        desc_clean = description.strip()
        loc_clean = location.strip() if location else ""

        if len(title_clean) < 3 or len(title_clean) > 100:
            return False, "Project title must be between 3 and 100 characters."

        # Create updated IDP instance
        idp_obj = IDP(
            idpId=idpId,
            designerId=designerId,
            categoryId=int(categoryId),
            title=title_clean,
            description=desc_clean,
            location=loc_clean,
            projectType="Past"
        )

        success = self.idpEntity.updatePastIDP(idp_obj)
        if success:
            return True, "Past IDP updated successfully."
        else:
            return False, "Failed to update Past IDP. Verify ownership and details."