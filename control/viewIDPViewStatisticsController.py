# Control: ViewIDPViewStatisticsController - UC37 View IDP view statistics (US37)

from entity.idpAnalytics import IDPAnalytics


class ViewIDPViewStatisticsController:
    # UC37 View IDP view statistics
    # the page passes in the logged-in designer's id, this just asks the entity for the counts
    def getViewStatistics(self, designerId):
        return IDPAnalytics().getViewStatistics(designerId)
