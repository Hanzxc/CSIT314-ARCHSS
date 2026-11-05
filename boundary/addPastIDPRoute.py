# boundary/addPastIDPRoute.py
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from control.addPastIDPController import AddPastIDPController
from database.db import getConnection  # <-- Use your DB connection helper

add_past_idp_bp = Blueprint('add_past_idp', __name__)
controller = AddPastIDPController()

@add_past_idp_bp.route('/designer/past-idps/add', methods=['GET', 'POST'])
def addPastIDP():
    if 'userId' not in session:
        return redirect(url_for('interiorDesignerLogin'))

    # Directly fetch active categories from the database
    conn = getConnection()
    categories = conn.execute(
        "SELECT categoryId, categoryName FROM idp_category WHERE status = 'Active'"
    ).fetchall()
    conn.close()

    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('categoryId', type=int)
        description = request.form.get('description')
        location = request.form.get('location')
        designer_id = session.get('userId')

        success, message = controller.addPastIDP(title, category_id, description, location, designer_id)
        if success:
            flash("Past IDP added successfully.", "success")
            return redirect(url_for('view_past_idp.viewPastIDPs'))
        else:
            flash(message, "error")

    return render_template('add_past_idp.html', categories=categories)