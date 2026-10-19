# Boundary: ViewUserProfilePage - UC4 View user profile (US4)
# template: templates/viewUserProfile.html

from flask import render_template

from control.viewUserProfileController import ViewUserProfileController

MSG_NOT_FOUND = "User profile not found"


class ViewUserProfilePage:
    def __init__(self):
        self.viewUserProfileController = ViewUserProfileController()

    def selectUserProfile(self, profileId):
        profile = self.viewUserProfileController.getUserProfile(profileId)
        if profile is not None:
            return self.displayUserProfile(profile)
        return self.displayErrorMessage(MSG_NOT_FOUND)

    def displayUserProfile(self, profile):
        # name, description, status badge and every permission (wireframe 4b)
        return render_template("viewUserProfile.html", activePage="profiles", profile=profile)

    def displayErrorMessage(self, msg):
        # wireframe 4c - just the message and a link back to the list
        return render_template("viewUserProfile.html", activePage="profiles",
                               profile=None, errorMessage=msg)
