# boundary/updatePastIDPRoute.py
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from control.updatePastIDPController import UpdatePastIDPController
from database.db import getConnection

# Define the blueprint BEFORE using it in decorators below!
update_past_idp_bp = Blueprint('update_past_idp', __name__)
controller = UpdatePastIDPController()

@update_past_idp_bp.route('/designer/past-idps/<int:idp_id>/update', methods=['GET', 'POST'])
def updatePastIDP(idp_id):
    if 'userId' not in session:
        return redirect(url_for('interiorDesignerLogin'))

    designer_id = session.get('userId')

    # Fetch active categories for select dropdown
    conn = getConnection()
    categories = conn.execute(
        "SELECT categoryId, categoryName FROM idp_category WHERE status = 'Active'"
    ).fetchall()
    conn.close()

    if request.method == 'POST':
        category_id = request.form.get('categoryId', type=int)
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        location = request.form.get('location', '')

        # Matches Controller signature: (idpId, designerId, categoryId, title, description, location)
        success, message = controller.updatePastIDP(idp_id, designer_id, category_id, title, description, location)
        if success:
            flash(message, "success")
            return redirect(url_for('view_past_idp.viewPastIDPs'))
        else:
            flash(message, "error")

    idp = controller.getIDPById(idp_id)
    if not idp:
        flash("Past IDP not found.", "error")
        return redirect(url_for('view_past_idp.viewPastIDPs'))

    return render_template('update_past_idp.html', idp=idp, categories=categories)