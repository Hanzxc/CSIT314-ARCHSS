# Control: ViewSavedListController - UC35 View saved list (US35)

from entity.savedIDP import SavedIDP


class ViewSavedListController:
    # UC35 View saved list
    # the logged-in customer's saved IDPs (the page passes in session["userId"])
    def getSavedList(self, customerId):
        return SavedIDP().getSavedRecords(customerId)
