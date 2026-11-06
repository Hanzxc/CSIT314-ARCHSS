# Control: ViewIDPSaveStatisticsController - UC38 View IDP save statistics (US38)

from entity.idpAnalytics import IDPAnalytics


class ViewIDPSaveStatisticsController:
    # UC38 View IDP save statistics
    # the page passes in the logged-in designer's id, this just asks the entity for the counts
    def getSaveStatistics(self, designerId):
        return IDPAnalytics().getSaveStatistics(designerId)
