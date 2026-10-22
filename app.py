# Flask app - links each URL to its boundary (page) class
# run with:  python app.py   then open http://127.0.0.1:5000

from functools import wraps

from flask import Flask, request, redirect, url_for, session, render_template

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
        return routeFunction(*args, **kwargs)
    return wrapper


@app.context_processor
def headerInfo():
    # base.html shows "Logged in as ..." on every admin page, this saves passing it in every time
    if "userId" not in session:
        return {}
    profile = UserProfile().getUserProfile(session["profileId"])
    return {"username": session["username"],
            "profileName": profile.profileName if profile else ""}


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


if __name__ == "__main__":
    initDatabase()
    app.run(debug=True)
