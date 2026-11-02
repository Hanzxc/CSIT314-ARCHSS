"""Share US30 customer identity with the saved-project blueprints."""
from flask import redirect, render_template, session, url_for

from control.customerLoginController import CustomerLoginController


def customerAccess():
    if session.get("userId") is None:
        return None, redirect(url_for("customerLogin"))
    account = CustomerLoginController().getAuthenticatedCustomer(session["userId"])
    if account is None:
        return None, (render_template("customerAccessDenied.html"), 403)
    return account, None
