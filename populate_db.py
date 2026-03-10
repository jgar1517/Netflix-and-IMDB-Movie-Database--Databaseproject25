import sqlite3
import csv

DATABASE_FILE = "netflix_db.db"

CSV_FILE = "netflix_titles.csv"

def populate_tables():

    subject_cache = {}
    
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        with open(CSV_FILE, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    #attempt to populate titles table
                    cursor.execute("""
                        INSERT INTO Titles (
                                show_id, type, title, release_year, rating,
                                duration, description, date_added, director, cast, country)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row["show_id"], row['type'], row['title'],
                        row['release_year'], row['rating'], row['duration'], 
                        row['description'], row['date_added'], row['director'], 
                        row['cast'], row['country']
                    ))

                    # string that will hold the subject
                    subjects_string = row['listed_in']

                    # splitting it into a list
                    subject_list = [s.strip() for s in subjects_string.split(',')]

                    for subject_name in subject_list:
                        if not subject_name:
                            continue

                        subject_id = None

                        # cahceing used to speed up the process
                        if subject_name in subject_cache:
                            subject_id = subject_cache[subject_name]
                        else:
                            #IF not found in the cache add to subject table
                            try:
                                cursor.execute("INSERT INTO Subjects (subject_name) VALUES (?)",
                                                (subject_name,))
                                
                                # grabs the new subject id that was just crated
                                subject_id = cursor.lastrowid

                                # add it to cache
                                subject_cache[subject_name] = subject_id
                            except sqlite3.IntegrityError:
                                # if subject is already in the table fetch the ID
                                cursor.execute("SELECT subject_id FROM Subjects WHERE subject_name = ?",
                                                (subject_name,))
                                subject_id = cursor.fetchone()[0]
                                subject_cache[subject_name] = subject_id

                            if subject_id:
                                cursor.execute("INSERT INTO Title_Subjects (show_id, subject_id) VALUES (?, ?)",
                                                (row['show_id'], subject_id))
                except sqlite3.IntegrityError as e:
                    print(f"Skipping duplicate row:{row['show_id']}: {e}")
                except Exception as e:
                    print(f"Error processing row {row['show_id']}: {e}")
            
            conn.commit()
        print(f"Successfully updated '{DATABASE_FILE}'")
    except sqlite3.Error as e:
        print(f"Error has occured: {e}")
    except FileNotFoundError:
        print(f"CSV file '{CSV_FILE}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            

if __name__ == "__main__":
    populate_tables()
                            
                                



