# Boundary: Route handler for UC34 Search Saved List
from flask import Blueprint, request, render_template, redirect, session
from control.searchSavedListController import SearchSavedListController
from boundary.customerAccess import customerAccess

search_saved_list_bp = Blueprint('search_saved_list', __name__)

@search_saved_list_bp.route('/customer/saved-list/search', methods=['GET'])
def searchSavedList():
    account, denied = customerAccess()
    if denied is not None:
        return denied

    controller = SearchSavedListController()
    customer_id = account.userId
    keyword = request.args.get('keyword', '').strip()

    # Execute search query
    saved_idps = controller.searchSavedList(customer_id, keyword)

    return render_template('view_saved_list.html', account=account, saved_idps=saved_idps,
                           keyword=keyword, activePage='savedIDPs')
