-- Users table to store user information
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    profile_picture TEXT DEFAULT 'uploads/default_pp.png',
    password_hash TEXT NOT NULL,
    overall_score INTEGER DEFAULT 0,
    played INTEGER DEFAULT 0,
    solved INTEGER DEFAULT 0,
    playtime INTEGER DEFAULT 0,
    all_time_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Words table to store the list of possible solution words for the game
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL
);

-- Words table to store valid words the user can enter
CREATE TABLE IF NOT EXISTS guessables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guessable TEXT UNIQUE NOT NULL
);

-- Games table to store information about each game
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    profile_picture TEXT DEFAULT 'uploads/default_pp.png',
    datum DATE,
    status TEXT DEFAULT 'in_progress', -- FALSE = lost TRUE = won
    attempts INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    time_used INTEGER DEFAULT 0,
    FOREIGN KEY (datum) REFERENCES word_of_the_day(date_set),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (profile_picture) REFERENCES users(profile_picture)
);

-- Guesses table to store each guess made by the user in a game
CREATE TABLE IF NOT EXISTS guesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    guess TEXT NOT NULL,
    result TEXT NOT NULL, -- e.g., "ccicc" where 'c' is correct, 'i' is incorrect place, 'x' is incorrect
    guessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id)
);

CREATE TABLE IF NOT EXISTS word_of_the_day (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    date_set DATE NOT NULL
);

-- Trigger to update profile_picture in games table when a new game is inserted
CREATE TRIGGER IF NOT EXISTS update_profile_picture_on_insert
AFTER INSERT ON games
FOR EACH ROW
BEGIN
    UPDATE games
    SET profile_picture = (SELECT profile_picture FROM users WHERE users.id = NEW.user_id)
    WHERE id = NEW.id;
END;

-- Trigger to update profile_picture in games table when a user's profile_picture is updated
CREATE TRIGGER IF NOT EXISTS update_profile_picture_on_user_update
AFTER UPDATE OF profile_picture ON users
FOR EACH ROW
BEGIN
    UPDATE games
    SET profile_picture = NEW.profile_picture
    WHERE user_id = OLD.id;
END;
