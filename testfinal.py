import tkinter as tk
import sqlite3
from tkinter import ttk
import os
from tkinter import messagebox
from Crud_components import create_watchlist, read_all_watchlist, delete_watchlist, update_watchlist, add_title_to_watchlist, get_titles_for_watchlist, get_all_titles, get_watchlists_for_title, remove_title_from_watchlist

DATABASE_FILE = "netflix_db.db"

#=========================#
# crud for watchlists GUI #
#=========================#

def add_watchlist():
    selected_item = tree.selection()
    if selected_item:
        messagebox.showwarning(
            "Error",
            "You have an existing watchlist selected. "
            "Use 'Update Selected Watchlist' to change it, or deselect first to create a new one."
        )
        return    
    
    list_name = entry_list.get()
    teacher_name = entry_teacher.get() 
    
    if list_name and teacher_name:
        create_watchlist(list_name, teacher_name)
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END) 
        print_watchlists()
        messagebox.showinfo("Success", f"Watchlist '{list_name}' added.")
    else:
        messagebox.showwarning("Error", "Please fill in all fields.")

def print_watchlists():
    for item in tree.get_children():
        tree.delete(item)

    watchlists = read_all_watchlist()
    for wlValues in watchlists:
        tree.insert('', 'end', values=(wlValues[0],wlValues[1], wlValues[2], wlValues[3]))

def delete_selected():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Error", "Please select a watchlist to delete.")
        return

    item = tree.item(selected_item)
    watchlist_id = item["values"][0]
    list_name = item["values"][1]

    confirm = messagebox.askyesno("Confirm Delete", f"Delete '{list_name}'?")
    if not confirm:
        return

    success, deleted_name = delete_watchlist(watchlist_id)

    if success:
        print_watchlists()
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END)
        messagebox.showinfo("Deleted", f"Watchlist '{list_name}' deleted.")      
    else:
        messagebox.showwarning("Error", "Watchlist not found or already deleted.")

def update_watchlist_gui():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Error", "Please select a watchlist to update.")
        return

    item = tree.item(selected_item)
    list_id = item["values"][0]
    old_list_name = item["values"][1]

    new_list_name = entry_list.get()
    new_teacher_name = entry_teacher.get()

    if not new_list_name or not new_teacher_name:
        messagebox.showwarning("Error", "Please fill in all fields.")
        return

    updated = update_watchlist(list_id, new_list_name, new_teacher_name)
    if updated > 0:
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END) 
        messagebox.showinfo("Updated", f"Watchlist '{old_list_name}' updated.")
        print_watchlists()
    else:
        messagebox.showwarning("Error", "No watchlist found to update.")

def on_row_select(event):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        values = item["values"]
        
        entry_list.delete(0, tk.END)
        entry_list.insert(0, values[1])
        entry_teacher.delete(0, tk.END)
        entry_teacher.insert(0, values[2])

#==============================================================#
# functions for adding titles to watchlists and viewing titles #
#==============================================================#
 
def view_titles_in_watchlist():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Error", "Select a watchlist first.")
        return

    item = tree.item(selected_item)
    list_id = item["values"][0]
    list_name = item["values"][1]

    titles = get_titles_for_watchlist(list_id)
    if not titles:
        messagebox.showinfo("Info", f"No titles found for '{list_name}'.")
        return

    win = tk.Toplevel(root)
    win.title(f"Titles in '{list_name}'")
    win.geometry("700x300")

    title_tree = ttk.Treeview(win, columns=("Show ID", "Title", "Type", "Year", "Rating"), show="headings")
    for col in ("Show ID", "Title", "Type", "Year", "Rating"):
        title_tree.heading(col, text=col)
        title_tree.column(col, width=120)
        if col == "Title":
            title_tree.column(col, width=250)
        elif col == "Show ID" or col == "Year" or "Rating":
            title_tree.column(col, width=50, anchor="center")
    title_tree.pack(fill="both", expand=True)

    for t in titles:
        title_tree.insert("", "end", values=t)

    def remove_selected_title():
        selected_title = title_tree.selection()
        if not selected_title:
            messagebox.showwarning("Error", "Select a title to remove.")
            return

        item = title_tree.item(selected_title)
        show_id = item["values"][0]
        show_title = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Remove", 
            f"Remove title '{show_title}' from watchlist '{list_name}'?"
        )
        if not confirm:
            return

        success = remove_title_from_watchlist(list_id, show_id)
        if success:
            messagebox.showinfo("Removed", f"Title '{show_title}' removed from '{list_name}'.")
            for i in title_tree.get_children():
                title_tree.delete(i)
            for t in get_titles_for_watchlist(list_id):
                title_tree.insert("", "end", values=t)
        else:
            messagebox.showwarning("Error", "Failed to remove title or title not found.")

    tk.Button(win, text="Remove Selected Title", command=remove_selected_title).pack(pady=10)
    
