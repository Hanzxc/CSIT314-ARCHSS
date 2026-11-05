# Boundary: Route handler for UC27 Update Past IDP
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from control.updatePastIDPController import UpdatePastIDPController
from entity.idpCategory import IDPCategory

update_past_idp_bp = Blueprint('update_past_idp', __name__)

@update_past_idp_bp.route('/designer/past-idps/update/<int:idp_id>', methods=['GET', 'POST'])
def updatePastIDP(idp_id):
    if session.get('user_role') != 'Interior Designer':
        return redirect('/designer/login')

    controller = UpdatePastIDPController()
    category_entity = IDPCategory()
    designer_id = session.get('user_id')

    # Security check: verify project ownership
    idp_data = controller.getIDPForEdit(idp_id, designer_id)
    if not idp_data:
        flash("Past IDP not found or access denied.", "error")
        return redirect('/designer/past-idps')

    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('categoryId')
        description = request.form.get('description')
        location = request.form.get('location')

        success, message = controller.updatePastIDP(
            idpId=idp_id,
            designerId=designer_id,
            categoryId=category_id,
            title=title,
            description=description,
            location=location
        )

        if success:
            flash(message, "success")
            return redirect('/designer/past-idps')
        else:
            flash(message, "error")

    active_categories = category_entity.getActiveCategories()
    return render_template('update_past_idp.html', idp=idp_data, categories=active_categories)