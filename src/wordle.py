import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort, redirect, url_for
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request, validate_response

from http import HTTPStatus
import json
from sqlalchemy import select, insert, func, update
import table_declarations as td
from typing import Optional
import request_dataclasses as rd

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"../{__name__}.toml", toml.load)

##CONNECT TO DATABASE##
async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database(app.config["DATABASES"]["URL"])
        await db.connect()
    return db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()

##WRITE API CODE HERE##

# NOTE: Routes can be changed, I just wanted to get down what
# I thought was good to move forward on them

#Test, returns all correct words to /, currently works.
@app.route("/", methods=["GET"])
async def test():
    db = await _get_db()
    all_words = await db.fetch_all("SELECT * FROM valid;")
    return list(map(dict, all_words))


###########################################################

@app.route("/register", methods=["POST"])
@validate_request(rd.AuthRequest)
async def create_user(data):
    db = await _get_db()
    usr_json = await request.get_json()
    try:
        username = usr_json['username']
        password = usr_json['password']
    except KeyError:
        return {'msg': 'Provide {"username":<username>, "password":<password>'},\
                400
    if username == '' or password == '':
        return {'msg': 'Username and password cannot be blank'},\
                400

    user_select = select(td.users)\
        .where(td.users.c.username == usr_json["username"])
    match = await db.fetch_one(user_select)
    print(match)
    if match is not None:
        return {'msg': 'Username taken'}, 400

    user_insert = insert(td.users).values(username=usr_json["username"], 
                                          password=usr_json["password"])
    user_id = await db.execute(user_insert)

    return {"user_id": user_id}, 201


@app.route("/login", methods=["GET"])
async def login():
    db = await _get_db()
    auth = request.headers["Authorization"]
    print(auth)
    try:
        # mask off
        auth_d = {}
        auth_d['uname'] = auth.split()[1].split(':')[0]
        auth_d['pword'] = auth.split()[1].split(':')[1]
    except IndexError:
        return "Fufill challenge in WWW-Authenticate", 401,\
               {'WWW-Authenticate': "Basic <username>:<password>"}

    query = select(td.users).where(td.users.c.username == auth_d["uname"])\
            .where(td.users.c.password == auth_d["uname"])
    result = await db.fetch_one(query)
    if result is not None:
        return { "authenticated": True }, 200
    return "Incorrect username or password",  401,\
            {'WWW-Authenticate': "Basic <username>:<password>"}


# Using dynamic routing, makes more sense to me. Maybe needs to change.
@app.route("/game", methods=["GET"])
async def get_users_games():
    db = await _get_db()
    usr_json = await request.get_json()
    print(usr_json)
    try:
        user_id = int(usr_json["user-id"])
    except (KeyError, TypeError, ValueError) as e:
        return {'msg': "Provide the {'user-id':<int:id>"}, 400
    user_select = select(td.users)\
        .where(td.users.c.userid == user_id)
    match = await db.fetch_one(user_select)
    if match is None:
        return {'msg': 'user-id not found'}, 400

    
    query = select(td.games).where(td.games.c.userid == user_id)\
            .where(td.games.c.gamewin == False)\
            .where(td.games.c.guessnum < 6)
    user_games = await db.fetch_all(query)
    return {"games":[game.gameid for game in user_games]}

@app.route("/game", methods=["POST"])
async def post_new_game():
    db = await _get_db()
    usr_json = await request.get_json()
    print(usr_json)
    try:
        user_id = int(usr_json["user-id"])
    except (KeyError, ValueError) as e:
        return {'msg': "Provide the {'user-id':<int:id>"}, 400
    user_select = select(td.users)\
        .where(td.users.c.userid == user_id)
    match = await db.fetch_one(user_select)
    if match is None:
        return {'msg': 'user-id not found'}, 400

    # Spun off of this, without query:
    # https://stackoverflow.com/a/33583008
    stmt = select(td.correct).order_by(func.random())
    to_guess = await db.fetch_one(stmt)

    insert_stmt = insert(td.games).values(
            userid = user_id,
            correctword = to_guess[0],
            guessnum = 0,
            gamewin = False,
    )

    game_id = await db.execute(insert_stmt)
    return {"game_id": game_id, "Location": f"/game/{game_id}"}, 201
    #return redirect(url_for("get_game_status", game_id=game_id))

