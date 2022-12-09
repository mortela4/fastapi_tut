"""
Piccolo-ORM config file.
"""

from piccolo.engine.sqlite import SQLiteEngine

DB_NAME = "my_db.sqlite"

# Define DB to use:
DB = SQLiteEngine(path=DB_NAME)      
