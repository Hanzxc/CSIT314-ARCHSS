# Boundary: SearchCompanyInformationPage - UC18 Search company information (US18)
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

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
    # searches the designer's own company profile for the keyword
    def searchCompanyInformation(self, keyword):
        # spaces around the keyword are ignored
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
