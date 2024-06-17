from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')

        user = db.session.scalars(db.select(User).where(User.login == login)).one_or_none()
        if user:
            if check_password_hash(user.password_hash, password):
                flash("Успешная авторизация", category="success")
                if remember_me is None:
                    login_user(user)
                else:
                    login_user(user, remember=True)
                return redirect(url_for('views.home_page'))
            else:
                flash("Невозможно авторизоваться с указанными логином и паролем", category="error")
        else:
            flash("Невозможно авторизоваться с указанными логином и паролем", category="error")

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home_page'))