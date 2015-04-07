QueryBox 1.0:

If you want to run this demo in your local server, querying your own database,
you can try running it as it is set up by default.
However you will be querying against a CSV file, which is REALLY, REALLY slow,
and terribly bad in performance.
I'd really recomennd you go set up a DB and get it running there.

So to run this from your DB You'll need PHP and Mysql installed.

1. GRAB THE CSV FILE
    go grab this file:
    http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv
    drop it inside the /tests/data folder.

2. SETUP YOUR DATABASE
    There's a createdatabase.php script inside the test/_masters folder.
    Run that to set up the table and parse the csv file into your DB.

3. POINT QUERYBOX TO THE DB_SEARCH SCRIPT
    Once you are done, open up the class.querybox.php file and set up the
    query method properly pointing it to your DB.

    Lastly, in index.php, change the line that reads:
    
        var qbox = new marumushi.widget.QueryBox('csv_search.php?q=','qbox');
    
        for:
    
        var qbox = new marumushi.widget.QueryBox('db_search.php?q=','qbox');
 
 You should be set to use QueryBox to query your DB.
 
 Have fun!
 
 .marcos
 