# Flask app - links each URL to its boundary (page) class
# run with:  python app.py   then open http://127.0.0.1:5000

from functools import wraps

from flask import Flask, request, redirect, url_for, session, render_template

from boundary.interiorDesignerLoginPage import InteriorDesignerLoginPage
from boundary.createCompanyProfilePage import CreateCompanyProfilePage
from boundary.viewCompanyProfilePage import ViewCompanyProfilePage
from boundary.updateCompanyProfilePage import UpdateCompanyProfilePage
from boundary.deleteCompanyProfilePage import DeleteCompanyProfilePage
from boundary.searchCompanyInformationPage import SearchCompanyInformationPage
from boundary.interiorDesignerLogoutPage import InteriorDesignerLogoutPage
from boundary.viewCurrentIDPPage import ViewCurrentIDPPage
from boundary.updateCurrentIDPPage import UpdateCurrentIDPPage
from boundary.deleteCurrentIDPPage import DeleteCurrentIDPPage
from boundary.searchCurrentIDPPage import SearchCurrentIDPPage

from boundary.restoreCompanyProfilePage import RestoreCompanyProfilePage
from boundary.platformManagerLoginPage import PlatformManagerLoginPage
from boundary.loginPage import LoginPage
from boundary.customerLoginPage import CustomerLoginPage
from boundary.customerLogoutPage import CustomerLogoutPage
from boundary.searchIDPPage import SearchIDPPage
from boundary.viewIDPPage import ViewIDPPage
from boundary.logoutPage import LogoutPage
from boundary.createUserProfilePage import CreateUserProfilePage
from boundary.viewUserProfilePage import ViewUserProfilePage
from boundary.updateUserProfilePage import UpdateUserProfilePage
from boundary.suspendUserProfilePage import SuspendUserProfilePage
from boundary.searchUserProfilePage import SearchUserProfilePage
from boundary.createUserAccountPage import CreateUserAccountPage
from boundary.viewUserAccountPage import ViewUserAccountPage
from boundary.updateUserAccountPage import UpdateUserAccountPage
from boundary.suspendUserAccountPage import SuspendUserAccountPage
from boundary.searchUserAccountPage import SearchUserAccountPage
from entity.userProfile import UserProfile

# Sprint 4 (US25 - US29 past IDPs, US33 - US35 saved list)
from boundary.addPastIDPPage import AddPastIDPPage
from boundary.pastIDPListPage import PastIDPListPage
from boundary.editPastIDPPage import EditPastIDPPage
from boundary.pastIDPSearchPage import PastIDPSearchPage
from boundary.idpDetailsPage import IDPDetailsPage
from boundary.savedListPage import SavedListPage

from database.db import initDatabase

from boundary.addCurrentIDPPage import AddCurrentIDPPage
from boundary.platformManagerLogoutPage import PlatformManagerLogoutPage
from boundary.createIDPCategoryPage import CreateIDPCategoryPage
from boundary.viewIDPCategoryPage import ViewIDPCategoryPage
from boundary.updateIDPCategoryPage import UpdateIDPCategoryPage
from boundary.suspendIDPCategoryPage import SuspendIDPCategoryPage
from boundary.searchIDPCategoryPage import SearchIDPCategoryPage

from boundary.viewIDPViewStatisticsPage import ViewIDPViewStatisticsPage
from boundary.viewIDPSaveStatisticsPage import ViewIDPSaveStatisticsPage
from boundary.generateDailyReportPage import GenerateDailyReportPage
from boundary.generateWeeklyReportPage import GenerateWeeklyReportPage
from boundary.generateMonthlyReportPage import GenerateMonthlyReportPage

app = Flask(__name__)
app.secret_key = "change-this-later"     # TODO: move to an environment variable


@app.after_request
def noCache(response):
    # stops the browser showing an old admin page when you press Back after logging out (US2 wireframe 4b)
    response.headers["Cache-Control"] = "no-store"
    return response


