# Control: SearchSavedListController - UC34 Search saved list (US34)

from entity.savedIDP import SavedIDP


class SearchSavedListController:
    # UC34 Search saved list
    # the page has already checked the keyword - this just asks the entity
    def searchSavedList(self, customerId, keyword):
        return SavedIDP().searchSavedRecords(customerId, keyword)
