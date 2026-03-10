# Netflix-and-IMDB-Movie-Database--Databaseproject25

The file to run the program lives in the file 'testfinal.py' 
If you have the netflix_db.db you should be able to run this file and explore the program

**if missing netflix_db.db ,To create the database**

Once you have cloned this repo onto your local machine you can run these commands in your terminal in order 

1. Creates the db with the appropraite tables 
  "py create_db.py"

2. populates the data from the csv file
  "py populate_db.py" 

3. populate the netflix and IMDB table with
   "import_merged_to_db.py"

4. you also need this on your local computer its too big to push to github,
 title.basics.tsv
download it here https://datasets.imdbws.com/

**YOU now have all the tables**

you'll have to set up a **DATABASE CONNECTION** if youre using vs code:

go to extensions > install 'SQLtools' from mattheus teixeira> also install the driver called "SQLTools SQLite" from mattheus teixeira > create a connection > probably have to restart and install dependices 

***its the cyllinder shape on the left hand side

it uses a path thats in your files , you can check your file explorer for the path something like "C:\Users\Yourname\Desktop\DatabaseProject25\netflix_db.db"
-name it netflix DB (whatever you want)
- test connection
- save connection

You can now query the database with that connection
👌👽

Group Project from Database Systems Course Fall 25 
