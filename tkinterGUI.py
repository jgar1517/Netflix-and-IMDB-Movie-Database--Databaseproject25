import tkinter as tk
import sqlite3
from tkinter import ttk # for styling
import os
from tkinter import messagebox # for displaying message boxes
from Crud_components import create_watchlist, read_all_watchlist, delete_watchlist, update_watchlist, add_title_to_watchlist, get_titles_for_watchlist, get_all_titles, get_watchlists_for_title, remove_title_from_watchlist # imports funcs from crud_components.py

#=========================#
# crud for watchlists GUI #
#=========================#

def add_watchlist(): # function to add watchlist
    selected_item = tree.selection() # checks if an item is selected in the treeview
    # if an item is selected, show error message and return
    if selected_item:
        messagebox.showwarning(
            "Error",
            "You have an existing watchlist selected. "
            "Use 'Update Selected Watchlist' to change it, or deselect first to create a new one."
        )
        return    
    # gets values from entry fields
    list_name = entry_list.get()
    teacher_name = entry_teacher.get() 
    
    if list_name and teacher_name: # checks if both fields are filled
        create_watchlist(list_name, teacher_name) # calls the create_watchlist function
        # clears the entry fields
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END) 
        print_watchlists() # refreshes the watchlist display
        messagebox.showinfo("Success", f"Watchlist '{list_name}' added.") # shows success message
    else:
        messagebox.showwarning("Error", "Please fill in all fields.")

def print_watchlists(): # function to print watchlists
    for item in tree.get_children(): # clears the treeview
        tree.delete(item) # deletes each item in the treeview

    watchlists = read_all_watchlist()  # calls the read_all_watchlist function
    for wlValues in watchlists: # iterates through the watchlists
        tree.insert('', 'end', values=(wlValues[0],wlValues[1], wlValues[2], wlValues[3])) # inserts watchlist data into the treeview

def delete_selected(): # function to delete selected watchlist
    selected_item = tree.selection() # gets the selected item in the treeview
    if not selected_item:
        messagebox.showwarning("Error", "Please select a watchlist to delete.")
        return

    item = tree.item(selected_item) # gets the item data
    watchlist_id = item["values"][0] # gets the watchlist ID from the selected item
    list_name = item["values"][1] # gets the list name from the selected item

    confirm = messagebox.askyesno("Confirm Delete", f"Delete '{list_name}'?") # asks for confirmation
    if not confirm:
        return

    success, deleted_name = delete_watchlist(watchlist_id) # calls the delete_watchlist function

    if success: # if a watchlist was deleted
        print_watchlists() # refreshes the watchlist display
        # clears the entry fields
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END)
        messagebox.showinfo("Deleted", f"Watchlist '{list_name}' deleted.")      
    else:
        messagebox.showwarning("Error", "Watchlist not found or already deleted.")

def update_watchlist_gui(): # function to update selected watchlist
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Error", "Please select a watchlist to update.")
        return

    item = tree.item(selected_item)
    list_id = item["values"][0]      # ID from Treeview
    old_list_name = item["values"][1]

    new_list_name = entry_list.get()
    new_teacher_name = entry_teacher.get()

    if not new_list_name or not new_teacher_name:
        messagebox.showwarning("Error", "Please fill in all fields.")
        return

    updated = update_watchlist(list_id, new_list_name, new_teacher_name) # calls the update_watchlist function
    if updated > 0: # if a watchlist was updated
        entry_list.delete(0, tk.END) # clears the entry fields
        entry_teacher.delete(0, tk.END) 
        messagebox.showinfo("Updated", f"Watchlist '{old_list_name}' updated.")
        print_watchlists()
    else:
        messagebox.showwarning("Error", "No watchlist found to update.")

def on_row_select(event): # function to handle row selection in treeview
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        values = item["values"]
        
        entry_list.delete(0, tk.END)
        entry_list.insert(0, values[1])  # list_name
        entry_teacher.delete(0, tk.END)
        entry_teacher.insert(0, values[2])  # teacher_name


#==============================================================#
# functions for adding titles to watchlists and viewing titles #
#==============================================================#
 
 # opens a new window to view titles in the selected watchlist, has scroll and search functionality
