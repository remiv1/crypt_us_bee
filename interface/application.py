from flask import Flask, session, g, request
from routes.home import home_bp
from routes.admin import admin_bp
from routes.links import link_bp
from typing import Any
from waitress import serve

interface = Flask(__name__)

# enregistrement des routes blueprints
interface.register_blueprint(home_bp)
interface.register_blueprint(admin_bp)
interface.register_blueprint(link_bp)

@interface.before_request
def before_request() -> None:
    """Hook to run before each request."""
    client_ip = request.remote_addr
    if client_ip and client_ip.startswith('192.168.'):
        g.local = True
    else:
        g.local = False

    if not session.get('user_id'):
        # Gérer le cas où la session n'existe pas
        g.need_connection = True
    else:
        g.need_connection = False


@interface.after_request
def after_request(response: Any) -> Any:
    response.headers['Cache-Control'] = 'no-store'  #TODO Retrait option DEV
    return response

if __name__ == "__main__":
    serve(interface, host='0.0.0.0', port=5000, threads=4)