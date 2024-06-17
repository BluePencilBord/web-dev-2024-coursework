from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Для выполнения данного действия необходимо пройти процедуру аутентификации", category="error")
                return redirect(url_for('auth.login'))
            if current_user.role.name not in roles:
                flash("У вас нет прав для доступа к этой странице", category="error")
                return redirect(url_for('views.home_page'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper