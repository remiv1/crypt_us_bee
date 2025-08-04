from flask import Blueprint

admin_bp = Blueprint('admin',
                     __name__,
                     static_folder='../statics/statics_admin',
                     template_folder='../templates/templates_admin',
                     url_prefix='/admin')

@admin_bp.route('/')
def admin_dashboard():
    return "Welcome to the Admin Dashboard!"