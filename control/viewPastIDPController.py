# Control: ViewPastIDPController - UC26 View Past IDPs
# control/viewPastIDPController.py
from entity.idp import IDP

class ViewPastIDPController:
    def __init__(self):
        # Initialize the entity instance when the controller is created
        self.idpEntity = IDP()

    def getPastIDPsByDesigner(self, designerId):
        # Validation check: Ensure a valid designer ID is provided
        if not designerId:
            return []
            
        # Delegate retrieval to Entity layer
        return self.idpEntity.getPastIDPsByDesigner(designerId)