def loginRequired(routeFunction):
    # US3 - US12 and the User Admin dashboard: being logged in as a User Admin is the precondition
    # of these use cases (US1), so the pages don't re-check it. this only stops a crash when there's
    # no session at all - not logged in = sent back to the login page
    @wraps(routeFunction)
    def wrapper(*args, **kwargs):
        if "userId" not in session:
            return redirect(url_for("login"))
        return routeFunction(*args, **kwargs)
    return wrapper


def designerLoginRequired(routeFunction):
    # US13 dashboard + US14 - US18, US20 - US24: being logged in as a designer is the precondition of
    # these use cases (US13), so the pages don't re-check it (lecturer's feedback). this only stops a
    # crash when there's no session at all
    @wraps(routeFunction)
    def wrapper(*args, **kwargs):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        return routeFunction(*args, **kwargs)
    return wrapper


def customerLoginRequired(routeFunction):
    # US30 dashboard + US31 - US35: being logged in as a customer is the precondition of these use
    # cases (US30), so the pages don't re-check it. this only stops a crash when there's no session at all
    @wraps(routeFunction)
    def wrapper(*args, **kwargs):
        if "userId" not in session:
            return redirect(url_for("customerLogin"))
        return routeFunction(*args, **kwargs)
    return wrapper


def managerLoginRequired(routeFunction):
    # US39 dashboard + US41 - US45: being logged in as a platform manager is the precondition of these
    # use cases (US39), so the pages don't re-check it. this only stops a crash when there's no session at all
    @wraps(routeFunction)
    def wrapper(*args, **kwargs):
        if "userId" not in session:
            return redirect(url_for("platformManagerLogin"))
        return routeFunction(*args, **kwargs)
    return wrapper


@app.context_processor
def headerInfo():
    # base.html shows "Logged in as ..." on every admin page, this saves passing it in every time
    # "header..." names so a page's own form fields (username, profileName) can't overwrite them
    if "userId" not in session:
        return {}
    profile = UserProfile().getUserProfile(session["profileId"])
    return {"headerUsername": session["username"],
            "headerProfileName": profile.profileName if profile else ""}


# UC1 Log in
# opening the bare site just sends you to the login page
@app.route("/")
def home():
    return redirect(url_for("login"))


# US1 Log in
@app.route("/login", methods=["GET", "POST"])
def login():
    page = LoginPage()
    if request.method == "POST":
        return page.submitLogin(request.form.get("username", ""), request.form.get("password", ""))
    return page.openLoginPage()


# UC30 Customer log in
# customers log in on their own page (the shared /login is only for User Admins, US1)
@app.route("/customer/login", methods=["GET", "POST"])
def customerLogin():
    page = CustomerLoginPage()
    if request.method == "POST":
        return page.submitLogin(request.form.get("username", ""), request.form.get("password", ""))
    return page.openLoginPage()


# UC30 Customer log in
# the customer's home page after logging in
@app.route("/customer/dashboard", methods=["GET"])
@customerLoginRequired
def customerDashboard():
    return CustomerLoginPage().openDashboard()


# UC36 Customer log out
# no decorator - with no session the customer just gets "Your session has already ended"
@app.route("/customer/logout", methods=["POST"])
def customerLogout():
    return CustomerLogoutPage().clickLogout()


# UC31 Search IDPs
@app.route("/customer/idps/search", methods=["GET"])
@customerLoginRequired
def searchIDPs():
    return SearchIDPPage().searchIDPs(request.args.get("keyword", ""))


# UC32 View IDP
# saved=1 is only there when US33's Save sends the customer back here - that reload isn't counted as a view
@app.route("/customer/idps/<int(signed=True):idpId>", methods=["GET"])
@customerLoginRequired
def viewIDP(idpId):
    return ViewIDPPage().selectIDP(idpId, request.args.get("keyword", ""),
                                   request.args.get("saved") == "1")


# US13: dedicated designer entry point, using the same CSS and entities.
@app.route("/designer/login", methods=["GET", "POST"])
def interiorDesignerLogin():
    page = InteriorDesignerLoginPage()
    if request.method == "POST":
        return page.submitLogin(request.form.get("username", ""), request.form.get("password", ""))
    return page.openLoginPage()


