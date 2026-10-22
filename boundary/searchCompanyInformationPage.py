# Boundary: SearchCompanyInformationPage - UC18 Search company information (US18)

from flask import redirect, render_template, session, url_for

from control.searchCompanyInformationController import SearchCompanyInformationController

MSG_NO_RESULTS = "No matching company information found"
MSG_NOT_FOUND = "You have not created a company profile yet"


class SearchCompanyInformationPage:
    def __init__(self):
        self.searchCompanyInformationController = SearchCompanyInformationController()
        self.keyword = ""

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.searchCompanyInformationController.canSearchCompanyInformation(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def searchCompanyInformation(self, keyword):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.keyword = (keyword or "").strip()
        designerId = session["userId"]
        if not self.searchCompanyInformationController.hasCompanyProfile(designerId):
            return self.displayNotFoundMessage()
        results = self.searchCompanyInformationController.searchCompanyInformation(designerId, self.keyword)
        if results:
            return self.displayResults(results)
        return self.displayNoResultsMessage()

    def displayResults(self, results):
        return render_template("searchCompanyInformation.html", results=results,
                               keyword=self.keyword, activePage="company")

    def displayNoResultsMessage(self):
        return render_template("searchCompanyInformation.html", results=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS, activePage="company")

    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
