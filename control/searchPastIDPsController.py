# Control: searchPastIDPsController - UC29 Search Past IDPs
from entity.idp import IDP

class SearchPastIDPsController:
    def __init__(self):
        self.idpEntity = IDP()

    def searchPastIDPs(self, designerId, keyword):
        if not designerId:
            return []
            
        kw_clean = keyword.strip() if keyword else ""
        
        # If keyword is empty, fall back to fetching all past IDPs for the designer
        if not kw_clean:
            return self.idpEntity.getPastIDPsByDesigner(designerId)

        # Delegate keyword search to Entity layer
        return self.idpEntity.searchPastIDPs(designerId, kw_clean)