# UC13 Interior designer log in
# the designer's home page after logging in
@app.route("/designer/dashboard")
@designerLoginRequired
def interiorDesignerDashboard():
    return InteriorDesignerLoginPage().openDashboard()


# UC21 View current IDPs
# the owner always comes from the session in the boundary, never the URL
@app.route("/designer/idps/current", methods=["GET"])
@designerLoginRequired
def viewCurrentIDPs():
    return ViewCurrentIDPPage().clickViewCurrentIDPs()


# UC24 Search current IDPs
@app.route("/designer/idps/current/search", methods=["GET"])
@designerLoginRequired
def searchCurrentIDPs():
    return SearchCurrentIDPPage().searchCurrentIDPs(request.args.get("keyword", ""))


# UC21 View current IDPs (one IDP's preview)
@app.route("/designer/idps/current/<int(signed=True):idpId>", methods=["GET"])
@designerLoginRequired
def viewCurrentIDP(idpId):
    return ViewCurrentIDPPage().selectCurrentIDP(idpId)


# UC22 Update current IDP
# categoryId comes from the drop-down as text, type=int turns it into a number (None if nothing picked)
@app.route("/designer/idps/current/<int(signed=True):idpId>/update", methods=["GET", "POST"])
@designerLoginRequired
def updateCurrentIDP(idpId):
    page = UpdateCurrentIDPPage()
    if request.method == "POST":
        return page.submitUpdate(idpId, request.form.get("title", ""),
                                 request.form.get("categoryId", type=int),
                                 request.form.get("description", ""),
                                 request.form.get("location", ""))
    return page.clickUpdate(idpId)


# UC23 Delete current IDP
# POST = Delete or Cancel in the confirmation box (no token, the idpId comes from the URL)
@app.route("/designer/idps/current/<int(signed=True):idpId>/delete", methods=["GET", "POST"])
@designerLoginRequired
def deleteCurrentIDP(idpId):
    page = DeleteCurrentIDPPage()
    if request.method == "POST":
        return page.submitDelete(idpId, request.form.get("choice", ""))
    return page.clickDelete(idpId)


# US14 Create company profile. Ownership is taken from the session in the boundary.
@app.route("/designer/company/create", methods=["GET", "POST"])
@designerLoginRequired
def createCompanyProfile():
    page = CreateCompanyProfilePage()
    if request.method == "POST":
        return page.submitCompanyProfile(request.form.get("companyName", ""),
                                         request.form.get("description", ""),
                                         request.form.get("services", ""),
                                         request.form.get("email", ""),
                                         request.form.get("phone", ""),
                                         request.form.get("address", ""))
    return page.clickCreateCompanyProfile()


# US15 View the company profile owned by the authenticated designer.
@app.route("/designer/company", methods=["GET"])
@designerLoginRequired
def viewCompanyProfile():
    return ViewCompanyProfilePage().clickView()


# US16 Update the existing company profile owned by the authenticated designer.
@app.route("/designer/company/update", methods=["GET", "POST"])
@designerLoginRequired
def updateCompanyProfile():
    page = UpdateCompanyProfilePage()
    if request.method == "POST":
        return page.submitUpdate(request.form.get("companyName", ""),
                                 request.form.get("description", ""),
                                 request.form.get("services", ""),
                                 request.form.get("email", ""),
                                 request.form.get("phone", ""),
                                 request.form.get("address", ""))
    return page.clickUpdate()


# US17 Delete company profile
# GET  = designer clicked Delete -> show the "Are you sure?" box
# POST = Delete or Cancel in the box, with the hidden companyId + revision
# (type=int gives None if they're missing, then the entity just matches no row)
@app.route("/designer/company/delete", methods=["GET", "POST"])
@designerLoginRequired
def deleteCompanyProfile():
    page = DeleteCompanyProfilePage()
    if request.method == "POST":
        return page.submitDelete(request.form.get("choice", ""),
                                 request.form.get("companyId", type=int),
                                 request.form.get("revision", type=int))
    return page.clickDelete()


# US18 Search only the authenticated designer's company information.
@app.route("/designer/company/search", methods=["GET"])
@designerLoginRequired
def searchCompanyInformation():
    return SearchCompanyInformationPage().searchCompanyInformation(request.args.get("keyword", ""))


