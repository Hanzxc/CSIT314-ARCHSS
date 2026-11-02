# Boundary: SearchCompanyInformationPage - UC18 Search company information (US18)

from flask import redirect, render_template, session, url_for

from control.searchCompanyInformationController import SearchCompanyInformationController

MSG_NO_RESULTS = "No matching company information found"
MSG_NOT_FOUND = "You have not created a company profile yet"


class SearchCompanyInformationPage:
    # UC18 Search company information
    # starts with an empty search box
    def __init__(self):
        self.searchCompanyInformationController = SearchCompanyInformationController()
        self.keyword = ""

    # UC18 Search company information
    # not logged in -> back to the designer login, not a designer -> access denied page
    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.searchCompanyInformationController.canSearchCompanyInformation(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    # UC18 Search company information
    # searches the designer's own company profile for the keyword
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

    # UC18 Search company information
    # shows the matching parts of the profile
    def displayResults(self, results):
        return render_template("searchCompanyInformation.html", results=results,
                               keyword=self.keyword, activePage="company")

    # UC18 Search company information
    # nothing matched the keyword
    def displayNoResultsMessage(self):
        return render_template("searchCompanyInformation.html", results=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS, activePage="company")

    # UC18 Search company information
    # shows the "no company profile" page (404) when there's nothing to show
    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
