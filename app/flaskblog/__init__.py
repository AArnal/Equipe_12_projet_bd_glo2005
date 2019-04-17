
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
"""Définition de la clé secret permettant de gérérer les données chiffrées"""
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
"""Configuration, pour faire le lien avec la base de donnée et l'application"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.cli.command()
def init_db():
    models.init_db()
"""Définition des variables nécessaire à la gestion de session utilisateur"""
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
"""Définition des variables nécessaire à la gestion de l'envoi de mail à l'utilisateur"""
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ulaval2019@gmail.com'
app.config['MAIL_PASSWORD'] = 'Universite2019' 
"""os.environ.get("""
mail = Mail(app)

from flaskblog import routes
