"""Flask page boundaries for US37, US38 and US46-48."""
from datetime import date
from flask import abort, render_template, request, session
from control.idpAnalyticsController import IDPAnalyticsController

class IDPAnalyticsPage:
    def __init__(self):
        self.controller = IDPAnalyticsController()

    def show_designer_statistics(self, metric):
        if metric not in ('views', 'saves'):
            abort(404)
        try:
            rows = self.controller.designer_statistics(session['userId'])
        except PermissionError:
            abort(403)
        return render_template('idpStatistics.html', metric=metric, rows=rows,
                               activePage='statistics')

    def show_category_report(self, period):
        chosen_date = request.args.get('date', date.today().isoformat())
        try:
            report = self.controller.category_report(session['userId'], period, chosen_date)
        except PermissionError:
            abort(403)
        except ValueError as exc:
            return render_template('idpCategoryReport.html', report=None,
                                   selectedDate=chosen_date, error=str(exc),
                                   period=period, activePage='reports'), 400
        return render_template('idpCategoryReport.html', report=report,
                               selectedDate=chosen_date, error=None,
                               period=period, activePage='reports')
