"""US31 Boundary: customer access, keyword form and search results."""
from flask import redirect, render_template, session, url_for

from control.searchIDPController import SearchIDPController

MSG_NO_RESULTS = "No matching IDPs found"
MSG_NO_IDPS = "No IDPs are currently available"


class SearchIDPPage:
    def __init__(self):
        self.searchIDPController = SearchIDPController()
        self.keyword = ""
        self.account = None

    def checkAccess(self):
        if session.get("userId") is None:
            return redirect(url_for("customerLogin"))
        self.account = self.searchIDPController.getCustomer(session["userId"])
        if self.account is None:
            return render_template("customerAccessDenied.html"), 403
        return None

    def searchIDPs(self, keyword):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.keyword = (keyword or "").strip()
        try:
            idps = self.searchIDPController.searchIDPs(session["userId"], self.keyword)
        except PermissionError:
            return render_template("customerAccessDenied.html"), 403
        return self.displayResults(idps) if idps else self.displayNoResultsMessage()

    def displayResults(self, idps):
        return render_template("customerSearchIDPs.html", account=self.account,
                               idps=idps, keyword=self.keyword, activePage="searchIDPs")

    def displayNoResultsMessage(self):
        return render_template("customerSearchIDPs.html", account=self.account,
                               idps=[], keyword=self.keyword, activePage="searchIDPs",
                               noResultsMessage=MSG_NO_RESULTS if self.keyword else MSG_NO_IDPS)
