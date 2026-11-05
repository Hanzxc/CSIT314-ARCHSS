# Boundary: Route handler for UC33 Save / Bookmark IDP
from flask import Blueprint, request, redirect, url_for, flash, session
from control.saveIDPController import SaveIDPController

save_idp_bp = Blueprint('save_idp', __name__)

@save_idp_bp.route('/customer/save-idp/<int:idp_id>', methods=['POST'])
def toggleSaveIDP(idp_id):
    # Session access & role check (Customers only)
    if session.get('user_role') != 'Customer':
        flash("Please log in as a Customer to save projects.", "error")
        return redirect('/login')

    controller = SaveIDPController()
    customer_id = session.get('user_id')

    # Execute toggle save/unsave logic
    success, is_saved, message = controller.toggleSaveIDP(customer_id, idp_id)

    flash(message, "info")

    # Redirect back to the page the user was previously viewing
    return redirect(request.referrer or url_for('view_saved_list.viewSavedList')) 