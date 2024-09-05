import sqlite3
import click
from flask import current_app, g, url_for, redirect
from pathlib import Path
import json

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def seeding():
    
    base_path = Path(__file__).resolve().parent.parent
    db_file = base_path / "instance" / "wordL.sqlite"
    
    if not db_file.exists():
        print("Database file does not exist. Initializing database.")
        init_db()
        db = get_db()

        words_json_path = base_path / "wordL" / "resources" / "words.json"
        shuffled_words_path = base_path / "wordL" / "resources" / "shuffled_real_wordles.txt"
        
        if not words_json_path.exists():
            print(f"Error: Words JSON file does not exist at {words_json_path}")
            return
        if not shuffled_words_path.exists():
            print(f"Error: Shuffled words file does not exist at {shuffled_words_path}")
            return

        with open(words_json_path) as f:
            guessables = json.load(f)
        db.execute("BEGIN TRANSACTION")
        db.executemany("INSERT INTO guessables (guessable) VALUES (?)", [(guessable,) for guessable in guessables])
        db.commit()

        with open(shuffled_words_path, 'r') as f:
            words = [line.strip() for line in f]
        db.execute("BEGIN TRANSACTION")
        db.executemany("INSERT INTO words (word) VALUES (?)", [(word,) for word in words])
        db.commit()

        return redirect(url_for('wordle.wordlepage'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
