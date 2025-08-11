from flask import Blueprint, render_template, g, request, session as session_web
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
              {'name': 'Utilisateurs', 'html': 'users.html', 'title': "Crypt'Us Bee | Utilisateurs", 'place': 5, 'id': 'utilisateurs'},
              {'name': 'Connexion', 'html': 'connect.html', 'title': "Crypt'Us Bee | Connexion", 'place': 6, 'id': 'connect'},
              {'name': 'Compte', 'html': 'account.html', 'title': "Crypt'Us Bee | Compte", 'place': 7, 'id': 'account'}]

def user_search_on_mongo(pseudo: str, pwd: str, id_file: str, public_key_file: str):
    #TODO: Création de la requête de recherche d'utilisateur dans la base de données
    pass

def request_api_for_user(pseudo: str, pwd: str, id_file: str, public_key_file: str):
    #TODO: Création de la requête API pour décrypter l'utilisateur
    pass

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

@home_bp.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'GET':
        return render_template(template_name_or_list=pages_list[6]['html'],
                           ac=pages_list[6]['place'],
                           title=pages_list[6]['title'],
                           id=pages_list[6]['id'],
                           to_connect=getattr(g, 'need_connection', False))
    # TODO Méthode post à terminer pour la connection
    else:
        pseudo = request.form.get('pseudo')
        pwd = request.form.get('pwd')
        id_file = request.files.get('id_file')
        public_key_file = request.files.get('public_key_file')

        #TODO: Création de la requête de recherche d'utilisateur dans la base de données
        #TODO: Vérification des identifiants, mots de passe et certificats
        #TODO: Authentification de l'utilisateur
        #TODO: Gestion des erreurs
        session_web['pseudo'] = pseudo
        session_web['pwd'] = pwd
        session_web['id_file'] = id_file
        session_web['public_key_file'] = public_key_file
        return render_template(template_name_or_list=pages_list[0]['html'],
                               ac=pages_list[0]['place'],
                               title=pages_list[0]['title'],
                               id=pages_list[0]['id'],
                               to_connect=getattr(g, 'need_connection', False),
                               header_value={'identifiant': pseudo, 'mot_de_passe': pwd, 'id_file': id_file, 'public_key_file': public_key_file})


@home_bp.route('/account', methods=['GET'])
def account():
    return render_template(template_name_or_list=pages_list[7]['html'],
                           ac=pages_list[7]['place'],
                           title=pages_list[7]['title'],
                           id=pages_list[7]['id'],
                           to_connect=getattr(g, 'need_connection', False))
