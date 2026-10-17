# Flask app - links each URL to its boundary (page) class
# run with:  python app.py   then open http://127.0.0.1:5000

from flask import Flask, request, redirect, url_for, session, render_template

from boundary.loginPage import LoginPage
from boundary.logoutPage import LogoutPage
from boundary.createUserProfilePage import CreateUserProfilePage
from boundary.viewUserProfilePage import ViewUserProfilePage
from boundary.updateUserProfilePage import UpdateUserProfilePage
from boundary.suspendUserProfilePage import SuspendUserProfilePage
from entity.userProfile import UserProfile
from database.db import initDatabase

app = Flask(__name__)
app.secret_key = "change-this-later"     # TODO: move to an environment variable


@app.after_request
def noCache(response):
    # stops the browser showing an old admin page when you press Back after logging out (US2 wireframe 4b)
    response.headers["Cache-Control"] = "no-store"
    return response


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
def dashboard():
    # not logged in -> back to the login page
    if "userId" not in session:
        return redirect(url_for("login"))

    profile = UserProfile().getUserProfile(session["profileId"])
    return render_template("dashboard.html", activePage="dashboard",
                           username=session["username"],
                           profileName=profile.profileName if profile else "")


# User Profiles list page (has the Create and View buttons)
@app.route("/profiles")
def profiles():
    # TODO: render userProfiles.html with every profile
    pass


# US3 Create user profile
@app.route("/profiles/create", methods=["GET", "POST"])
def createUserProfile():
    page = CreateUserProfilePage()
    if request.method == "POST":
        return page.submitUserProfile(request.form.get("profileName", ""),
                                      request.form.get("description", ""),
                                      request.form.getlist("permissions"))
    return page.clickCreateUserProfile()


# US4 View user profile
@app.route("/profiles/<int:profileId>")
def viewUserProfile(profileId):
    return ViewUserProfilePage().selectUserProfile(profileId)


# US5 Update user profile
@app.route("/profiles/<int:profileId>/update", methods=["GET", "POST"])
def updateUserProfile(profileId):
    page = UpdateUserProfilePage()
    if request.method == "POST":
        page.profileId = profileId
        return page.submitUpdate(request.form.get("profileName", ""),
                                 request.form.get("description", ""),
                                 request.form.getlist("permissions"))
    return page.clickUpdate(profileId)


# US6 Suspend user profile (only runs after the admin clicks OK on the confirm box)
@app.route("/profiles/<int:profileId>/suspend", methods=["POST"])
def suspendUserProfile(profileId):
    page = SuspendUserProfilePage()
    page.profileId = profileId
    return page.confirmSuspend()


if __name__ == "__main__":
    initDatabase()
    app.run(debug=True)
