-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    body VARCHAR(1023) NOT NULL,
    analysed_body VARCHAR(1023),
    public BOOLEAN NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);