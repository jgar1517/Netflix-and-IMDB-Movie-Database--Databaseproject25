import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3 
from Crud_components import create_watchlist 

DATABASE_FILE = "netflix_db.db"

# Helper function to get subjects for the dropdown 
def fetch_all_subjects():
    """
    Connects to the DB and fetches a clean list of all subject names
    to populate the parameter dropdown.
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT subject_name FROM Subjects ORDER BY subject_name ASC")
        # Convert list of tuples [('Action',), ('Comedy',)] to list ['Action', 'Comedy']
        subjects = [row[0] for row in c.fetchall()]
        conn.close()
        
        if not subjects:
            messagebox.showwarning("DB Warning", "Could not find any subjects in the 'Subjects' table. Make sure populatedb.py has been run.")
            return ["No subjects found"]
            
        return subjects
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not fetch subjects: {e}\n\nMake sure your database '{DATABASE_FILE}' exists and is populated.")
        return ["DB Error"]


def add_watchlist():
    list_name = entry_list.get() 
    teacher_name = entry_teacher.get()
    
    if list_name and teacher_name:
        create_watchlist(list_name, teacher_name) # Calls your Crud_components function
        messagebox.showinfo("Success", "Watchlist added successfully.")
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END)
    else:
        messagebox.showwarning("Error", "Please fill in all fields.")

# show/hide the correct parameter boxes 
def on_query_select(event):
    """
    Called when the user changes the query dropdown.
    Hides all parameter frames, then shows the correct one.
    """
    # Hide all parameter frames
    param_frame_q1.pack_forget()
    param_frame_q2.pack_forget()
    param_frame_q3.pack_forget()
    param_frame_q4.pack_forget()
    
    selected_query = query_combo.get()
    
    
    if selected_query == "Query 1: Find by Academic Keyword (in Description)":
        param_frame_q3.pack(pady=5)  # 
        
    elif selected_query == "Query 2: Find by Genre (Top-Rated)":
        param_frame_q1.pack(pady=5)  # 
        
    elif selected_query == "Query 3: Find Films by Age Rating & Duration":
        param_frame_q2.pack(pady=5)  

    elif selected_query == "Query 4: Find Average Rating Per Year":
        param_frame_q4.pack(pady=5)  


# run the selected query
def run_selected_query():
    selected_option = query_combo.get()
    results_text.delete('1.0', tk.END)
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        results_text.insert(tk.END, f"--- Running: {selected_option} ---\n")
        
        query = ""
        params = ()

        # --- QUERY 1 ---
        if selected_option == "Query 1: Find by Academic Keyword (in Description)":
            keyword = param3_keyword_entry.get()
            rating = param3_rating_entry.get()
            
            if not keyword or not rating:
                messagebox.showwarning("Input Error", "Please enter a Keyword and a Min Rating.")
                conn.close()
                return
                
            try:
                
                keyword_param = f'%{keyword}%'
                params = (keyword_param, keyword_param, float(rating))
                
                
                query = """
                    SELECT title, averageRating, type, description
                    FROM Netflix_IMDB
                    WHERE 
                        (title LIKE ? OR description LIKE ?)
                        AND CAST(averageRating AS REAL) >= ?
                    ORDER BY 
                        CAST(averageRating AS REAL) DESC
                    LIMIT 20;
                """
            except ValueError:
                messagebox.showwarning("Input Error", "Minimum Rating must be a number (e.g., 7.0).")
                conn.close()
                return

        # --- QUERY 2 ---
        elif selected_option == "Query 2: Find by Genre (Top-Rated)":
            subject = param1_combo.get()
            rating = param1_rating_entry.get()
            
            if not subject or not rating:
                messagebox.showwarning("Input Error", "Please select a Subject and enter a Min Rating.")
                conn.close()
                return
            
            try:
                
                subject_param = f'%{subject}%'
                params = (subject_param, float(rating))
                
                
                query = """
                    SELECT title, type, averageRating, release_year
                    FROM Netflix_IMDB
                    WHERE 
                        listed_in LIKE ?
                        AND CAST(averageRating AS REAL) >= ?
                    ORDER BY 
                        CAST(averageRating AS REAL) DESC
                    LIMIT 20;
                """
            except ValueError:
                messagebox.showwarning("Input Error", "Minimum Rating must be a number (e.g., 7.5).")
                conn.close()
                return

        # --- QUERY 3 ---
        elif selected_option == "Query 3: Find Films by Age Rating & Duration":
            age_rating = param2_age_entry.get()
            duration = param2_duration_entry.get()

            if not age_rating or not duration:
                messagebox.showwarning("Input Error", "Please enter an Age Rating and a Max Duration.")
                conn.close()
                return
                
            try:
                params = (age_rating, int(duration))
                
                
                query = """
                    SELECT title, rating, duration, averageRating, description
                    FROM Netflix_IMDB
                    WHERE 
                        type = 'Movie' 
                        AND rating = ?
                        AND CAST(REPLACE(duration, ' min', '') AS INTEGER) <= ?
                    ORDER BY 
                        CAST(averageRating AS REAL) DESC
                    LIMIT 20;
                """
            except ValueError:
                messagebox.showwarning("Input Error", "Max Duration must be a number (e.g., 50).")
                conn.close()
                return
            
        # --- QUERY 4 ---
        elif selected_option == "Query 4: Find Average Rating Per Year":
                
                query = """
                    SELECT 
                        n.release_year, 
                        ROUND(AVG(n.averageRating), 2) AS avg_rating,
                        COUNT(*) AS title_count
                    FROM Netflix_IMDB AS n
                    WHERE n.averageRating IS NOT NULL
                    GROUP BY n.release_year
                    ORDER BY n.release_year DESC;
                """
            
        # --- QUERY 5 ---
        elif selected_option == "Query 5: Find Best Movies Per Year":

            query = """
                WITH RankedMovies AS (
                    SELECT 
                        title, 
                        release_year, 
                        averageRating, 
                        numVotes,
                        genres,
                        ROW_NUMBER() OVER(
                            PARTITION BY release_year 
                            ORDER BY averageRating DESC, numVotes DESC
                        ) AS rank
                    FROM Netflix_IMDB
                    WHERE 
                        type = 'Movie' 
                        AND averageRating IS NOT NULL
                        AND numVotes >= 1000 -- Parameter for min votes
                )
                SELECT 
                    release_year, 
                    title,
                    averageRating, 
                    numVotes,
                    genres
                FROM RankedMovies
                WHERE rank = 1
                ORDER BY release_year DESC;
                """

        # --- NO QUERY SELECTED ---
        else:
            messagebox.showwarning("Warning", "Please select a valid query.")
            conn.close()
            return

        # --- Execute the chosen query ---
        c.execute(query, params)
        results = c.fetchall()
        
        if results:
            col_names = [description[0] for description in c.description]
            results_text.insert(tk.END, f"{col_names}\n")
            results_text.insert(tk.END, "-"*60 + "\n")

            # formats the results with newlines 
            for row in results:
                # This will be our new, multi-line string
                formatted_string = ""
                
                if selected_option == "Query 1: Find by Academic Keyword (in Description)":
                    # row = (title, averageRating, type, description)
                    title, rating, type, desc = row
                    
                    # Add \n to put description on its own line
                    formatted_string = f"Title: {title} ({type}, IMDB: {rating})\n"
                    formatted_string += f"  Desc: {desc[:150]}...\n\n" # Truncate desc
                    
                elif selected_option == "Query 2: Find by Genre (Top-Rated)":
                    # row = (title, type, averageRating, release_year)
                    title, type, rating, year = row
                    formatted_string = f"Title: {title} ({type}, {year}) - IMDB: {rating}\n\n"
                    
                elif selected_option == "Query 3: Find Films by Age Rating & Duration":
                    # row = (title, rating, duration, averageRating, description)
                    title, age_rating, dur, imdb_rating, desc = row
                    
                    # Add \n to put description on its own line
                    formatted_string = f"Title: {title} (Age: {age_rating}, {dur}, IMDB: {imdb_rating})\n"
                    formatted_string += f"  Desc: {desc[:150]}...\n\n" 
                
                else: 
                    formatted_string = f"{row}\n\n"

                
                results_text.insert(tk.END, formatted_string)

        else:
            
            results_text.insert(tk.END, "No results found for these parameters.")
            
        conn.close()
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

# --- Main Application Setup ---

# Fetch the list of subjects *before* creating the main window
all_subjects_list = fetch_all_subjects()

root = tk.Tk()
root.title("Netflix Educational Content Finder")
root.geometry("500x800") 

#Add Watchlist
add_frame = ttk.Frame(root, padding="10")
add_frame.pack(fill='x')

tk.Label(add_frame, text="List Name:").pack(pady=5)
entry_list = tk.Entry(add_frame, width=40)
entry_list.pack(pady=5)

tk.Label(add_frame, text="Teacher Name:").pack(pady=5)
entry_teacher = tk.Entry(add_frame, width=40)
entry_teacher.pack(pady=5)

tk.Button(add_frame, text="Add Watchlist", command=add_watchlist).pack(pady=10)

#Separator 
ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)

#'Run Query'
query_frame = ttk.Frame(root, padding="10")
query_frame.pack(fill='x')

tk.Label(query_frame, text="Select a Database Query:").pack(pady=5)

# Main Query Dropdown 
query_options = [
    "Query 1: Find by Academic Keyword (in Description)",
    "Query 2: Find by Genre (Top-Rated)",
    "Query 3: Find Films by Age Rating & Duration",
    "Query 4: Find Average Rating Per Year",
    "Query 5: Find Best Movies Per Year"
]
query_combo = ttk.Combobox(query_frame, values=query_options, width=45, state="readonly")
query_combo.pack(pady=5)
query_combo.current(0) # Default to our new Query 1
# Bind the selection event to our function
query_combo.bind("<<ComboboxSelected>>", on_query_select)

# Parameter Frames

#Parameters for Query 1 
param_frame_q1 = ttk.Frame(query_frame)
# Subject/Genre
tk.Label(param_frame_q1, text="Genre:").grid(row=0, column=0, padx=5, sticky="e")
param1_combo = ttk.Combobox(param_frame_q1, values=all_subjects_list, width=25, state="readonly")
param1_combo.grid(row=0, column=1, padx=5)
param1_combo.set("Documentaries") # Set a default
# Min Rating
tk.Label(param_frame_q1, text="Min IMDB Rating:").grid(row=1, column=0, padx=5, sticky="e")
param1_rating_entry = tk.Entry(param_frame_q1, width=28)
param1_rating_entry.grid(row=1, column=1, padx=5)
param1_rating_entry.insert(0, "7.5")

# Parameters for Query 2 
param_frame_q2 = ttk.Frame(query_frame)
# Age Rating
tk.Label(param_frame_q2, text="Age Rating:").grid(row=0, column=0, padx=5, sticky="e")
param2_age_entry = tk.Entry(param_frame_q2, width=28)
param2_age_entry.grid(row=0, column=1, padx=5)
param2_age_entry.insert(0, "PG-13")
# Max Duration
tk.Label(param_frame_q2, text="Max Duration (min):").grid(row=1, column=0, padx=5, sticky="e")
param2_duration_entry = tk.Entry(param_frame_q2, width=28)
param2_duration_entry.grid(row=1, column=1, padx=5)
param2_duration_entry.insert(0, "50")

# Parameters for Query 3 
param_frame_q3 = ttk.Frame(query_frame)
# Keyword
tk.Label(param_frame_q3, text="Academic Keyword:").grid(row=0, column=0, padx=5, sticky="e")
param3_keyword_entry = tk.Entry(param_frame_q3, width=28)
param3_keyword_entry.grid(row=0, column=1, padx=5)
param3_keyword_entry.insert(0, "Shakespeare")
# Min Rating
tk.Label(param_frame_q3, text="Min IMDB Rating:").grid(row=1, column=0, padx=5, sticky="e")
param3_rating_entry = tk.Entry(param_frame_q3, width=28)
param3_rating_entry.grid(row=1, column=1, padx=5)
param3_rating_entry.insert(0, "7.0")

# Parameters for Query 4
param_frame_q4 = ttk.Frame(query_frame)
tk.Label(param_frame_q4, text="This query takes no parameters.").pack(pady=10)

# Parameters for Query 5
param_frame_q5 = ttk.Frame(query_frame)
tk.Label(param_frame_q5, text="Finds the top movie per year (min 1000 votes).").pack(pady=10)

# --- Run Button ---
tk.Button(query_frame, text="Run Selected Query", command=run_selected_query).pack(pady=10)

# --- Results Text Box ---
results_text = tk.Text(root, height=15, width=60)
results_text.pack(pady=10, padx=10)

# --- Final setup ---
# Manually call this once to show the default parameter frame (for our new Query 1)
on_query_select(None)

# Start the GUI
root.mainloop()