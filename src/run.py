""" Run module for running the app """

# import modules
import utils.const as const
import app.views as flask_app

# constants
HOST = const.APP_HOST
PORT = const.APP_PORT

# flask app
app = flask_app.app


if __name__ == "__main__":

    # runs flask app
    app.run(
        host=HOST,
        port=PORT,
        debug=True,
        load_dotenv=True
    )