# US19 End the current designer browser session; no active-role guard is required to log out.
@app.route("/designer/logout", methods=["POST"])
def interiorDesignerLogout():
    return InteriorDesignerLogoutPage().clickLogout()


# US2 Log out
@app.route("/logout", methods=["POST"])
def logout():
    return LogoutPage().clickLogout()


# User Admin dashboard (where US1 ends up)
@app.route("/dashboard")
@loginRequired
def dashboard():
    return render_template("dashboard.html", activePage="dashboard")


# US7 Search user profiles - this is also the User Profiles list page
# /profiles shows everything, /profiles?keyword=cust only shows the matches
@app.route("/profiles")
@loginRequired
def profiles():
    return SearchUserProfilePage().searchUserProfiles(request.args.get("keyword", ""))


# US3 Create user profile
@app.route("/profiles/create", methods=["GET", "POST"])
@loginRequired
def createUserProfile():
    page = CreateUserProfilePage()
    if request.method == "POST":
        return page.submitUserProfile(request.form.get("profileName", ""),
                                      request.form.get("description", ""),
                                      request.form.getlist("permissions"))
    return page.clickCreateUserProfile()


# US4 View user profile
@app.route("/profiles/<int:profileId>")
@loginRequired
def viewUserProfile(profileId):
    return ViewUserProfilePage().selectUserProfile(profileId)


# US5 Update user profile
@app.route("/profiles/<int:profileId>/update", methods=["GET", "POST"])
@loginRequired
def updateUserProfile(profileId):
    page = UpdateUserProfilePage()
    if request.method == "POST":
        page.profileId = profileId
        return page.submitUpdate(request.form.get("profileName", ""),
                                 request.form.get("description", ""),
                                 request.form.getlist("permissions"))
    return page.clickUpdate(profileId)


# US6 Suspend user profile
# GET  = admin clicked Suspend -> show the "Are you sure?" box
# POST = admin clicked OK or Cancel in the box
@app.route("/profiles/<int:profileId>/suspend", methods=["GET", "POST"])
@loginRequired
def suspendUserProfile(profileId):
    page = SuspendUserProfilePage()
    if request.method == "GET":
        return page.clickSuspend(profileId)

    page.profileId = profileId
    if request.form.get("choice") == "cancel":
        return page.cancelSuspend()
    return page.confirmSuspend()


# US12 Search user account - this is also the User Accounts list page
# /accounts shows everything, /accounts?keyword=chloe only shows the matches
@app.route("/accounts")
@loginRequired
def accounts():
    return SearchUserAccountPage().searchUserAccounts(request.args.get("keyword", ""))


# US8 Create user account
# profileId comes from the drop-down as text, type=int turns it into a number (None if nothing picked)
@app.route("/accounts/create", methods=["GET", "POST"])
@loginRequired
def createUserAccount():
    page = CreateUserAccountPage()
    if request.method == "POST":
        return page.submitCreateAccount(request.form.get("username", ""),
                                        request.form.get("password", ""),
                                        request.form.get("fullName", ""),
                                        request.form.get("email", ""),
                                        request.form.get("phone", ""),
                                        request.form.get("profileId", type=int))
    return page.clickCreateUserAccount()


# US9 View user account
@app.route("/accounts/<int:userId>")
@loginRequired
def viewUserAccount(userId):
    return ViewUserAccountPage().clickView(userId)


# US10 Update user account
@app.route("/accounts/<int:userId>/update", methods=["GET", "POST"])
@loginRequired
def updateUserAccount(userId):
    page = UpdateUserAccountPage()
    if request.method == "POST":
        return page.submitUpdate(userId,
                                 request.form.get("username", ""),
                                 request.form.get("fullName", ""),
                                 request.form.get("email", ""),
                                 request.form.get("phone", ""),
                                 request.form.get("profileId", type=int))
    return page.clickUpdate(userId)


