# boundary/deletePastIDPRoute.py
from flask import Blueprint, request, session, redirect, url_for, flash
from control.deletePastIDPController import DeletePastIDPController

delete_past_idp_bp = Blueprint('delete_past_idp', __name__)
controller = DeletePastIDPController()

@delete_past_idp_bp.route('/designer/past-idps/<int:idp_id>/delete', methods=['POST'])
def deletePastIDP(idp_id):
    if 'userId' not in session:
        return redirect(url_for('interiorDesignerLogin'))

    designer_id = session.get('userId')
    success, message = controller.deletePastIDP(idp_id, designer_id)

    if success:
        flash("Past IDP deleted successfully.", "success")
    else:
        flash(message, "error")

    return redirect(url_for('view_past_idp.viewPastIDPs'))