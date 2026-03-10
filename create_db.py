import sqlite3

DATABASE_FILE = "netflix_db.db"

SQL_CREATE_TABLE = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Titles (
    show_id VARCHAR(10) PRIMARY KEY,
    type VARCHAR(10),
    title VARCHAR(255) NOT NULL,
    release_year INTEGER,
    RATING VARCHAR(10),
    duration VARCHAR(20),
    description TEXT,
    date_added DATE,
    director TEXT,
    cast TEXT,
    country TEXT
);

CREATE TABLE IF NOT EXISTS Subjects (
    subject_id INTEGER PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Title_Subjects (
    show_id VARCHAR(10) NOT NULL,
    subject_id INTEGER NOT NULL,
    PRIMARY KEY (show_id, subject_id),
    FOREIGN KEY (show_id) REFERENCES Titles(show_id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
);

CREATE TABLE IF NOT EXISTS Watchlists (
    list_id INTEGER PRIMARY KEY,
    list_name VARCHAR(100) NOT NULL UNIQUE,
    teacher_name VARCHAR(100) NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Watchlist_Items (
    list_id INTEGER NOT NULL,
    show_id VARCHAR(10) NOT NULL,
    PRIMARY KEY (list_id, show_id),
    FOREIGN KEY (list_id) REFERENCES Watchlist(list_id),
    FOREIGN KEY (show_id) REFERENCES Titles(show_id)
);
"""
def create_database():
    conn = None
    try:#connect to db
        conn = sqlite3.connect(DATABASE_FILE)
        #cursor object runs sql commands
        cursor = conn.cursor()
        #execute big sql string
        cursor.executescript(SQL_CREATE_TABLE)
        #commit the changes to the db file
        conn.commit()
        print(f"Successfully updated '{DATABASE_FILE}'")
    except sqlite3.Error as e:
        print(f"Error has occured: {e}")
        
    finally:
        if conn:
            conn.close()
            

if __name__ == "__main__":
    create_database()
    
