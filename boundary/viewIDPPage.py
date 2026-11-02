"""US32 Boundary: protected customer detail view with a search return link."""
from flask import redirect, render_template, session, url_for

from control.viewIDPController import ViewIDPController


class ViewIDPPage:
    def __init__(self):
        self.viewIDPController = ViewIDPController()
        self.account = None
        self.keyword = ""
        self.isSaved = False

    def checkAccess(self):
        if session.get("userId") is None:
            return redirect(url_for("customerLogin"))
        self.account = self.viewIDPController.getCustomer(session["userId"])
        if self.account is None:
            return render_template("customerAccessDenied.html"), 403
        return None

    def selectIDP(self, idpId, keyword=""):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.keyword = (keyword or "").strip()
        try:
            result = self.viewIDPController.viewIDP(session["userId"], idpId)
        except PermissionError:
            return render_template("customerAccessDenied.html"), 403
        if result is None:
            return self.displayNotFoundMessage()
        self.isSaved = result["isSaved"]
        return self.displayIDP(result["idp"], result["companyProfile"])

    def displayIDP(self, idp, companyProfile):
        return render_template("customerViewIDP.html", account=self.account, idp=idp,
                               companyProfile=companyProfile, keyword=self.keyword,
                               isSaved=self.isSaved,
                               activePage="searchIDPs")

    def displayNotFoundMessage(self):
        return render_template("customerIDPNotFound.html", account=self.account,
                               keyword=self.keyword, activePage="searchIDPs"), 404
