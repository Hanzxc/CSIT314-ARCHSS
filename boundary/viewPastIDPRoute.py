# Boundary: Route handler for UC26 View Past IDPs
from flask import Blueprint, render_template, redirect, session
from control.viewPastIDPsController import ViewPastIDPsController

view_past_idp_bp = Blueprint('view_past_idp', __name__)

@view_past_idp_bp.route('/designer/past-idps', methods=['GET'])
def viewPastIDPs():
    # Session access & role check
    if session.get('user_role') != 'Interior Designer':
        return redirect('/designer/login')

    controller = ViewPastIDPsController()
    designer_id = session.get('user_id')

    # Fetch all past IDPs owned by the logged-in designer
    past_idps = controller.getPastIDPsByDesigner(designer_id)

    return render_template('view_past_idps.html', past_idps=past_idps)