from flask import Blueprint, g, jsonify
from typing import Tuple

link_bp = Blueprint('links',
                    __name__,
                    static_folder='../statics/statics_home',
                    template_folder='../templates/templates_home',
                    url_prefix='/common')

def get_element_from_usb_key() -> Tuple[str, str]:
    '''
    Récupération de l'identifiant utilisateur et de la clé publique
    '''
    user = ''
    link_id = ''
    return user, link_id

def create_header():
    user, link_id = get_element_from_usb_key()
    header_value = {
        'X-User': user,
        'X-Link-ID': link_id
    }
    return jsonify(header_value), 200

@link_bp.errorhandler(404)
def not_found(error: Exception):
    return jsonify({'error': f'{error}'}), 404

@link_bp.errorhandler(500)
def internal_server_error(error: Exception):
    return jsonify({'error': f'{error}'}), 500

@link_bp.route('/<user>/<link_id>', methods=['POST'])
def index(user: str, link_id: str):
    header_value = g.get('request').headers.get('Your-Header-Name', 'Default-Value')
    return jsonify({'user': user, 'link_id': link_id, 'header_value': header_value}), 200
