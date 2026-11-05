# Boundary: Route handler for UC35 View Saved List
from flask import Blueprint, render_template, redirect, session
from control.viewSavedListController import ViewSavedListController

view_saved_list_bp = Blueprint('view_saved_list', __name__)

@view_saved_list_bp.route('/customer/saved-list', methods=['GET'])
def viewSavedList():
    # Session access & role check (Customers only)
    if session.get('user_role') != 'Customer':
        return redirect('/login')

    controller = ViewSavedListController()
    customer_id = session.get('user_id')

    # Fetch all IDPs bookmarked by the logged-in customer
    saved_idps = controller.getSavedListByCustomer(customer_id)

    return render_template('view_saved_list.html', saved_idps=saved_idps)