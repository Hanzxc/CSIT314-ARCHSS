# Control: searchSavedListController - UC34 Search Saved List
from entity.savedIDP import SavedIDP

class SearchSavedListController:
    def __init__(self):
        self.savedEntity = SavedIDP()

    def searchSavedList(self, customerId, keyword):
        if not customerId:
            return []

        kw_clean = keyword.strip() if keyword else ""

        # Fallback: if search term is empty, return all saved items for customer
        if not kw_clean:
            return self.savedEntity.getSavedListByCustomer(customerId)

        # Delegate search query execution to Entity layer
        return self.savedEntity.searchSavedList(customerId, kw_clean)