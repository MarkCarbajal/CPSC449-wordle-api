"""
Generate a database with two one column tables in the database wordle.db:
    - correct: a table of correct words for the wordle game
    - valid: a table of valid and correct words for the wordle game
Calls 3 bash commands to accomplish this.

Group 2
Mark Carbajal
Nicholas Fonseca
Maria Ortega
Marina Urrutia

CPSC449 Fall 2022: Section 1
"""
## IMPORTS
import subprocess as sp
import json
import sqlite3
import typing
import os

## CONSTANTS
NYTIMES_LINK = "https://www.nytimes.com/games-assets/v2/" \
               "wordle.9137f06eca6ff33e8d5a306bda84e37b69a8f227.js"
WORDLE_JS = "wordle.9137f06eca6ff33e8d5a306bda84e37b69a8f227.js"
CORRECT_FNAME = "correct.json"
VALID_FNAME = "valid.json"
DB_NAME = "src/wordle.db"
EXP_CORRECT = 2309
EXP_VALID = 12546


## METHODS
def get_valid_and_correct_words():
    """Fetches and parses Wordle for words.

    Fetches the javascript for wordle from the NYT, and parses out
    the valid words and the correct words.

    Args:
        None

    Returns:
        A list of correct words, and a list of valid words.

    Side Effects:
        Creates 3 files - the wget'd .js file, and two json files for the
        valid and correct words

    """
    # wget the NYT Wordle game's js, and sed out the words to JSON files
    sp.run(f"wget {NYTIMES_LINK}", shell=True, stdout=open(os.devnull, 'wb'))
    sp.run(f"sed -e 's/^.*,ft=//' -e 's/,bt=.*$//' -e 1q {WORDLE_JS} > "
           f"{CORRECT_FNAME}", shell=True)
    sp.run(f"sed -e 's/^.*,bt=//' -e 's/;.*$//' -e 1q {WORDLE_JS} > "
           f"{VALID_FNAME}", shell=True)

    # Parse the produced JSON Files
    with open(CORRECT_FNAME, 'r') as correct_fp:
        correct_words = json.load(correct_fp)

    with open(VALID_FNAME, 'r') as valid_fp:
        valid_words = json.load(valid_fp)

    return correct_words, valid_words


def create_db(correct_words, valid_words):
    """Creates a database with a correct and a valid table.

    Args:
        correct_words: A list of correct words for wordle.
        valid_words: A list of valid words for wordle.

    Returns:
        None

    Side Effects:
        world.db database with two tables.

    """
    # Create the wordle.db, and if the tables already exist,
    # drop them
    db_conn = sqlite3.connect(DB_NAME)
    db_cur = db_conn.cursor()
    db_cur.execute("DROP TABLE IF EXISTS valid")
    db_cur.execute("DROP TABLE IF EXISTS correct")

    # Create the new tables
    db_cur.execute("CREATE TABLE correct(words CHAR(5))")
    db_cur.execute("CREATE TABLE valid(words CHAR(5))")

    # Iterate thru the words and insert them into the tables
    for word in correct_words:
        word = ( f"{word}", )
        db_cur.execute("INSERT INTO correct VALUES (?)", word)
    for word in valid_words:
        word = ( f"{word}", )
        db_cur.execute("INSERT INTO valid VALUES (?)", word)

    with open("src/wordle.sql") as sql_script:
        db_cur.executescript(sql_script.read())


    # Commit the changes
    db_conn.commit()


## MAIN
if __name__ == "__main__":
    correct, valid = get_valid_and_correct_words()
    # Clean up the extra files
    os.remove(VALID_FNAME)
    os.remove(CORRECT_FNAME)
    os.remove(WORDLE_JS)
    # Double check that there's the expect number of words
    # Comment this out as this is technically a "dynamic" solution
#    if (len(correct) != EXP_CORRECT):
#        print("Something went wrong with parsing")
#        exit(1)
#    if (len(valid) != EXP_VALID):
#        print("Something went wrong with parsing")
#        exit(1)
    # Valid should include correct
    valid += correct
    create_db(correct, valid)

