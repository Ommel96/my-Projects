from wordL.db import get_db
from datetime import date
from flask import (
    Blueprint, render_template, request
)

bp = Blueprint('scoreboard', __name__)

@bp.route('/scoreboard', methods=('GET', 'POST'))
def get_scores():
    db = get_db()
    scores = []
    choice = 'daily'
    today = date.today()
    
    scores = db.execute('SELECT username, attempts, score, time_used, profile_picture FROM games WHERE datum = ?'
        'ORDER BY score DESC',
        (today,)).fetchall()

    if request.method == 'POST':

        if request.form['choice'] == 'oat':
            scores = db.execute("SELECT username, solved, overall_score, profile_picture FROM users "
                                "ORDER BY overall_score DESC").fetchall()
            choice = 'oat'
        
        else:
            scores = db.execute('SELECT username, attempts, score, time_used, profile_picture FROM games WHERE datum = ?'
                    'ORDER BY score DESC',
                    (today,)).fetchall()
            choice = 'daily'
        
   
    return render_template('main/scoreboard.html', scores=scores, choice=choice)
