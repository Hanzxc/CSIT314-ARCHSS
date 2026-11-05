# Flask app - links each URL to its boundary (page) class
# run with:  python app.py   then open http://127.0.0.1:5000

from functools import wraps

from flask import Flask, request, redirect, url_for, session, render_template, abort

from boundary.interiorDesignerLoginPage import InteriorDesignerLoginPage
from boundary.createCompanyProfilePage import CreateCompanyProfilePage
from boundary.viewCompanyProfilePage import ViewCompanyProfilePage
from boundary.updateCompanyProfilePage import UpdateCompanyProfilePage
from boundary.deleteCompanyProfilePage import DeleteCompanyProfilePage
from boundary.searchCompanyInformationPage import SearchCompanyInformationPage
from boundary.interiorDesignerLogoutPage import InteriorDesignerLogoutPage
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.userAccount import UserAccount

from boundary.restoreCompanyProfilePage import RestoreCompanyProfilePage
from boundary.platformManagerLoginPage import PlatformManagerLoginPage
from control.platformManagerLoginController import PlatformManagerLoginController
from boundary.loginPage import LoginPage
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
from database.db import initDatabase

from boundary.addCurrentIDPPage import AddCurrentIDPPage
from boundary.platformManagerLogoutPage import PlatformManagerLogoutPage
from boundary.createIDPCategoryPage import CreateIDPCategoryPage
from boundary.viewIDPCategoryPage import ViewIDPCategoryPage
from boundary.updateIDPCategoryPage import UpdateIDPCategoryPage
from boundary.suspendIDPCategoryPage import SuspendIDPCategoryPage
from boundary.searchIDPCategoryPage import SearchIDPCategoryPage

app = Flask(__name__)
app.secret_key = "change-this-later"     # TODO: move to an environment variable


@app.after_request
def noCache(response):
    # stops the browser showing an old admin page when you press Back after logging out (US2 wireframe 4b)
    response.headers["Cache-Control"] = "no-store"
    return response


def loginRequired(routeFunction):
    # put @loginRequired on any admin page -> not logged in = sent back to the login page
    @wraps(routeFunction)
    def wrapper(*args, **kwargs):
        if "userId" not in session:
            return redirect(url_for("login"))
        # US13: the existing management routes are for admins. Recheck the
        # database rather than treating any authenticated session as an admin.
        account = UserAccount().getUserAccount(session["userId"])
        profile = UserProfile().getUserProfile(account.profileId) if account else None
        if not account or not account.isActive() or not profile or not profile.isActive():
            abort(403)
        if routeFunction.__name__ == "dashboard" and InteriorDesignerLoginController().isInteriorDesigner(account):
            return redirect(url_for("interiorDesignerDashboard"))
        if routeFunction.__name__ == "dashboard" and PlatformManagerLoginController().isPlatformManager(account):
            return redirect(url_for("platformManagerDashboard"))
        if not {"Manage user accounts", "Manage user profiles"}.issubset(profile.permissions):
            abort(403)
        return routeFunction(*args, **kwargs)
    return wrapper


def designerLoginRequired(routeFunction):
# US14 – US18: Verify active Interior Designer access before handling company profile requests.
    @wraps(routeFunction)
    def wrapper(*args, **kwargs):
        userId = session.get("userId")
        if userId is None:
            return redirect(url_for("interiorDesignerLogin"))
        designer = InteriorDesignerLoginController().getAuthenticatedDesigner(userId)
        if designer is None:
            abort(403)
        return routeFunction(*args, **kwargs)
    return wrapper


def managerLoginRequired(routeFunction):
    # US41 - US45: being logged in as a platform manager is the precondition of these use cases (US39),
    # so the pages don't re-check it. this only stops a crash when there's no session at all
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


# US13: dedicated designer entry point, using the same CSS and entities.
@app.route("/designer/login", methods=["GET", "POST"])
def interiorDesignerLogin():
    page = InteriorDesignerLoginPage()
    if request.method == "POST":
        return page.submitLogin(request.form.get("username", ""), request.form.get("password", ""))
    return page.openLoginPage()


# UC13 Interior designer log in
# the designer's home page after logging in (the page class checks the login itself)
@app.route("/designer/dashboard")
def interiorDesignerDashboard():
    return InteriorDesignerLoginPage().openDashboard()


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


# US17 GET opens confirmation; only an explicit, validated POST can delete.
@app.route("/designer/company/delete", methods=["GET", "POST"])
@designerLoginRequired
def deleteCompanyProfile():
    page = DeleteCompanyProfilePage()
    if request.method == "POST":
        return page.submitDelete(request.form.get("choice", ""),
                                 request.form.get("companyId", type=int),
                                 request.form.get("confirmationToken", ""))
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
def platformManagerDashboard():
    return PlatformManagerLoginPage().openDashboard()


# US17 recovery: restore saved company details without re-entering them.
@app.route("/designer/company/restore", methods=["POST"])
@designerLoginRequired
def restoreCompanyProfile():
    return RestoreCompanyProfilePage().submitRestore(request.form.get("confirmationToken", ""))


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


if __name__ == "__main__":
    initDatabase()
    app.run(debug=True)


