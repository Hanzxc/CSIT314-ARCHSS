# Boundary: ViewUserAccountPage - UC9 View user account (US9)
# template: templates/viewUserAccount.html

from flask import render_template

from control.viewUserAccountController import ViewUserAccountController

MSG_NOT_FOUND = "Account not found"


class ViewUserAccountPage:
    # UC9 View user account
    # just sets up the controller
    def __init__(self):
        self.viewUserAccountController = ViewUserAccountController()

    # UC9 View user account
    # admin clicked View on an account - show its details, or "Account not found"
    def clickView(self, userId):
        account = self.viewUserAccountController.viewUserAccount(userId)
        if account is not None:
            # the controller keeps the account's profile for us (seq diagram msg 8)
            profile = self.viewUserAccountController.profile
            return self.displayAccountDetails(account, profile)
        return self.displayErrorMessage(MSG_NOT_FOUND)

    def displayAccountDetails(self, account, profile):
        # everything except the password (not even the hash)
        return render_template("viewUserAccount.html", activePage="accounts",
                               account=account, profile=profile)

    def displayErrorMessage(self, msg):
        # alt flow 2a - just the message and a link back to the list
        return render_template("viewUserAccount.html", activePage="accounts",
                               account=None, errorMessage=msg)