def view_titles_in_watchlist():
    selected_item = tree.selection() # gets the selected watchlist
    if not selected_item:
        messagebox.showwarning("Error", "Select a watchlist first.")
        return

    item = tree.item(selected_item) # gets the item data
    list_id = item["values"][0] # gets the watchlist ID
    list_name = item["values"][1] # gets the watchlist name

    titles = get_titles_for_watchlist(list_id) # gets titles for the watchlist
    if not titles:
        messagebox.showinfo("Info", f"No titles found for '{list_name}'.")
        return

    # new popup window
    win = tk.Toplevel(root)
    win.title(f"Titles in '{list_name}'")
    win.geometry("700x300")

    # treeview for titles
    title_tree = ttk.Treeview(win, columns=("Show ID", "Title", "Type", "Year", "Rating"), show="headings")
    for col in ("Show ID", "Title", "Type", "Year", "Rating"): # sets up columns
        title_tree.heading(col, text=col)
        title_tree.column(col, width=120)
        if col == "Title":
            title_tree.column(col, width=250) # wider for title column  
        elif col == "Show ID" or col == "Year" or "Rating":
            title_tree.column(col, width=50, anchor="center")    # shorter for IDs and Year
    title_tree.pack(fill="both", expand=True) # makes the treeview expand to fill the window

    for t in titles:
        title_tree.insert("", "end", values=t) # inserts titles into the treeview

    def remove_selected_title():
        selected_title = title_tree.selection() # gets the selected title
        if not selected_title:
            messagebox.showwarning("Error", "Select a title to remove.")
            return

        item = title_tree.item(selected_title) # gets the item data
        show_id = item["values"][0] # gets the show ID
        show_title = item["values"][1] # gets the show title

        confirm = messagebox.askyesno( # asks for confirmation
            "Confirm Remove", 
            f"Remove title '{show_title}' from watchlist '{list_name}'?"
        )
        if not confirm:
            return

        success = remove_title_from_watchlist(list_id, show_id) # removes the title from the watchlist
        if success:
            messagebox.showinfo("Removed", f"Title '{show_title}' removed from '{list_name}'.")
            # refresh the view
            for i in title_tree.get_children():
                title_tree.delete(i)
            for t in get_titles_for_watchlist(list_id):
                title_tree.insert("", "end", values=t)
        else:
            messagebox.showwarning("Error", "Failed to remove title or title not found.")

    tk.Button(win, text="Remove Selected Title", command=remove_selected_title).pack(pady=10) # button to remove selected title
    
#================================================================================#
#                       fancy view all title functions                           #                 
# this comes with ability to add watchlists via right click vs. entering show id #
#================================================================================#

