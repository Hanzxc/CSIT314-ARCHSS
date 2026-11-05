# Boundary: Route handler for UC29 Search Past IDPs
from flask import Blueprint, request, render_template, redirect, session
from control.searchPastIDPsController import SearchPastIDPsController

search_past_idp_bp = Blueprint('search_past_idp', __name__)

@search_past_idp_bp.route('/designer/past-idps/search', methods=['GET'])
def searchPastIDPs():
    # Session access & role check
    if session.get('user_role') != 'Interior Designer':
        return redirect('/designer/login')

    controller = SearchPastIDPsController()
    designer_id = session.get('user_id')
    keyword = request.args.get('keyword', '').strip()

    # Execute search query
    past_idps = controller.searchPastIDPs(designer_id, keyword)

    return render_template('view_past_idps.html', past_idps=past_idps, keyword=keyword) 