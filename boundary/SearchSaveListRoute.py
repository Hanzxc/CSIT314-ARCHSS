# Boundary: Route handler for UC34 Search Saved List
from flask import Blueprint, request, render_template, redirect, session
from control.searchSavedListController import SearchSavedListController

search_saved_list_bp = Blueprint('search_saved_list', __name__)

@search_saved_list_bp.route('/customer/saved-list/search', methods=['GET'])
def searchSavedList():
    # Session access & role check (Customers only)
    if session.get('user_role') != 'Customer':
        return redirect('/login')

    controller = SearchSavedListController()
    customer_id = session.get('user_id')
    keyword = request.args.get('keyword', '').strip()

    # Execute search query
    saved_idps = controller.searchSavedList(customer_id, keyword)

    return render_template('view_saved_list.html', saved_idps=saved_idps, keyword=keyword) 
