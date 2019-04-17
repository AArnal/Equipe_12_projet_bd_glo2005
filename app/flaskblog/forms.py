from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

"""
Classe concernant les informations des formulaires d'inscriptions 
Dans un premier temps on définit les variables requises auquelles on ajoute des spécificitées qui seront vérifiées lors des appels validate 
Dans un second temps, définition de la fonction permettant de vérifier que le pseudo n'est pas déjà présent dans la base de donnée. Affiche un message d'erreur au besoin
Dans un troisième temps, définition de la fonction permettant de vérifier que l'email n'est pas déjà présent dans la base de donnée. Affiche un message d'erreur au besoin
"""
class RegistrationForm(FlaskForm):
    username = StringField('Pseudo',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mots de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mots de passe',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S\'inscrire')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce pseudo est déjà utilisé. Merci d\'en choisir un autre')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cette Email est déjà utilisée. Merci d\'en choisir une autre')

"""
Classe concernant les informations du formulaire de connexion
Dans un premier temps on définit les variables requises auquelles on ajoute des spécificitées qui seront vérifiées lors des appels validate 
"""
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mots de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connection')

"""
Classe concernant les informations du formulaire de modification d'information du compte
Dans un premier temps on définit les variables requises auquelles on ajoute des spécificitées qui seront vérifiées lors des appels validate 
Dans un second temps, définition de la fonction permettant de vérifier que le pseudo n'est pas déjà présent dans la base de donnée. Affiche un message d'erreur au besoin
Dans un troisième temps, définition de la fonction permettant de vérifier que l'email n'est pas déjà présent dans la base de donnée. Affiche un message d'erreur au besoin
"""
class UpdateAccountForm(FlaskForm):
    username = StringField('Pseudo',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Mettre à jour sa photo de profile', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Appliquer')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ce pseudo est déjà utilisé. Merci d\'en choisir un autre')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cette Email est déjà utilisée. Merci d\'en choisir une autre')

"""
Classe concernant les informations du formulaire de création d'une nouvelle publication
Dans un premier temps on définit les variables requises auquelles on ajoute des spécificitées qui seront vérifiées lors des appels validate 
"""
class PostForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    content = TextAreaField('Contenu', validators=[DataRequired()])
    submit = SubmitField('Publier')

"""
Classe concernant les informations du formulaire de demande de modification du mots de passe
Dans un premier temps, on définit les variables requises auquelles on ajoute des spécificitées qui seront vérifiées lors des appels validate 
Dans un second temps, définition de la fonction permettant de vérifier que l'email est bien associé à un compte de la base de donnée. Affiche un message d'erreur au besoin 
"""

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Envoyer')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Auncun compte n\'est associé à cette Email. Commencez par vous enregistrer')

"""
Classe concernant les informations du formulaire de modification du mots de passe
Dans un premier temps on définit les variables requises auquelles on ajoute des spécificitées qui seront vérifiées lors des appels validate 
"""
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mots de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer mots de passe',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Appliquer')