# US11 Suspend user account
# GET  = admin clicked Suspend -> show the confirmation box
# POST = admin clicked Suspend or Cancel in the box
@app.route("/accounts/<int:userId>/suspend", methods=["GET", "POST"])
@loginRequired
def suspendUserAccount(userId):
    page = SuspendUserAccountPage()
    if request.method == "GET":
        return page.clickSuspend(userId)

    page.userId = userId
    if request.form.get("choice") == "cancel":
        return page.cancelSuspend()
    return page.confirmSuspend()


# US39 Platform manager login, sharing the existing account and profile entities.
@app.route("/manager/login", methods=["GET", "POST"])
def platformManagerLogin():
    page = PlatformManagerLoginPage()
    if request.method == "POST":
        return page.submitLogin(request.form.get("username", ""), request.form.get("password", ""))
    return page.openLoginPage()


# UC39 Platform manager log in
# the platform manager's home page after logging in
@app.route("/manager/dashboard")
@managerLoginRequired
def platformManagerDashboard():
    return PlatformManagerLoginPage().openDashboard()


# US17 Restore company profile (UC17-R)
# the dashboard's Restore button posts the deleted profile's companyId + revision
@app.route("/designer/company/restore", methods=["POST"])
@designerLoginRequired
def restoreCompanyProfile():
    return RestoreCompanyProfilePage().submitRestore(request.form.get("companyId", type=int),
                                                     request.form.get("revision", type=int))


# US20 Add current IDP. Ownership is taken from the session in the boundary.
# categoryId comes from the drop-down as text, type=int turns it into a number (None if nothing picked)
@app.route("/designer/idps/add", methods=["GET", "POST"])
@designerLoginRequired
def addCurrentIDP():
    page = AddCurrentIDPPage()
    if request.method == "POST":
        return page.submitCurrentIDP(request.form.get("title", ""),
                                     request.form.get("categoryId", type=int),
                                     request.form.get("description", ""),
                                     request.form.get("location", ""))
    return page.clickAddCurrentIDP()


# US40 End the current manager browser session; no active-role guard is required to log out.
@app.route("/manager/logout", methods=["POST"])
def platformManagerLogout():
    return PlatformManagerLogoutPage().clickLogout()


# US45 Search IDP categories - this is also the IDP Categories list page
# /manager/categories shows everything, /manager/categories?keyword=kit only shows the matches
@app.route("/manager/categories")
@managerLoginRequired
def idpCategories():
    return SearchIDPCategoryPage().searchIDPCategories(request.args.get("keyword", ""))


# US41 Create IDP category
@app.route("/manager/categories/create", methods=["GET", "POST"])
@managerLoginRequired
def createIDPCategory():
    page = CreateIDPCategoryPage()
    if request.method == "POST":
        return page.submitIDPCategory(request.form.get("categoryName", ""),
                                      request.form.get("description", ""))
    return page.clickCreateIDPCategory()


# US42 View IDP category and the IDPs in it
@app.route("/manager/categories/<int:categoryId>")
@managerLoginRequired
def viewIDPCategory(categoryId):
    return ViewIDPCategoryPage().selectIDPCategory(categoryId)


# US43 Update IDP category
@app.route("/manager/categories/<int:categoryId>/update", methods=["GET", "POST"])
@managerLoginRequired
def updateIDPCategory(categoryId):
    page = UpdateIDPCategoryPage()
    if request.method == "POST":
        page.categoryId = categoryId
        return page.submitUpdate(request.form.get("categoryName", ""),
                                 request.form.get("description", ""))
    return page.clickUpdate(categoryId)


# US44 Suspend IDP category
# GET  = manager clicked Suspend -> show the "Are you sure?" box
# POST = manager clicked OK or Cancel in the box
@app.route("/manager/categories/<int:categoryId>/suspend", methods=["GET", "POST"])
@managerLoginRequired
def suspendIDPCategory(categoryId):
    page = SuspendIDPCategoryPage()
    if request.method == "GET":
        return page.clickSuspend(categoryId)

    page.categoryId = categoryId
    if request.form.get("choice") == "cancel":
        return page.cancelSuspend()
    return page.confirmSuspend()


