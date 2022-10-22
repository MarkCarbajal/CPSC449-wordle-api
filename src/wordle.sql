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
    correctword VARCHAR(5),
    guess1 VARCHAR(5),
    guess2 VARCHAR(5),
    guess3 VARCHAR(5),
    guess4 VARCHAR(5),
    guess5 VARCHAR(5),
    guess6 VARCHAR(5),
    gamewin BOOLEAN,
    guessnum INT
);

/*Add tables for input checking*/

COMMIT;
