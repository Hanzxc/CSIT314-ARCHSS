# boundary/searchPastIDPsRoute.py
from flask import Blueprint, render_template, request, session, redirect, url_for
from control.searchPastIDPsController import SearchPastIDPsController

search_past_idp_bp = Blueprint('search_past_idp', __name__)
controller = SearchPastIDPsController()

@search_past_idp_bp.route('/designer/past-idps/search', methods=['GET'])
def searchPastIDPs():
    if 'userId' not in session:
        return redirect(url_for('interiorDesignerLogin'))

    designer_id = session.get('userId')
    query = request.args.get('query', '').strip()

    past_idps = controller.searchPastIDPs(designer_id, query)
    return render_template('view_past_idps.html', past_idps=past_idps, query=query)