import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

"""
Routes permettant l'accès à la page d'accueil
Initialise la variable page
Récupère les publications et les classes par ordre de sortie la plus récente par page de 5 éléments
"""
@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

"""
Routes permettant l'accès à la page information
"""
@app.route("/about")
def about():
    return render_template('about.html', title='About')

"""
Route permettant l'accès à la page d'inscription ou la page d'accueil si l'utilisateur est déjà connecté
Pour une inscripttion à l'aide des fonctions de validation des données passées en post avec le formulaire
Les mots de passe est hacher puis encrypté avec bcrypt afin d'assuré une sécurité optimale.
Toutes les informations sont ensuites passé à un objet user qui est ajouté à la base de donnée et à la session utilisateur
Un message de succès est affiché si tout c'est bien déroulé (sinon les fonctions de validation de donnée affiche un message d'erreur)
"""
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

"""
Routes permettant l'accès à la page se connecter ou la page d'accueil si l'utilisateur est déjà connecté
Dans un premier temps on vérifie si l'utilisateur est connecté si oui redirection à la page d'accueil
Dans un second temps on vérifie que les informations passé en post avec le formulaire de connection sont valides
On vérifie que l'adresse email est bien présente et est unique dans la base de donnée
Si oui, on vérifie que le mots de passe passé par le formulaire et celui dans la base de donnée sont les mêmes en les gardant crypté
Si oui, à la fonction login_user les informations de l'utilisateur pour qu'il reste connecté pendant sa session sur le site puis on le redirige vers la page home
Un message de succès est affiché si tout c'est bien déroulé
"""
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

"""
Routes permettant l'accès à la page home en déconnectant l'utilisateur actuel à l'aide la fonction logout_user() qui supprime les informations de sessions de l'utilisateur
"""
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

"""
Cette fonction, permet de sauvegarder une nouvelle image de profil dans la base de donnée. 
Dans un premier temps on récupère un token aléatoir en hexa d'une certaine taille
Puis on mélange le nom de l'image avec le token aléatoire pour garantir une confidentialité
Enfin on redimensionne l'image et on la retourne au bon format et avec un nouveau nom
"""
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

"""
Route permettant l'accès à la page compte accessible que si l'utilisateur est connecté
Cette page permet la modification des informations personnelles
Pour cela, dans un premier temps on vérifie que les informations transmise en post sont valides
Si dans le formulaire est présent une image on appelle la fonction de traitement de l'image et on la sauvegarde puis passe à la variable de session utilisateur
On récupère alors les autres informations et on les sauvegardes et ajoute à la session utilisateur
On affiche un message en succès si ça c'est bien déroulé et l'utilisateur est redirigé vers la page de compte
Si on a une requette get on réccupère les informations de l'utilisateur courant et on les renvois à la page compte de ce dernier
"""
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

"""
Routes permettant l'accès à la page Nouvelle publication
Dans un premiert temps on vérifie que les informations passées en POST sont valides sinon l'utilisateur est redirigé vers la page de nouvelle publication 
Puis on construit un objet post qui contient les informations nécessaires que l'on ajoute à la base de donnée
Si tout se passe bien un message de succès est affiché et l'utilisateur est redirigé vers la page d'accueil

"""
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Votre publication à bien été créé !', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='Nouvelle Publication')

"""
Routes permettant l'accès à la page d'une publication en particulière
Récupère la publication avec son id.
Si elle n'existe pas l'erreur 404(erreur serveur) est affiché à l'utilisateur
Dans le cas contraire les informations de la publication sont retournées à la page d'affichage de la publication en question
"""
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

"""
Routes permettant l'accès à la page de modification d'une publication.
Accessible uniquement par un utilisateur connecté
Dans un premier temps récupère la publication retourne erreur 404 si l'id ne correspond à aucune publication en base de donnée
Vérifie que l'auteur de la publication est bien l'utilisateur courant sinon erreur 403(accès interdit)
Vérifie que les informations transmisent dans le formulaire en POST sont valides
Si oui, elles sont ajoutées à la base de donnée, un message de succès est affiché et l'utilisateur est redirigé vers la page d'affichage de la publication
Dans le cas d'une requête GET les informations de la publication demandée sont retourné dans le formulaire de la page de modification de la publication
"""
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

"""
Routes permettant l'accès à la page de suppression d'une publication.
Accessible uniquement par un utilisateur connecté
Dans un premier temps récupère la publication retourne erreur 404 si l'id ne correspond à aucune publication en base de donnée
Vérifie que l'auteur de la publication est bien l'utilisateur courant sinon erreur 403(accès interdit)
Si oui, la publication est supprimé de la base de donnée, un message de succès est affiché et l'utilisateur est redirigé vers la page d'affichage de la publication
Puis l'utilisateur est redirigé à la page d'accueil
"""
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Votre publication à été supprimé!', 'success')
    return redirect(url_for('home'))

"""
Route permettant l'accès à la page contenant toutes les publications d'un utilisateur
Selon le nom d'utilisateur passé en paramètre, récupère le nom de l'utilisateur s'il existe et les publications qu'il a crée en les affichants par groupe de 5 sur une page
Redirige l'utilisateur vers la page des publications associées à l'utilisateur demandé 
"""
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

"""
Fontion permettant de reinitialiser le mots de passe d'un compte utilisateur
Dans un premier temps on vient récupérer un tokent de réinitialisation afin de garantir une sécurité (confidentialité et temporelle)
Ensuite le mail est envoyé selon les configurations du compte mail d'envoi initialisé dans le fichier __init__.py 
"""
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Pour changer votre mots de passe, cliquez sur ce lien:
{url_for('reset_token', token=token, _external=True)}
Si vous n'avez pas fait cette requête. Vous pouvez ignorer ce mail et aucun changement ne sera fait. 
'''
    mail.send(msg)

"""
Route permettant l'accès à la page de demande de modification de mots de passe
Dans un premier temps si l'utilisateur est connecté on le redirige vers la page d'accueil
On vérifie que les informations passées par le formulaire en post sont valides
Si oui, on récupère l'adresse mail de l'utilisateur en s'assurant qu'elle est bien présente dans la base de donnée
Puis l'on fait appel à la fonction de réinitialisation de mots de passe qui envoi un mail à l'utilisateur
Si tout se passe bien un message de succès est affiché
"""
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Un email vient d\'être envoyé avec les informations permettant le changement de mots de passe.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

"""
Route permettant l'accès à la page de modification de mots de passe
Dans un premier temps récupère le token passé, après que l'utilisateur est cliqué sur le lien présent dans son mail de modification de mots de passe
Si l'utilisateur est connecté on le redirige vers la page d'accueil
Puis dans l'objet user on vérifie que le token est bien associé à l'utilisateur et est encore valide et on le stocke 
On vérifie que l'objet user est non vide. Si oui, un message d'échec est affiché
On vérifie alors que les informations du formulaire passées en post sont valide 
Si oui, on hache et encrypte le nouveau mots de passe avant de l'enregistrer dans la base de donnée pour assuré une confidentialité
Un message de succès est affiché à l'utilisateur et il est redirigé vers la page de connection au site
"""
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Ce lien n\'est plus valide !', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Votre mots de passe à bien été changé! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)