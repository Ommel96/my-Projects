from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session)
import time
from datetime import date
from wordL.db import get_db, seeding

bp = Blueprint('wordle', __name__)


def get_word_of_the_day():

    # Picks a new word from the database if there is none for the day

    db = get_db()
    today = date.today().isoformat()

    word_of_the_day = db.execute(
        'SELECT word FROM word_of_the_day WHERE date_set = ?', (today,)
    ).fetchone()

    if word_of_the_day is None:
        session.clear()
        session_setup()
        new_word = db.execute(
            'SELECT word FROM words ORDER BY RANDOM() LIMIT 1'
        ).fetchone()['word']

        db.execute(
            'INSERT INTO word_of_the_day (word, date_set) VALUES (?, ?)',
            (new_word, today)
        )
        db.commit()
        word_of_the_day = new_word

    else:
        word_of_the_day = word_of_the_day['word']

    return word_of_the_day

def comparing(wordle, guess):

    # Compares each single letter in the users guess with the word of the day
    comparison = []
    for i, char in enumerate(guess):
        if char == wordle[i]:
            comparison.append((char, 'correct'))  # Correct position
        elif char in wordle:
            comparison.append((char, 'wrong_position'))  # Incorrect position
        else:
            comparison.append((char, 'incorrect'))  # Not in the word
    return comparison

def score_calculation(attempts, won, letters_guessed, letters_guessed_correctly, time_used):
    score = 0
    score += (6 - attempts) * 100

    if time_used < 300 and won:
        score += 300 - time_used
    elif time_used < 150:
        score += 150 - time_used

    if won:
        score += 150
    else:
        score += letters_guessed * 5
        score += letters_guessed_correctly * 10

    return round(score)

def append_score(db, username, guesses):

    # Ensures a user cannot generate more than one score per day by deleting cookies
    if db.execute('SELECT * FROM games WHERE username = ? AND datum = ?', (username, date.today().isoformat())).fetchone() == None:
        
        if session.get('game_over', False):
            db.execute(
                'INSERT INTO games (user_id, username, datum, status, attempts, score, time_used) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (session.get('user_id'), username, date.today().isoformat(), session.get('game_won', 0), len(guesses), session.get('score', 0), session.get('time_used', 0))
            )
            db.execute(
                'UPDATE users SET overall_score = overall_score + ?,'
                'played = played + 1,'
                'playtime = playtime + ?,'
                'all_time_attempts = all_time_attempts + ?'
                'WHERE id = ?',
                (session.get('score'),
                 session.get('time_used'),
                 len(session.get('guesses', 0)),
                 session.get('user_id')
                 )
            )
            if session.get('game_won'):
                db.execute(
                    'UPDATE users SET solved = solved + 1 WHERE id = ?',
                    (session.get('user_id'),)
                )
            db.commit()

def session_setup():
    keys = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Creating session variables
    session.setdefault('start_time', None)
    session.setdefault('time_used', 0)
    session.setdefault('guesses', [])
    session.setdefault('game_over', False)
    session.setdefault('letter_status', {letter: 'unknown' for letter in keys})
    session.setdefault('game_won', False)
    session.setdefault('letters_guessed', [])
    session.setdefault('letters_guessed_correctly', [])
    session.setdefault('score', 0)
    session.setdefault('score_appended', False)
    session.setdefault('last_played_on', None)
    session.setdefault('game_started', False)

def evaluate_guess(db, guess):
    wordle = get_word_of_the_day()
    guesses = session['guesses']
    error = None

    if not guess or len(guess) != 5:
        error = "Enter a valid 5 letter word."
    elif any(g[0] == guess for g in guesses):
        error = "You already guessed that word."
    else:
        # Checks list of guessable words so the user doesn't input made up words
        correct = db.execute('SELECT * FROM guessables WHERE guessable = ?', (guess,)).fetchone()
        if not correct:
            error = "Invalid word! Enter a valid 5 letter word."

    if error:
        flash(error)
        return None
    else:
        comparison_result = comparing(wordle, guess)
        guesses.append((guess, comparison_result))
        session['guesses'] = guesses
        session.modified = True

        return comparison_result

