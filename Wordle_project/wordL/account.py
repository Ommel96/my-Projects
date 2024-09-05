import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from wordL.db import get_db
from wordL.auth import login_required

bp = Blueprint('account', __name__, url_prefix='/account')

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = "profile_picture_user_id_" + str(session.get('user_id')) +".png"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Use forward slashes for URL paths
            relative_file_path = f'uploads/{filename}'

            db = get_db()
            db.execute(
                'UPDATE users SET profile_picture = ? WHERE id = ?',
                (relative_file_path, g.user['id'])
            )
            db.commit()
            session['profile_picture'] = relative_file_path
            return redirect(url_for('account.profile'))
    return render_template('account/upload.html')

def get_stats():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()

    username = user['username']
    email = user['email']
    solved = user['solved']
    played= user['played']
    overall_score= user['overall_score']
    playtime = user['playtime']
    all_time_attempts = user['all_time_attempts']
    member_since= user['created_at']
    if user['played'] != 0:
        solve_rate= f"{solved / played * 100}%"
        avg_score= overall_score / played
        avg_attempts= all_time_attempts / played
        avg_time= playtime / played
    else:
        solve_rate= 0
        avg_score= 0
        avg_attempts= 0
        avg_time= 0

    return(username, email, played, solved, overall_score, playtime, solve_rate, avg_attempts, avg_score, avg_time, member_since)

def get_user():

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()

    username = user['username']
    email = user['email']
    return(username,email)

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    username, email, played, solved, overall_score, playtime, solve_rate, avg_attempts, avg_score, avg_time, member_since = get_stats()

    return render_template('account/profile.html', user=g.user, username=username, email=email, 
                           played=played, solved=solved, overall_score=overall_score, playtime=playtime, 
                           solve_rate=solve_rate, avg_attempts=avg_attempts, avg_score=avg_score, avg_time=avg_time, member_since=member_since)



@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    username, email = get_user()
    db = get_db()
    error = None
    success_message = None 

    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if request.method == 'POST':
        if 'file' in request.form:
            upload()
        elif 'username_submit' in request.form:
            new_username = request.form['username']
            if db.execute('SELECT * from users WHERE username = ?', (new_username,)).fetchone() is None:
                db.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, session.get('user_id')))
                db.commit()
                success_message = "Username successfully changed."
            else:
                error = "Username is already in use."
        
        elif 'email_submit' in request.form:
            new_email = request.form['email']
            if db.execute('SELECT * from users WHERE email = ?' , (new_email,)).fetchone() is None:
                db.execute('UPDATE users SET email = ? WHERE id = ?' , (new_email, session.get('user_id')))
                db.commit()
                success_message = "E-mail address successfully changed."
            else:
                error = "E-mail address is already in use."

        elif 'password_submit' in request.form:
            if not check_password_hash(user['password_hash'], request.form['password']):
                error = "Incorrect password"
            elif request.form['new_password'] != request.form['confirm_password']:
                error = "Password confirmation is not the same as the new password"
            else:
                new_password = request.form['new_password']
                db.execute('UPDATE users SET password_hash = ? WHERE id = ?' , (generate_password_hash(new_password), session.get('user_id')))
                db.commit()
                success_message = "Password successfully changed."

        username, email = get_user()
        if error:
            flash(error)
        if success_message:
            flash(success_message)

    return render_template('account/edit.html', username=username, email=email)

