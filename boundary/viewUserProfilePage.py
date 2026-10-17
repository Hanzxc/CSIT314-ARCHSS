# Boundary: ViewUserProfilePage - UC4 View user profile (US4)
# template: templates/viewUserProfile.html

from flask import render_template

from control.viewUserProfileController import ViewUserProfileController

MSG_NOT_FOUND = "User profile not found"


class ViewUserProfilePage:
    def __init__(self):
        self.viewUserProfileController = ViewUserProfileController()

    def selectUserProfile(self, profileId):
        # TODO (sequence diagram msgs 2-8):
        # - profile = self.viewUserProfileController.getUserProfile(profileId)
        # - profile not None -> return self.displayUserProfile(profile)
        # - profile is None  -> return self.displayErrorMessage(MSG_NOT_FOUND)
        pass

    def displayUserProfile(self, profile):
        # TODO: render_template("viewUserProfile.html", profile=profile)
        # show name, description, status badge and every permission
        pass

    def displayErrorMessage(self, msg):
        # TODO: render_template("viewUserProfile.html", profile=None, errorMessage=msg)
        pass