def view_all_titles(): 
    titles = get_all_titles() # gets all titles from the database
    if not titles:
        messagebox.showinfo("Info", "No titles found in database.")
        return

    win = tk.Toplevel(root) # new popup window
    win.title("All Titles in Netflix Database") # title of the window
    win.geometry("900x500")

    # Search bar
    tk.Label(win, text="Search by title or release year:").pack(pady=5) # label for search bar
    search_var = tk.StringVar() # variable to hold search text
    tk.Entry(win, textvariable=search_var, width=50).pack(pady=5) # entry for search bar

    # Frame for treeview and scrollbar
    frame = ttk.Frame(win) 
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(frame, orient="vertical") # scrollbar for treeview
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Main columns only
    main_columns = ("Show ID", "Title", "Type", "Release Year", "Rating")

    # Treeview for titles
    title_tree = ttk.Treeview(frame, columns=main_columns, show="headings", yscrollcommand=scrollbar.set) 
    title_tree.grid(row=0, column=0, sticky="nsew") # makes the treeview expand to fill the frame
    scrollbar.config(command=title_tree.yview) # connects scrollbar to treeview
    frame.grid_columnconfigure(0, weight=1) 
    frame.grid_rowconfigure(0, weight=1)

    # Set up columns
    for col in main_columns:
        title_tree.heading(col, text=col)
        if col == "Show ID" or col == "Release Year":
            title_tree.column(col, width=50, anchor="center")    # shorter for IDs
        elif col == "Title":
            title_tree.column(col, width=300)   # wider for titles
        else:
            title_tree.column(col, width=150, anchor="center")   # default for others

    # Populate treeview
    def populate_titles(filter_text=""):
        for i in title_tree.get_children():
            title_tree.delete(i)
        filtered = [t for t in titles if filter_text.lower() in t[1].lower() or filter_text in str(t[3])]
        for t in filtered:
            title_tree.insert("", "end", values=(t[0], t[1], t[2], t[3], t[4]))

    # initial population
    populate_titles()
    search_var.trace_add("write", lambda *_: populate_titles(search_var.get().strip())) # live search

    # right click to add to watchlist or view watchlists containing title
    menu = tk.Menu(win, tearoff=0)
    selected_show_id = None

    # function to add title to selected watchlist
    def add_title_to_watchlist_dropdown(show_id):
        watchlists = read_all_watchlist() # get all watchlists
        if not watchlists:
            messagebox.showinfo("Info", "No watchlists available. Create one first.")
            return

        wl_win = tk.Toplevel(win) # new popup window
        wl_win.title(f"Add '{show_id}' to Watchlist")
        wl_win.geometry("350x120")

        tk.Label(wl_win, text="Select a Watchlist:").pack(pady=5) # label for watchlist selection
        wl_var = tk.StringVar()
        wl_names = [f"{wl[1]} ({wl[2]})" for wl in watchlists] # list of watchlist names
        wl_combo = ttk.Combobox(wl_win, values=wl_names, textvariable=wl_var, state="readonly") # dropdown for watchlist selection
        wl_combo.pack(pady=5)
        wl_combo.current(0)

        def add_selected(): # function to add title to selected watchlist
            index = wl_combo.current() # get selected index
            list_id = watchlists[index][0] # get list_id from selected watchlist
            success, msg = add_title_to_watchlist(list_id, show_id) 
            if success:
                messagebox.showinfo("Success", f"Added show '{show_id}' to watchlist.")
                wl_win.destroy()
            else:
                messagebox.showwarning("Error", msg)

        tk.Button(wl_win, text="Add", command=add_selected).pack(pady=5) # button to add title

    def view_watchlists_containing_title(show_id): # function to view watchlists containing the title
        show_watchlists_for_title(show_id) # calls function to show watchlists containing title

    menu.add_command(label="Add to Watchlist", command=lambda: add_title_to_watchlist_dropdown(selected_show_id)) # menu option to add title to watchlist
    menu.add_command(label="View Watchlists", command=lambda: view_watchlists_containing_title(selected_show_id)) # menu option to view watchlists containing title

    def popup_menu(event): # function to show popup menu
        nonlocal selected_show_id  # declare selected_show_id as nonlocal
        iid = title_tree.identify_row(event.y) # gets the row under the cursor
        if iid: # if a row is found
            title_tree.selection_set(iid) # select the row
            item = title_tree.item(iid) # gets the item data
            selected_show_id = item["values"][0] # gets the show ID
            menu.post(event.x_root, event.y_root) # shows the menu at the cursor position

    title_tree.bind("<Button-3>", popup_menu) # right click to show menu - linux/windows
    title_tree.bind("<Control-Button-1>", popup_menu) # right click for macos

    # double click to view full details
    def on_title_double_click(event):
        iid = title_tree.selection()
        if not iid:
            return # no selection

        item = title_tree.item(iid) # gets the item data
        show_id = item["values"][0] # gets the show ID

        # Fetch full row from the database
        full_data = next((t for t in get_all_titles() if t[0] == show_id), None) # get full data for the selected title
        if not full_data:
            messagebox.showwarning("Error", "Title not found.")
            return

        info_win = tk.Toplevel(title_tree.master) # new popup window
        info_win.title(f"Details for {full_data[1]}") # title of the window
        info_win.geometry("600x500")

        # Scrollable frame setup - in case desc/or any are too long for window
        canvas = tk.Canvas(info_win) # canvas for scrolling
        scrollbar = ttk.Scrollbar(info_win, orient="vertical", command=canvas.yview) 
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind( # configure scroll region
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw") # add frame to canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True) # pack canvas
        scrollbar.pack(side="right", fill="y")

        # Columns to display
        all_columns = ("Show ID", "Title", "Type", "Release Year", "Rating", 
                    "Duration", "Description", "Date Added", "Director", 
                    "Cast", "Country")

        for i, col in enumerate(all_columns): # iterate through columns
            # Column label
            tk.Label(scroll_frame, text=f"{col}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="nw", padx=5, pady=2
            )
            # Column value
            value = full_data[i] if i < len(full_data) else "" # get value or empty string
            # for description or long text, use wraplength
            tk.Label(scroll_frame, text=str(value), wraplength=450, justify="left").grid(
                row=i, column=1, sticky="w", padx=5, pady=2
            )

    title_tree.bind("<Double-1>", on_title_double_click) # double click to view full details, should work on all platforms

# viewing watchlists containing a specific title
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

#=================#
# actual GUI code #
#=================#

root = tk.Tk() # main window
root.title("Netflix Watchlist Manager") # title of the window

# main frame
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10) # padding around the frame

