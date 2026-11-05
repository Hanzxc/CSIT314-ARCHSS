# Control: addPastIDPController - UC25 Add Past IDP
from entity.idp import IDP

class AddPastIDPController:
    def __init__(self):
        self.idpEntity = IDP()

    def addPastIDP(self, title, categoryId, description, location=None, designerId=None):
        if not title or not categoryId or not description:
            return False, "Please fill in all required fields."
            
        title_clean = title.strip()
        desc_clean = description.strip()
        loc_clean = location.strip() if location else ""

        if len(title_clean) < 3 or len(title_clean) > 100:
            return False, "Project title must be between 3 and 100 characters."

        new_idp = IDP(
            designerId=designerId,
            categoryId=int(categoryId),
            title=title_clean,
            description=desc_clean,
            location=loc_clean,
            projectType="Past",
            status="Active"
        )

        success = self.idpEntity.addPastIDP(new_idp)
        if success:
            return True, "Past IDP added successfully."
        else:
            return False, "Failed to add Past IDP. The selected category may no longer be active."