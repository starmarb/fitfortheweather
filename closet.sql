-- Database schema
DROP TABLE IF EXISTS clothes;

CREATE TABLE clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL, 
    description TEXT NOT NULL,
    img BLOB NOT NULL, 
    type TEXT NOT NULL, 
    summer INTEGER NOT NULL,
    fall INTEGER NOT NULL, 
    winter INTEGER NOT NULL,
    spring INTEGER NOT NULL,
    color TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE outfit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    outfitname TEXT NOT NULL,
    outfitvalue TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