# left frame for watchlist management
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# search bar for watchlists
tk.Label(left_frame, text="Search watchlists:", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
search_var = tk.StringVar()
search_entry = tk.Entry(left_frame, textvariable=search_var)
search_entry.pack(pady=2, fill="x") # adds padding

# frame for Treeview + scrollbar
tree_frame = tk.Frame(left_frame)
tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

# scrollbar
tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scrollbar.pack(side="right", fill="y")


tree = ttk.Treeview(tree_frame, columns=("ID", "List Name", "Teacher Name", "Created Date"), show="headings", yscrollcommand=tree_scrollbar.set) # 
tree.heading("ID", text="ID") 
tree.column("ID", width=50, anchor="center") # sets column width and alignment of ID to be short n small
tree.heading("List Name", text="List Name") # sets heading for List Name
tree.heading("Teacher Name", text="Teacher Name") # sets heading for Teacher Name
tree.heading("Created Date", text="Created Date") # sets heading for Created Date
tree.column("Created Date", width=120, anchor="center") # sets column width and alignment of Created Date
tree.pack(fill="both", expand=True) # makes the treeview expand to fill the window
tree.bind("<<TreeviewSelect>>", on_row_select) # binds row selection to on_row_select function
tree.bind("<Double-1>", lambda e: view_titles_in_watchlist()) # double click to view titles in watchlist

tree_scrollbar.config(command=tree.yview) # connects scrollbar to treeview

tk.Label(left_frame, text="Double click on a watchlist to view its contents. Click anywhere to clear list name and teacher name entry boxes.").pack(pady=5) # info label

tk.Label(left_frame, text="Enter watchlist name and teacher name to create watchlist.", font=("tkDefaultFont", 10, "bold")).pack(pady=2) # label for watchlist info

# entry fields for watchlist info
tk.Label(left_frame, text="List Name:", font=("tkDefaultFont", 10, "bold")).pack(pady=2) # label for list name
entry_list = tk.Entry(left_frame) # entry for list name
entry_list.pack(pady=2, padx=25) # adds padding and makes it fill horizontally

tk.Label(left_frame, text="Teacher Name:", font=("tkDefaultFont", 10, "bold")).pack(pady=5) # label for teacher name added padding
entry_teacher = tk.Entry(left_frame) # entry for teacher name
entry_teacher.pack(pady=2, padx=25) # adds padding and makes it fill horizontally
tk.Button(left_frame, text="Create Watchlist", command=add_watchlist).pack(padx=10, pady=5)

# Buttons for watchlist actions
btn_frame = tk.Frame(left_frame)
btn_frame.pack(pady=10, fill="x")

left_btn_frame = tk.Frame(btn_frame)
left_btn_frame.pack(side="left", padx=5)

tk.Label(left_btn_frame, text="Select a watchlist to update or delete.", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
tk.Button(left_btn_frame, text="Update Selected Watchlist", command=update_watchlist_gui).pack(padx=10, pady=5)
tk.Button(left_btn_frame, text="Delete Selected Watchlist", command=delete_selected).pack(padx=10, pady=5)

# function to populate watchlists with optional filtering
def populate_watchlists(filter_text=""):
    for i in tree.get_children(): # clears the treeview
        tree.delete(i)
    all_watchlists = read_all_watchlist() # reads all watchlists
    filtered = [ # filters watchlists based on search text
        wl for wl in all_watchlists
        if filter_text.lower() in wl[1].lower() or filter_text.lower() in wl[2].lower()
    ]
    for wlValues in filtered: # inserts filtered watchlists into the treeview
        tree.insert("", "end", values=(wlValues[0], wlValues[1], wlValues[2], wlValues[3]))

# Initial population
populate_watchlists()

# live search as user types
def on_search_change(*_):
    populate_watchlists(search_var.get().strip())

search_var.trace_add("write", on_search_change) # traces changes to the search variable

# right frame for viewing all titles
right_btn_frame = tk.Frame(btn_frame)
right_btn_frame.pack(side="right", padx=5)

tk.Label(right_btn_frame, text="View and add titles:", font=("tkDefaultFont", 10, "bold")).pack(pady=2)
tk.Button(right_btn_frame, text="View All Titles", command=view_all_titles, width=20).pack(padx=5, pady=5)

# auto-display watchlists on startup
print_watchlists()

# deselect treeview when clicking outside of it
def deselect_treeview(event):
    # Get the widget that was clicked
    clicked_widget = event.widget

    # List of widget classes that should not trigger deselection
    ignored_widgets = (ttk.Treeview, tk.Entry, tk.Button, ttk.Combobox, tk.Label, ttk.Scrollbar)

    # If the clicked widget is not in the ignored list, deselect the Treeview
    if not isinstance(clicked_widget, ignored_widgets):
        tree.selection_remove(tree.selection())
        # clear entry fields
        entry_list.delete(0, tk.END)
        entry_teacher.delete(0, tk.END)

# Bind left-click globally
root.bind("<Button-1>", deselect_treeview)

# main loop
root.mainloop() # starts the GUI event loop