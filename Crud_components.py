import sqlite3

DATABASE_FILE = "netflix_db.db"

#================================#
# CRUD operations for Watchlists #
#================================#

def create_watchlist(list_name, teacher_name): # create
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Watchlists (list_name, teacher_name) VALUES (?, ?)",
                       (list_name, teacher_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error has occured: {e}")
    finally:
        if conn:
            conn.close()
            
def read_all_watchlist(): # read
    #prints the watchlist
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Watchlists")
        watchlists = cursor.fetchall()
        return watchlists # return the fetched watchlists
    
    except sqlite3.Error as e:
        print(f"Error has occured: {e}")
        return [] # return empty list on error
    finally:
        if conn:
            conn.close()
            
def delete_watchlist(watchlist_id): # deletes a watchlist by ID
    # connect to the database
    conn = None 
    try:
        conn = sqlite3.connect(DATABASE_FILE) 
        cursor = conn.cursor()

        # get name before deleting
        cursor.execute("SELECT list_name FROM Watchlists WHERE list_id = ?", (watchlist_id,))
        result = cursor.fetchone()
        if not result:
            return False, None  # no record found
        
        list_name = result[0] # extract list name

        # execute the delete statement
        cursor.execute("DELETE FROM Watchlists WHERE list_id = ?", (watchlist_id,)) # delete watchlist
        cursor.execute("DELETE FROM Watchlist_Items WHERE list_id = ?", (watchlist_id,)) # also delete associated items
        conn.commit()

        # check if any row was deleted
        return True, list_name  # success

    except sqlite3.Error as e:
        print(f"Error has occurred: {e}")
    finally:
        if conn:
            conn.close()

def update_watchlist(list_id, new_list_name, new_teacher_name): # updates a watchlist's name and teacher
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Watchlists SET list_name = ?, teacher_name = ? WHERE list_id= ?",
            (new_list_name, new_teacher_name, list_id),
        )
        conn.commit()
        return cursor.rowcount  # number of rows updated
    except sqlite3.Error as e:
        print(f"Error has occurred: {e}")
        return 0
    finally:
        if conn:
            conn.close()

#===========================================================================#
#                  CRUD operations for Watchlist Items                      #                
# note: there is no real way to update watchlist items as they store titles #
# in a many-to-many relationship. You can only add or remove titles.        #
#===========================================================================#

def add_title_to_watchlist(list_id, show_id): # add title to watchlist by show id
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Ensure both exist
        cursor.execute("SELECT 1 FROM Watchlists WHERE list_id = ?", (list_id,))
        if not cursor.fetchone():
            print(f"No watchlist found with id {list_id}")
            return False, "Watchlist not found."

        cursor.execute("SELECT 1 FROM Titles WHERE show_id = ?", (show_id,))
        if not cursor.fetchone():
            print(f"No title found with show_id {show_id}")
            return False, "Title not found."

        # Check for duplicates
        cursor.execute(
            "SELECT 1 FROM Watchlist_Items WHERE list_id = ? AND show_id = ?",
            (list_id, show_id),
        )
        if cursor.fetchone():
            print("Title already exists in this watchlist.")
            return False, "Title already in watchlist."

        cursor.execute(
            "INSERT INTO Watchlist_Items (list_id, show_id) VALUES (?, ?)",
            (list_id, show_id),
        )
        conn.commit()
        print(f"Added title {show_id} to watchlist {list_id}.")
        return True, "Title added successfully."

    except sqlite3.Error as e:
        print(f"Error adding title to watchlist: {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def get_titles_for_watchlist(list_id): # get all titles for a given watchlist
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT T.show_id, T.title, T.type, T.release_year, T.rating
            FROM Watchlist_Items WI
            JOIN Titles T ON WI.show_id = T.show_id
            WHERE WI.list_id = ?
        """, (list_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving titles: {e}")
        return []
    finally:
        if conn:
            conn.close()

def remove_title_from_watchlist(list_id, show_id): # remove a title from a watchlist
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Watchlist_Items WHERE list_id = ? AND show_id = ?",
            (list_id, show_id),
        )
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Removed title {show_id} from watchlist {list_id}.")
            return True
        else:
            print(f"No match found for list_id={list_id}, show_id={show_id}.")
            return False
    except sqlite3.Error as e:
        print(f"Error removing title from watchlist: {e}")
        return False
    finally:
        if conn:
            conn.close()

#==============================================================================#
# Retrieve titles from Titles table and watchlists containing a specific title #
#==============================================================================#

def get_all_titles(): # get all titles from Titles table
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT show_id, title, type, release_year, RATING, duration, description, date_added, director, [cast], country
            FROM Titles
            ORDER BY release_year DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving all titles: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_watchlists_for_title(show_id): # get all watchlists containing a specific title
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT W.list_id, W.list_name, W.teacher_name
            FROM Watchlist_Items WI
            JOIN Watchlists W ON WI.list_id = W.list_id
            WHERE WI.show_id = ?
        """, (show_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving watchlists for title: {e}")
        return []
    finally:
        if conn:
            conn.close()

#==========================================================================================#
# simple demo of CRUD operations, will not show unless the crud_components.py file is ran. #
#==========================================================================================#

if __name__ == "__main__":
    
    print("--- (R)EAD: First, reading all watchlists . ---")
    read_all_watchlist()
    
    print("\n--- (C)REATE: Now, creating two new watchlists. ---")
    create_watchlist("Geology 101", "Mr. Smith")
    create_watchlist("History of Film", "Ms. Davis")
    
    print("\n--- (R)EAD: Finally, reading all watchlists again. ---")
    read_all_watchlist()
    
    print("\n--- END OF DEMO ---")