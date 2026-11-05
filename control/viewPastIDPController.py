# Control: viewPastIDPsController - UC26 View Past IDPs
from entity.idp import IDP

class ViewPastIDPsController:
    def __init__(self):
        self.idpEntity = IDP()

    def getPastIDPsByDesigner(self, designerId):
        # Validation check: Ensure a valid designer ID is provided
        if not designerId:
            return []
            
        # Delegate retrieval to Entity layer
        return self.idpEntity.getPastIDPsByDesigner(designerId)