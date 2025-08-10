from flask import Blueprint, render_template, g
from typing import List, Dict, Any

home_bp = Blueprint('home',
                    __name__,
                    static_folder='../statics/statics_home',
                    template_folder='../templates/templates_home',
                    url_prefix='/home')

pages_list: List[Dict[str, Any]] = [{'name': 'Accueil', 'html': 'accueil.html', 'title': "Crypt'Us Bee | Accueil", 'place': 0, 'id': 'accueil'},
              {'name': 'A propos', 'html': 'about.html', 'title': "Crypt'Us Bee | À propos", 'place': 1, 'id': 'apropos'},
              {'name': 'Tableau de bord', 'html': 'dashboard.html', 'title': "Crypt'Us Bee | Tableau de bord", 'place': 2, 'id': 'dashboard'},
              {'name': 'Postes de travail', 'html': 'workstations.html', 'title': "Crypt'Us Bee | Postes de travail", 'place': 3, 'id': 'postes'},
              {'name': 'Clés', 'html': 'keys.html', 'title': "Crypt'Us Bee | Clés", 'place': 4, 'id': 'cles'},
              {'name': 'Utilisateurs', 'html': 'users.html', 'title': "Crypt'Us Bee | Utilisateurs", 'place': 5, 'id': 'utilisateurs'}]

@home_bp.errorhandler(404)
def not_found(error: Exception):
    return render_template('404.html', error=error), 404

@home_bp.errorhandler(500)
def internal_server_error(error: Exception):
    return render_template('500.html', error=error), 500

@home_bp.route('/', methods=['GET'])
def index():
    return render_template(template_name_or_list=pages_list[0]['html'],
                           ac=pages_list[0]['place'],
                           title=pages_list[0]['title'],
                           id=pages_list[0]['id'],
                           to_connect=getattr(g, 'need_connection', False))

@home_bp.route('/about', methods=['GET'])
def about():
    return render_template(template_name_or_list=pages_list[1]['html'],
                           ac=pages_list[1]['place'],
                           title=pages_list[1]['title'],
                           id=pages_list[1]['id'],
                           to_connect=getattr(g, 'need_connection', False))

@home_bp.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template(template_name_or_list=pages_list[2]['html'],
                           ac=pages_list[2]['place'],
                           title=pages_list[2]['title'],
                           id=pages_list[2]['id'],
                           to_connect=getattr(g, 'need_connection', False))

@home_bp.route('/workstations', methods=['GET'])
def workstations():
    return render_template(template_name_or_list=pages_list[3]['html'],
                           ac=pages_list[3]['place'],
                           title=pages_list[3]['title'],
                           id=pages_list[3]['id'],
                           to_connect=getattr(g, 'need_connection', False))

@home_bp.route('/keys', methods=['GET'])
def keys():
    return render_template(template_name_or_list=pages_list[4]['html'],
                           ac=pages_list[4]['place'],
                           title=pages_list[4]['title'],
                           id=pages_list[4]['id'],
                           to_connect=getattr(g, 'need_connection', False))

@home_bp.route('/users', methods=['GET'])
def users():
    return render_template(template_name_or_list=pages_list[5]['html'],
                           ac=pages_list[5]['place'],
                           title=pages_list[5]['title'],
                           id=pages_list[5]['id'],
                           to_connect=getattr(g, 'need_connection', False))
