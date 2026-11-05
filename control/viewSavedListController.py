# Control: viewSavedListController - UC35 View Saved List
from entity.savedIDP import SavedIDP

class ViewSavedListController:
    def __init__(self):
        self.savedEntity = SavedIDP()

    def getSavedListByCustomer(self, customerId):
        # Validation check: Ensure customer is authenticated
        if not customerId:
            return []

        # Delegate retrieval of bookmarked IDPs to Entity layer
        return self.savedEntity.getSavedListByCustomer(customerId)