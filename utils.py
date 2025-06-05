from functools import wraps
from flask import session, redirect, url_for, flash
from models.models import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.profile'))
        return f(*args, **kwargs)
    return decorated_function
