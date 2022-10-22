import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort, redirect
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

from http import HTTPStatus
import json
from sqlalchemy import select, func
import table_declarations as td
from typing import Optional

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"../{__name__}.toml", toml.load)

@dataclasses.dataclass
class Users:
    username:str
    password:str

@dataclasses.dataclass
class Games:
    userid: int
    gameid: int
    correctword: str
    validword: str
    gamewin: bool
    guessnum: int

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


@app.route("/register", methods=["POST"])
async def register():
    db = await _get_db()
    pass


@app.route("/login", methods=["POST"])
async def login():
    db = await _get_db()
    pass

# Using dynamic routing, makes more sense to me. Maybe needs to change.
@app.route("/game", methods=["GET"])
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
    pass

@app.route("/game/<int:game_id>", methods=["GET"])
async def get_game_status(game_id):
    db = await _get_db()
    query = select(games).where(games.gameid==game_id)
    game = await db.fetch_one(query)
    if game == None:
        return 400
    pass

@app.route("/game/<int:game_id>", methods=["POST"])
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

