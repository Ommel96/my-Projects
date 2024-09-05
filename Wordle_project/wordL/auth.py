import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from wordL.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Function to register a new account
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        # Checks if all credentials are entered
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'E-Mail is required.'
        elif not password:
            error = 'Password is required.'

        # If all credentials are entered, a new account will be created
        # unless there is already an account using either the same email or username
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError as e:
                error_message = str(e)
                if 'username' in error_message:
                    error = f"Username {username} already exists."
                elif 'email' in error_message:
                    error = "E-Mail address already in use."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template('auth/register.html')


# Function to log in with an existing account
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect credentials or account does not exist."
        elif not check_password_hash(user['password_hash'], password):
            error = "Incorrect credentials or account does not exist."

        if error is None:
            session['user_id'] = user['id']
            session['profile_picture'] = user['profile_picture']
            return redirect(url_for('wordle.wordlepage'))
        
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('wordle.wordlepage'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view