@app.route("/game/<int:game_id>", methods=["GET"])
async def get_game_status(game_id):
    db = await _get_db()
    query = select(td.games).where(td.games.c.gameid==game_id)
    game = await db.fetch_one(query)
    if game == None:
        return {"msg": "No game exists with this id"}, 404
    right_spot = []
    wrong_spot = []
    guesses_remaining = 6 - game["guessnum"]
    if game["gamewin"] or guesses_remaining == 0:
        return {"game-won": game["gamewin"],
                "guesses-left": 6 - game["guessnum"]}, 200
    for guess_num in range(game["guessnum"]):
        correct_word = list(game["correctword"])
        this_guess = game["guesses"][guess_num*5:(guess_num+1)*5]
        # Generate right spot and valid lists
        # Obviously should be stored instead of doing this
        # Here be dragons
        for idx in range(5):
            this_right = []
            if this_guess[idx] == correct_word[idx]:
                this_right.append(correct_word.pop(idx))
                correct_word.insert(idx,'')
            right_spot.append(this_right)
        wrong_spot.append([correct_word.pop(correct_word.index(this_guess[idx]))\
                for idx in range(5) if this_guess[idx] in correct_word])
    return {
            "guesses-left": guesses_remaining,
            "correct-letter": right_spot,
            "ooo-letter":wrong_spot
            }


@app.route("/game/<int:game_id>", methods=["POST"])
async def play_game(game_id):
    db = await _get_db()
    guess_json = await request.get_json()
    guess = guess_json["guess"]
    game_query = select(td.games).where(td.games.c.gameid==game_id)
    game = await db.fetch_one(game_query)
    if game == None:
        return {"msg": "No game exists with this id"}, 404
    response = {"valid":True}
    valid_query = select(td.valid).where(td.valid.c.words == guess_json["guess"])
    valid_match = await db.fetch_one(valid_query)
    guess_num = game["guessnum"] + 1
    guesses_remaining = 6 - guess_num
    if game["gamewin"] or guesses_remaining < 0:
        return {"game-won": game["gamewin"], 
                "guesses-left": 6 - game["guessnum"]}, 200
    # Catch first pass type error
    print(valid_match)
    try:
        guesses = game["guesses"] + guess
    except TypeError:
        guesses = guess
    if guess == game.correctword:
        update_stmt = update(td.games).where(td.games.c.gameid == game_id)\
            .values(guessnum=guess_num, guesses=guesses, gamewin=True)
        response = {"correct": True, "guesses-left": guesses_remaining,
                "valid": True}
    elif valid_match != None:
        update_stmt = update(td.games).where(td.games.c.gameid == game_id)\
            .values(guessnum=guess_num, guesses=guesses)
        correct_word = list(game.correctword)
        guess_word = list(guess)
        right_spot = []
        for idx in range(5):
            if guess[idx] == correct_word[idx]:
                right_spot.append(correct_word.pop(idx))
                guess_word.pop(idx)
                correct_word.insert(idx,'')
                guess_word.insert(idx,',')
        wrong_spot = [correct_word.pop(correct_word.index(guess_word[idx]))\
                for idx in range(5) if guess_word[idx] in correct_word]
        response = {"correct": False, "guesses-left": guesses_remaining,
                "valid": True, "correct-letter": right_spot,
                "ooo-letter": wrong_spot}

    else:
        response = {"valid":False, "guesses-left":guesses_remaining}
        update_stmt = update(td.games).where(td.games.c.gameid == game_id)\
            .values(guessnum=guess_num, guesses=".....")
    await db.execute(update_stmt)
    return response, 200
