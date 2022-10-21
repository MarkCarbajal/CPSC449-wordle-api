PRAGMA FOREIGN_KEYS=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER primary key,
    username VARCHAR,
    password VARCHAR
);

DROP TABLE IF EXISTS game;
CREATE TABLE game(
    id INTEGER primary key,
    id_user INT references user(id),
    correct_word VARCHAR,
    valid_word VARCHAR,
    game_win BOOLEAN,
    guess_num INT
);

/*Add tables for input checking*/

COMMIT;
