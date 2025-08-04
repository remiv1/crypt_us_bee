from flask import Flask
from routes.home import home_bp
from routes.admin import admin_bp
from typing import Any

interface = Flask(__name__)

# enregistrement des routes blueprints
interface.register_blueprint(home_bp)
interface.register_blueprint(admin_bp)

@interface.before_request
def before_request() -> None:
    """Hook to run before each request."""
    pass

@interface.after_request
def after_request(response: Any) -> Any:
    """Hook to run after each request."""
    return response

if __name__ == "__main__":
    interface.run(debug=True, host='0.0.0.0', port=5001)