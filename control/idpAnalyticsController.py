"""US37-38 and US46-48 authorization and reporting coordination."""
from entity.idpAnalytics import IDPAnalytics
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from control.platformManagerLoginController import PlatformManagerLoginController

class IDPAnalyticsController:
    def __init__(self):
        self.analytics = IDPAnalytics()

    def designer_statistics(self, user_id):
        if not InteriorDesignerLoginController().getAuthenticatedDesigner(user_id):
            raise PermissionError('Only active interior designers can view these statistics')
        return self.analytics.get_designer_statistics(user_id)

    def category_report(self, user_id, period, selected_date):
        if not PlatformManagerLoginController().getAuthenticatedManager(user_id):
            raise PermissionError('Only active platform managers can generate reports')
        return self.analytics.get_category_report(period, selected_date)
