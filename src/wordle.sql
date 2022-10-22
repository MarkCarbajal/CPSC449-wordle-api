PRAGMA FOREIGN_KEYS=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    userid INTEGER primary key,
    username VARCHAR,
    password VARCHAR
);

DROP TABLE IF EXISTS games;
CREATE TABLE games (
    gameid INTEGER primary key,
    userid INT references user(id),
    correctword VARCHAR,
    validword VARCHAR,
    gamewin BOOLEAN,
    guessnum INT
);

/*Add tables for input checking*/

COMMIT;
