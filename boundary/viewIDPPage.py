# Boundary: ViewIDPPage - UC32 View IDP (US32)
# templates: customerViewIDP.html, customerIDPNotFound.html
# precondition: the customer is already logged in (US30), so there's no extra access check here.
# showing the designer's company profile is US15's job, so we borrow that controller

from flask import render_template

from control.viewIDPController import ViewIDPController
from control.viewCompanyProfileController import ViewCompanyProfileController


class ViewIDPPage:
    # UC32 View IDP
    # starts with an empty keyword
    def __init__(self):
        self.viewIDPController = ViewIDPController()
        self.keyword = ""

    # UC32 View IDP
    # customer clicked View on a search result. the keyword is only kept for "Back to search".
    # saved is True only when US33's Save sends the customer back here (?saved=1) - that reload
    # isn't counted as a view
    def selectIDP(self, idpId, keyword, saved=False):
        self.keyword = (keyword or "").strip()
        countView = not saved
        idp = self.viewIDPController.viewIDP(idpId, countView)
        if idp is not None:
            companyProfile = ViewCompanyProfileController().viewCompanyProfile(idp.designerId)
            return self.displayIDP(idp, companyProfile)
        return self.displayNotFoundMessage()

    # UC32 View IDP
    # the IDP's details + the designer's company (fallback text if companyProfile is None).
    # the Save IDP button (US33) is always shown
    def displayIDP(self, idp, companyProfile):
        return render_template("customerViewIDP.html", idp=idp, companyProfile=companyProfile,
                               keyword=self.keyword, activePage="searchIDPs")

    # UC32 View IDP
    # HTTP 404 with no project or designer details
    def displayNotFoundMessage(self):
        return render_template("customerIDPNotFound.html", keyword=self.keyword,
                               activePage="searchIDPs"), 404
