from sys import argv, exit, stderr
from closet import app
import argparse 


import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def main():
    parser = argparse.ArgumentParser(description="A closet-weather application")
    parser.add_argument("port",  help="the port at which the server should listen")
    args = parser.parse_args()
    print(args)
    if len(argv) != 2:
        print('Usage: runserver.py [-h]  port', file=stderr)
        exit(1)
    
    try:
        port = int(argv[1])
    except Exception:
        print('Port must be an integer.', file=stderr)
        exit(1)

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
