import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort, redirect
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request, validate_response

from http import HTTPStatus
import json
from sqlalchemy import select, insert, func
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

#User Authentication
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
    
    #Prints 401 if the username and password if not valid

    query = select(td.users).where(td.users.c.username == auth_d["uname"])\
            .where(td.users.c.password == auth_d["uname"])
    result = await db.fetch_one(query)
    if result is not None:
        return { "authenticated": True }, 200
    return "Incorrect username or password",  401,\
            {'WWW-Authenticate': "Basic <username>:<password>"}


# Using dynamic routing, makes more sense to me. Maybe needs to change.
@app.route("/game", methods=["GET"])
@validate_request(rd.FullGameRequest)
async def get_users_games():
    db = await _get_db()
    usr_json = await request.get_json()
    print(usr_json)
    try:
        user_id = int(usr_json["user-id"])
    except (KeyError, ValueError) as e:
        return 400

    query = select(games).where(games.userid == user_id)
    user_games = db.fetch_all(query)
    pass

@app.route("/game", methods=["POST"])
async def post_new_game():
    db = await _get_db()
    usr_json = await request.get_json()
    print(usr_json)
    try:
        user_id = int(usr_json["user-id"])
    except (KeyError, ValueError) as e:
        return 400
    # https://stackoverflow.com/a/33583008
    stmt = select(td.correct).order_by(func.random())

    to_guess = await db.fetch_one(stmt)
    print(to_guess)

#    await db.insert(games).values(gameid=game_id, userid=user_id,
#            correct_word=to_guess, guessnum=6)
    return {"word":to_guess}, 200

@app.route("/game/<int:game_id>", methods=["GET"])
async def get_game_status(game_id):
    db = await _get_db()
    query = select(games).where(games.gameid==game_id)
    game = await db.fetch_one(query)
    if game == None:
        return 400
    pass

@app.route("/game/<int:game_id>", methods=["POST"])
@validate_request(rd.GuessRequest)
async def play_game(game_id):
    db = await _get_db()

    query = select(games).where(games.gameid==game_id)
    game = await db.fetch_one(query)
    recvd = request.form
    if "guess" not in recvd.keys():
        return 400
    guess = recvd['guess']
    valid_query = "SELECT * FROM valid WHERE word = (:guess)"
    valid_match = db.execute(query=valid_query, value=guess)
    if valid_match == None:
        return 400
    if guess == game.correct:
        return redirect(Quart.url_for(f"game/{game_id}"), 302)
    else:
        return redirect(Quart.url_for(f"game/{game_id}"), 302)
