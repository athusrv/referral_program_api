import os

from flask import Flask

from controllers.login import login
from controllers.referral_code import refcode
from controllers.signup import signup
from controllers.statement import statement
from database import migrate

app = Flask(__name__)


def register_blueprints():
    app.register_blueprint(signup)
    app.register_blueprint(refcode)
    app.register_blueprint(login)
    app.register_blueprint(statement)


if __name__ == '__main__':
    # migrate the database schema
    migrate()

    register_blueprints()

    # start the application
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
