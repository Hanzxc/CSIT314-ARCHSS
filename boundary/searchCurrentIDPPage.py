# Boundary: SearchCurrentIDPPage - UC24 Search current IDPs.
from flask import redirect, render_template, session, url_for

from control.searchCurrentIDPController import SearchCurrentIDPController

MSG_NO_RESULTS = "No matching current IDPs found"
MSG_NO_IDPS = "You have no current IDPs to display"


class SearchCurrentIDPPage:
    def __init__(self):
        self.searchCurrentIDPController = SearchCurrentIDPController()
        self.keyword = ""

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.searchCurrentIDPController.canSearchCurrentIDPs(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def searchCurrentIDPs(self, keyword):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.keyword = (keyword or "").strip()
        try:
            idps = self.searchCurrentIDPController.searchCurrentIDPs(session["userId"], self.keyword)
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403
        return self.displayResults(idps) if idps else self.displayNoResultsMessage()

    def displayResults(self, idps):
        return render_template("searchCurrentIDPs.html", idps=idps, keyword=self.keyword,
                               activePage="currentIDPs")

    def displayNoResultsMessage(self):
        return render_template("searchCurrentIDPs.html", idps=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS if self.keyword else MSG_NO_IDPS,
                               activePage="currentIDPs")
