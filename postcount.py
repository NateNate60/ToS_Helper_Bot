# We keep track of who's submitted how many posts with an SQLite 3 database
submitters = sqlite3.connect(path.join(wpath, 'submitters.sqlite3'))
with submitters:
    submitters.execute("CREATE TABLE IF NOT EXISTS submitters"
                       "(username TEXT NOT NULL PRIMARY KEY,"
                       " quantity INTEGER NOT NULL,"
                       " last_date TEXT NOT NULL DEFAULT CURRENT_DATE)")