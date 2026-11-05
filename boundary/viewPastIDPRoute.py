# boundary/viewPastIDPRoute.py
from flask import Blueprint, render_template, session, redirect, url_for
from control.viewPastIDPController import ViewPastIDPController

view_past_idp_bp = Blueprint('view_past_idp', __name__)
controller = ViewPastIDPController()

@view_past_idp_bp.route('/designer/past-idps', methods=['GET'])
def viewPastIDPs():
    # Check for userId in session (matching app.py session structure)
    user_id = session.get('userId')
    if not user_id:
        return redirect(url_for('interiorDesignerLogin'))

    past_idps = controller.getPastIDPsByDesigner(user_id)
    return render_template('view_past_idps.html', past_idps=past_idps)