def update_letter_status(comparison_result):
    letter_status = session['letter_status']
    letters_guessed = session['letters_guessed']
    letters_guessed_correctly = session['letters_guessed_correctly']

    # Track the letters used in the guess
    for char, status in comparison_result:
        # Save letters used to show the user which letters haven't been used yet and which of them were (semi)correct
        if letter_status[char.upper()] != 'correct':
            letter_status[char.upper()] = status
        # Save letters guessed that were (semi-)correct for score calculation
        if status == 'correct' and char.upper() not in letters_guessed_correctly:
            letters_guessed_correctly.append(char.upper())
        elif status == 'wrong_position' and char.upper() not in letters_guessed:
            letters_guessed.append(char.upper())

    session['letter_status'] = letter_status
    session['letters_guessed'] = letters_guessed
    session['letters_guessed_correctly'] = letters_guessed_correctly
    session.modified = True

def daily_reset():

    # pops relevant session variables to ensure a proper new game
    session.pop('start_time')
    session.pop('time_used')
    session.pop('guesses')
    session.pop('game_over')
    session.pop('letter_status')
    session.pop('game_won')
    session.pop('letters_guessed')
    session.pop('letters_guessed_correctly')
    session.pop('score')
    session.pop('score_appended')
    session.pop('game_started')
    session_setup()
    session['last_played_on'] = date.today().isoformat()

@bp.route('/', methods=('GET', 'POST'))
def wordlepage():

    # Debugging: Creates and seeds a DB if there is none
    seeding()

    db = get_db()
    session_setup()

    # Resets most of the session variables if user did not play the daily word yet
    if session['last_played_on'] != date.today().isoformat():
     
        daily_reset()

    # Appends the score if the user logged in after finishing the game
    if session.get('user_id') and session['game_over'] and session['score_appended'] == False:
        username_row = db.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        username = username_row['username']
        append_score(db, username, session['guesses'])
        session['score_appended'] = True

    # The Game
    if request.method == 'POST':

        if 'Start!' in request.form:
            session['game_started'] = True
            session.modified = True
            start_timer()

        # for Debugging
        if 'reset' in request.form:
            session.clear()
            session_setup()
            db.execute('DELETE FROM word_of_the_day WHERE date_set = ?', (date.today().isoformat(),))
            db.commit()
            return redirect(url_for('wordle.wordlepage'))

        # Game Logic
        guess = request.form['guess'].lower().strip()
        comparison_result = evaluate_guess(db, guess)

        if comparison_result:
            update_letter_status(comparison_result)

            # Check win condition
            if all(char[1] == 'correct' for char in comparison_result):
                flash("Congratulations! You guessed the word correctly!")
                if not session.get('game_over'):
                    session['time_used'] = round((time.time() - session['start_time']))
                session['game_over'] = True
                session['game_won'] = True

            #Check lose condition
            elif len(session['guesses']) >= 6:
                flash("Sorry, you've run out of guesses.")

                if not session.get('game_over'):
                    session['time_used'] = round((time.time() - session['start_time']))
                session['game_over'] = True
                session['game_won'] = False

            # Calculating the score
            session['score'] = score_calculation(
                len(session['guesses']), session['game_won'], 
                len(session['letters_guessed']), len(session['letters_guessed_correctly']), session['time_used']
            )
            session.modified = True

            #Appends the score if the user was logged in during the game
            if session.get('user_id') and session['game_over']:
                username_row = db.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
                username = username_row['username']
                append_score(db, username, session['guesses'])
                session['score_appended'] = True

    return render_template('main/start.html', 
                           wordle=get_word_of_the_day(), 
                           keys="ABCDEFGHIJKLMNOPQRSTUVWXYZ", 
                           letter_status=session['letter_status'],
                           attempts=len(session.get('guesses', 0)),
                           guesses=session.get('guesses', 0),
                           game_over=session.get('game_over', 0),
                           score=session.get('score', 0),
                           time_used=session.get('time_used', 0),
                           logged_in_user=session.get('user_id'),
                           game_started = session.get('game_started', 0))

@bp.route('/start_timer', methods=['POST'])
def start_timer():
    session['start_time'] = time.time()
    session.modified = True
    return '', 204
