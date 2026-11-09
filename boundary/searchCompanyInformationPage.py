# Boundary: SearchCompanyInformationPage - UC18 Search company information (US18)
# template: templates/searchCompanyInformation.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.searchCompanyInformationController import SearchCompanyInformationController

MSG_NO_RESULTS = "No matching company information found"
MSG_NOT_FOUND = "You have not created a company profile yet"

# the labels shown next to each field - the entity only gives back the field names
FIELD_LABELS = {"companyName": "Company name", "description": "Company description",
                "services": "Services offered", "email": "Contact email",
                "phone": "Contact phone", "address": "Company address"}


class SearchCompanyInformationPage:
    # UC18 Search company information
    # starts with an empty search box
    def __init__(self):
        self.searchCompanyInformationController = SearchCompanyInformationController()
        self.keyword = ""

    # UC18 Search company information
    # searches the designer's own company profile for the keyword straight away
    def searchCompanyInformation(self, keyword):
        # spaces around the keyword are ignored
        self.keyword = keyword.strip()
        companyProfile = self.searchCompanyInformationController.searchCompanyInformation(session["userId"], self.keyword)
        if companyProfile is None:
            return self.displayNotFoundMessage()
        if not companyProfile.matchedFields:
            return self.displayNoResultsMessage()
        return self.displayResults(companyProfile)

    # UC18 Search company information
    # one row per matching field, with its label
    def displayResults(self, companyProfile):
        return render_template("searchCompanyInformation.html", companyProfile=companyProfile,
                               fieldLabels=FIELD_LABELS, keyword=self.keyword, activePage="company")

    # UC18 Search company information
    # nothing matched the keyword
    def displayNoResultsMessage(self):
        return render_template("searchCompanyInformation.html", companyProfile=None, keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS, activePage="company")

    # UC18 Search company information
    # shows the "no company profile" page (404) when there's nothing to show
    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