#================================================================================#
#                       fancy view all title functions                           #                 
# this comes with ability to add watchlists via right click vs. entering show id #
#================================================================================#

def view_all_titles(): 
    titles = get_all_titles()
    if not titles:
        messagebox.showinfo("Info", "No titles found in database.")
        return

    win = tk.Toplevel(root)
    win.title("All Titles in Netflix Database")
    win.geometry("900x500")

    tk.Label(win, text="Search by title, year, name:").pack(pady=5)
    search_var = tk.StringVar()
    tk.Entry(win, textvariable=search_var, width=50).pack(pady=5)

    frame = ttk.Frame(win) 
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.grid(row=0, column=1, sticky="ns")

    main_columns = ("Show ID", "Title", "Type", "Release Year", "Rating")

    title_tree = ttk.Treeview(frame, columns=main_columns, show="headings", yscrollcommand=scrollbar.set) 
    title_tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.config(command=title_tree.yview)
    frame.grid_columnconfigure(0, weight=1) 
    frame.grid_rowconfigure(0, weight=1)

    for col in main_columns:
        title_tree.heading(col, text=col)
        if col == "Show ID" or col == "Release Year":
            title_tree.column(col, width=50, anchor="center")
        elif col == "Title":
            title_tree.column(col, width=300)
        else:
            title_tree.column(col, width=150, anchor="center")

    def populate_titles(filter_text=""):
        for i in title_tree.get_children():
            title_tree.delete(i)
        filtered = [t for t in titles if filter_text.lower() in t[1].lower() or filter_text in str(t[3])]
        for t in filtered:
            title_tree.insert("", "end", values=(t[0], t[1], t[2], t[3], t[4]))

    populate_titles()
    search_var.trace_add("write", lambda *_: populate_titles(search_var.get().strip()))

    menu = tk.Menu(win, tearoff=0)
    selected_show_id = None

    def add_title_to_watchlist_dropdown(show_id):
        watchlists = read_all_watchlist()
        if not watchlists:
            messagebox.showinfo("Info", "No watchlists available. Create one first.")
            return

        wl_win = tk.Toplevel(win)
        wl_win.title(f"Add '{show_id}' to Watchlist")
        wl_win.geometry("350x120")

        tk.Label(wl_win, text="Select a Watchlist:").pack(pady=5)
        wl_var = tk.StringVar()
        wl_names = [f"{wl[1]} ({wl[2]})" for wl in watchlists]
        wl_combo = ttk.Combobox(wl_win, values=wl_names, textvariable=wl_var, state="readonly")
        wl_combo.pack(pady=5)
        wl_combo.current(0)

        def add_selected():
            index = wl_combo.current()
            list_id = watchlists[index][0]
            success, msg = add_title_to_watchlist(list_id, show_id) 
            if success:
                messagebox.showinfo("Success", f"Added show '{show_id}' to watchlist.")
                wl_win.destroy()
            else:
                messagebox.showwarning("Error", msg)

        tk.Button(wl_win, text="Add", command=add_selected).pack(pady=5)

    def view_watchlists_containing_title(show_id):
        show_watchlists_for_title(show_id)

    menu.add_command(label="Add to Watchlist", command=lambda: add_title_to_watchlist_dropdown(selected_show_id))
    menu.add_command(label="View Watchlists", command=lambda: view_watchlists_containing_title(selected_show_id))

    def popup_menu(event):
        nonlocal selected_show_id
        iid = title_tree.identify_row(event.y)
        if iid:
            title_tree.selection_set(iid)
            item = title_tree.item(iid)
            selected_show_id = item["values"][0]
            menu.post(event.x_root, event.y_root)

    title_tree.bind("<Button-3>", popup_menu)
    title_tree.bind("<Control-Button-1>", popup_menu)

    def on_title_double_click(event):
        iid = title_tree.selection()
        if not iid:
            return

        item = title_tree.item(iid)
        show_id = item["values"][0]

        full_data = next((t for t in get_all_titles() if t[0] == show_id), None)
        if not full_data:
            messagebox.showwarning("Error", "Title not found.")
            return

        info_win = tk.Toplevel(title_tree.master)
        info_win.title(f"Details for {full_data[1]}")
        info_win.geometry("600x500")

        canvas = tk.Canvas(info_win)
        scrollbar = ttk.Scrollbar(info_win, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        all_columns = ("Show ID", "Title", "Type", "Release Year", "Rating", 
                    "Duration", "Description", "Date Added", "Director", 
                    "Cast", "Country")

        for i, col in enumerate(all_columns):
            tk.Label(scroll_frame, text=f"{col}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="nw", padx=5, pady=2
            )
            value = full_data[i] if i < len(full_data) else ""
            tk.Label(scroll_frame, text=str(value), wraplength=450, justify="left").grid(
                row=i, column=1, sticky="w", padx=5, pady=2
            )

    title_tree.bind("<Double-1>", on_title_double_click)

def show_watchlists_for_title(show_id): 
    watchlists = get_watchlists_for_title(show_id)
    if not watchlists:
        messagebox.showinfo("Info", f"No watchlists contain title '{show_id}'.")
        return

    win = tk.Toplevel(root)
    win.title(f"Watchlists containing '{show_id}'")
    win.geometry("600x300")

    wl_tree = ttk.Treeview(win, columns=("List ID", "List Name", "Teacher Name"), show="headings")
    for col in ("List ID", "List Name", "Teacher Name"):
        wl_tree.heading(col, text=col)
        wl_tree.column(col, width=180)
    wl_tree.pack(fill="both", expand=True)

    for w in watchlists:
        wl_tree.insert("", "end", values=w)

#=================================#
# DATABASE QUERY FUNCTIONS        #
#=================================#

def fetch_all_subjects():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT subject_name FROM Subjects ORDER BY subject_name ASC")
        subjects = [row[0] for row in c.fetchall()]
        conn.close()
        
        if not subjects:
            messagebox.showwarning("DB Warning", "Could not find any subjects in the 'Subjects' table.")
            return ["No subjects found"]
            
        return subjects
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not fetch subjects: {e}")
        return ["DB Error"]

def on_query_select(event):
    param_frame_q1.pack_forget()
    param_frame_q2.pack_forget()
    param_frame_q3.pack_forget()
    param_frame_q4.pack_forget()
    
    selected_query = query_combo.get()
    
    if selected_query == "Query 1: Find by Academic Keyword (in Description)":
        param_frame_q3.pack(pady=5)
    elif selected_query == "Query 2: Find by Genre (Top-Rated)":
        param_frame_q1.pack(pady=5)
    elif selected_query == "Query 3: Find Films by Age Rating & Duration":
        param_frame_q2.pack(pady=5)
    elif selected_query == "Query 4: Find Average Rating Per Year":
        param_frame_q4.pack(pady=5)

def run_selected_query():
    selected_option = query_combo.get()
    results_text.delete('1.0', tk.END)
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        results_text.insert(tk.END, f"--- Running: {selected_option} ---\n")
        
        query = ""
        params = ()

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
                        AND numVotes >= 1000
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

        else:
            messagebox.showwarning("Warning", "Please select a valid query.")
            conn.close()
            return

        c.execute(query, params)
        results = c.fetchall()
        
        if results:
            col_names = [description[0] for description in c.description]
            results_text.insert(tk.END, f"{col_names}\n")
            results_text.insert(tk.END, "-"*60 + "\n")

            for row in results:
                formatted_string = ""
                
                if selected_option == "Query 1: Find by Academic Keyword (in Description)":
                    title, rating, type, desc = row
                    formatted_string = f"Title: {title} ({type}, IMDB: {rating})\n"
                    formatted_string += f"  Desc: {desc[:150]}...\n\n"
                    
                elif selected_option == "Query 2: Find by Genre (Top-Rated)":
                    title, type, rating, year = row
                    formatted_string = f"Title: {title} ({type}, {year}) - IMDB: {rating}\n\n"
                    
                elif selected_option == "Query 3: Find Films by Age Rating & Duration":
                    title, age_rating, dur, imdb_rating, desc = row
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

#=================#
# actual GUI code #
#=================#

# Fetch subjects before creating main window
all_subjects_list = fetch_all_subjects()

root = tk.Tk()
root.title("Netflix Watchlist Manager")

notebook = ttk.Notebook(root) # adding tabs
notebook.pack(fill="both", expand=True, padx=10, pady=10)

tab_watchlists = ttk.Frame(notebook)
tab_queries = ttk.Frame(notebook)

notebook.add(tab_watchlists, text="Watchlists") # first tab
notebook.add(tab_queries, text="Database Queries") # second tab

main_frame = tk.Frame(tab_watchlists)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# left frame for watchlist management
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(left_frame, text="Search watchlists:", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
search_var = tk.StringVar()
search_entry = tk.Entry(left_frame, textvariable=search_var)
search_entry.pack(pady=2, fill="x")

tree_frame = tk.Frame(left_frame)
tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scrollbar.pack(side="right", fill="y")

tree = ttk.Treeview(tree_frame, columns=("ID", "List Name", "Teacher Name", "Created Date"), show="headings", yscrollcommand=tree_scrollbar.set)
tree.heading("ID", text="ID") 
tree.column("ID", width=50, anchor="center")
tree.heading("List Name", text="List Name")
tree.heading("Teacher Name", text="Teacher Name")
tree.heading("Created Date", text="Created Date")
tree.column("Created Date", width=120, anchor="center")
tree.pack(fill="both", expand=True)
tree.bind("<<TreeviewSelect>>", on_row_select)
tree.bind("<Double-1>", lambda e: view_titles_in_watchlist())

tree_scrollbar.config(command=tree.yview)

tk.Label(left_frame, text="Double click on a watchlist to view its contents. Click anywhere to clear list name and teacher name entry boxes.").pack(pady=5)

tk.Label(left_frame, text="Enter watchlist name and teacher name to create watchlist.", font=("tkDefaultFont", 10, "bold")).pack(pady=2)

tk.Label(left_frame, text="List Name:", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
entry_list = tk.Entry(left_frame)
entry_list.pack(pady=2, padx=25)

tk.Label(left_frame, text="Teacher Name:", font=("tkDefaultFont", 10, "bold")).pack(pady=5)
entry_teacher = tk.Entry(left_frame)
entry_teacher.pack(pady=2, padx=25)
tk.Button(left_frame, text="Create Watchlist", command=add_watchlist).pack(padx=10, pady=5)

btn_frame = tk.Frame(left_frame)
btn_frame.pack(pady=10, fill="x")

left_btn_frame = tk.Frame(btn_frame)
left_btn_frame.pack(side="left", padx=5)

tk.Label(left_btn_frame, text="Select a watchlist to update or delete.", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
tk.Button(left_btn_frame, text="Update Selected Watchlist", command=update_watchlist_gui).pack(padx=10, pady=5)
tk.Button(left_btn_frame, text="Delete Selected Watchlist", command=delete_selected).pack(padx=10, pady=5)

def populate_watchlists(filter_text=""):
    for i in tree.get_children():
        tree.delete(i)
    all_watchlists = read_all_watchlist()
    filtered = [
        wl for wl in all_watchlists
        if filter_text.lower() in wl[1].lower() or filter_text.lower() in wl[2].lower()
    ]
    for wlValues in filtered:
        tree.insert("", "end", values=(wlValues[0], wlValues[1], wlValues[2], wlValues[3]))

populate_watchlists()

def on_search_change(*_):
    populate_watchlists(search_var.get().strip())

search_var.trace_add("write", on_search_change)

right_btn_frame = tk.Frame(btn_frame)
right_btn_frame.pack(side="right", padx=5)

tk.Label(right_btn_frame, text="View and add titles:", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
tk.Button(right_btn_frame, text="View All Titles", command=view_all_titles, width=20).pack(padx=5, pady=5)

#===============================#
# DATABASE QUERY SECTION        #
#===============================#

query_section = tk.Frame(tab_queries) # removed separator to make tabs
query_section.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(query_section, text="Educational Content Finder - Database Queries", font=("tkDefaultFont", 12, "bold")).pack(pady=5)

query_frame = ttk.Frame(query_section, padding="10")
query_frame.pack(fill='x')

tk.Label(query_frame, text="Select a Query:", font=("tkDefaultFont", 10, "bold")).pack(pady=5)

query_options = [
    "Query 1: Find by Academic Keyword (in Description)",
    "Query 2: Find by Genre (Top-Rated)",
    "Query 3: Find Films by Age Rating & Duration",
    "Query 4: Find Average Rating Per Year",
    "Query 5: Find Best Movies Per Year"
]
query_combo = ttk.Combobox(query_frame, values=query_options, width=50, state="readonly")
query_combo.pack(pady=5)
query_combo.current(0)
query_combo.bind("<<ComboboxSelected>>", on_query_select)

# Parameter Frames
param_frame_q1 = ttk.Frame(query_frame)
tk.Label(param_frame_q1, text="Genre:").grid(row=0, column=0, padx=5, sticky="e")
param1_combo = ttk.Combobox(param_frame_q1, values=all_subjects_list, width=25, state="readonly")
param1_combo.grid(row=0, column=1, padx=5)
param1_combo.set("Documentaries")
tk.Label(param_frame_q1, text="Min IMDB Rating:").grid(row=1, column=0, padx=5, sticky="e")
param1_rating_entry = tk.Entry(param_frame_q1, width=28)
param1_rating_entry.grid(row=1, column=1, padx=5)
param1_rating_entry.insert(0, "7.5")

param_frame_q2 = ttk.Frame(query_frame)
tk.Label(param_frame_q2, text="Age Rating:").grid(row=0, column=0, padx=5, sticky="e")
param2_age_entry = tk.Entry(param_frame_q2, width=28)
param2_age_entry.grid(row=0, column=1, padx=5)
param2_age_entry.insert(0, "PG-13")
tk.Label(param_frame_q2, text="Max Duration (min):").grid(row=1, column=0, padx=5, sticky="e")
param2_duration_entry = tk.Entry(param_frame_q2, width=28)
param2_duration_entry.grid(row=1, column=1, padx=5)
param2_duration_entry.insert(0, "50")

param_frame_q3 = ttk.Frame(query_frame)
tk.Label(param_frame_q3, text="Academic Keyword:").grid(row=0, column=0, padx=5, sticky="e")
param3_keyword_entry = tk.Entry(param_frame_q3, width=28)
param3_keyword_entry.grid(row=0, column=1, padx=5)
param3_keyword_entry.insert(0, "Shakespeare")
tk.Label(param_frame_q3, text="Min IMDB Rating:").grid(row=1, column=0, padx=5, sticky="e")
param3_rating_entry = tk.Entry(param_frame_q3, width=28)
param3_rating_entry.grid(row=1, column=1, padx=5)
param3_rating_entry.insert(0, "7.0")

param_frame_q4 = ttk.Frame(query_frame)
tk.Label(param_frame_q4, text="This query takes no parameters.").pack(pady=10)

tk.Button(query_frame, text="Run Selected Query", command=run_selected_query).pack(pady=10)

results_text = tk.Text(query_section, height=12, width=80, wrap="word")
results_text.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_results = ttk.Scrollbar(query_section, orient="vertical", command=results_text.yview)
results_text.configure(yscrollcommand=scrollbar_results.set)

on_query_select(None)

print_watchlists()

def deselect_treeview(event):
    clicked_widget = event.widget
    ignored_widgets = (ttk.Treeview, tk.Entry, tk.Button, ttk.Combobox, tk.Label, ttk.Scrollbar, tk.Text)

    if not isinstance(clicked_widget, ignored_widgets):
        tree.selection_remove(tree.selection())
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END)

root.bind("<Button-1>", deselect_treeview)

root.mainloop()