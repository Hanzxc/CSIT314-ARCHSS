# boundary/viewSavedListRoute.py
from flask import Blueprint, render_template, redirect, session
from control.viewSavedListController import ViewSavedListController
from boundary.customerAccess import customerAccess

view_saved_list_bp = Blueprint('view_saved_list', __name__)

@view_saved_list_bp.route('/customer/saved-list', methods=['GET'])
def viewSavedList():
    account, denied = customerAccess()
    if denied is not None:
        return denied

    controller = ViewSavedListController()
    customer_id = account.userId
    saved_idps = controller.getSavedListByCustomer(customer_id)

    return render_template('view_saved_list.html', account=account, saved_idps=saved_idps,
                           keyword='', activePage='savedIDPs')
