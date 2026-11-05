from flask import Blueprint, render_template, redirect, session
from control.viewPastIDPsController import ViewPastIDPsController

view_past_idp_bp = Blueprint('view_past_idp', __name__)

@view_past_idp_bp.route('/designer/past-idps', methods=['GET'])
def view_past_idps():
    if session.get('user_role') != 'Interior Designer':
        return redirect('/designer/login')

    controller = ViewPastIDPsController()
    past_idps = controller.getPastIDPsByDesigner(session.get('user_id'))

    return render_template('view_past_idps.html', past_idps=past_idps)