# US37 View IDP view statistics
@app.route("/designer/idps/statistics/views")
@designerLoginRequired
def viewIDPViewStatistics():
    return ViewIDPViewStatisticsPage().clickViewIDPViews()


# US38 View IDP save statistics
@app.route("/designer/idps/statistics/saves")
@designerLoginRequired
def viewIDPSaveStatistics():
    return ViewIDPSaveStatisticsPage().clickViewIDPSaves()


# US46 Generate daily report
# no ?date= -> manager just opened the page, with ?date= -> they pressed "Generate report"
@app.route("/manager/reports/daily")
@managerLoginRequired
def generateDailyReport():
    page = GenerateDailyReportPage()
    if "date" in request.args:
        return page.submitDate(request.args.get("date", ""))
    return page.clickGenerateDailyReport()


# US47 Generate weekly report
@app.route("/manager/reports/weekly")
@managerLoginRequired
def generateWeeklyReport():
    page = GenerateWeeklyReportPage()
    if "date" in request.args:
        return page.submitDate(request.args.get("date", ""))
    return page.clickGenerateWeeklyReport()


# US48 Generate monthly report
@app.route("/manager/reports/monthly")
@managerLoginRequired
def generateMonthlyReport():
    page = GenerateMonthlyReportPage()
    if "date" in request.args:
        return page.submitDate(request.args.get("date", ""))
    return page.clickGenerateMonthlyReport()


# US26 View past IDPs
@app.route("/designer/past-idps")
@designerLoginRequired
def pastIDPs():
    return PastIDPListPage().openPastIDPs()


# US25 Add past IDP
@app.route("/designer/past-idps/add", methods=["GET", "POST"])
@designerLoginRequired
def addPastIDP():
    page = AddPastIDPPage()
    if request.method == "POST":
        return page.submitPastIDP(request.form.get("title", ""),
                                  request.form.get("categoryId", type=int),
                                  request.form.get("description", ""),
                                  request.form.get("location", ""))
    return page.openAddPastIDPForm()


# US29 Search past IDPs
@app.route("/designer/past-idps/search")
@designerLoginRequired
def searchPastIDPs():
    return PastIDPSearchPage().submitSearch(request.args.get("keyword", ""))


# US26 View past IDPs - one past IDP's details
@app.route("/designer/past-idps/<int:idpId>")
@designerLoginRequired
def viewPastIDP(idpId):
    return PastIDPListPage().selectPastIDP(idpId)


# US27 Update past IDP
@app.route("/designer/past-idps/<int:idpId>/edit", methods=["GET", "POST"])
@designerLoginRequired
def editPastIDP(idpId):
    page = EditPastIDPPage()
    if request.method == "POST":
        return page.submitUpdatedDetails(idpId,
                                         request.form.get("title", ""),
                                         request.form.get("categoryId", type=int),
                                         request.form.get("description", ""),
                                         request.form.get("location", ""))
    return page.openEditForm(idpId)


# US28 Delete past IDP
# GET  = designer clicked Delete -> show the "are you sure?" box
# POST = designer clicked "Delete past IDP" or Cancel in the box
@app.route("/designer/past-idps/<int:idpId>/delete", methods=["GET", "POST"])
@designerLoginRequired
def deletePastIDP(idpId):
    page = PastIDPListPage()
    if request.method == "GET":
        return page.clickDelete(idpId)
    if request.form.get("choice") == "delete":
        return page.confirmDeletion(idpId)
    return page.cancelDeletion(idpId)


# US33 Save IDP (the Save button on the US32 IDP details page)
@app.route("/customer/idps/<int:idpId>/save", methods=["POST"])
@customerLoginRequired
def saveIDP(idpId):
    return IDPDetailsPage().clickSave(idpId)


# US35 View saved list
@app.route("/customer/saved-list")
@customerLoginRequired
def savedList():
    return SavedListPage().openSavedList()


# US34 Search saved list
@app.route("/customer/saved-list/search")
@customerLoginRequired
def searchSavedList():
    return SavedListPage().submitSearch(request.args.get("keyword", ""))


if __name__ == "__main__":
    initDatabase()
    app.run(debug=True)