"""Creates local instance of flask app"""

# imports
from flask import Flask
from api.routes import views


def create_app(test_config=None):
    """Create and configure a local instance of the Flask application."""

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(SECRET_KEY="dev")
    else:
        app.config.from_mapping(test_config)

    # homepage- http://127.0.0.1:5000/
    @app.route("/")
    def home():
        return "Hello Elastic!"

    # apply the blueprints to the app
    app.register_blueprint(views.bp)

    return app
