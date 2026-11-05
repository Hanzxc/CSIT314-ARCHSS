# Control: deletePastIDPController - UC28 Delete Past IDP
from entity.idp import IDP

class DeletePastIDPController:
    def __init__(self):
        self.idpEntity = IDP()

    def deletePastIDP(self, idpId, designerId):
        # Validation checks
        if not idpId or not designerId:
            return False, "Invalid project or session credentials."

        # Delegate soft-deletion (status='Suspended') to Entity layer
        success = self.idpEntity.deletePastIDP(idpId, designerId)
        if success:
            return True, "Past IDP deleted successfully."
            
        return False, "Failed to delete Past IDP. Verify ownership and project status."