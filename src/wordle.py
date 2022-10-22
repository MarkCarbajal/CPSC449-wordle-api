import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

from http import HTTPStatus
import json
import sqlalchemy
import table_declarations

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"../{__name__}.toml", toml.load)

##CONNECT TO DATABASE##
async def _connect_db():

    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


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
    all_words = await db.fetch_all("SELECT * FROM correct;")
    return list(map(dict, all_words))


@app.route("/register", methods=["POST"])
async def register():
    db = _get_db()
    pass


@app.route("/login", methods=["POST"])
async def login():
    db = _get_db()
    pass

# Using dynamic routing, makes more sense to me. Maybe needs to change.
@app.route("/game/<int:game_no>", methods=["GET", "POST"])
async def game(game_no):
    db = _get_db()
    query = "SELECT * FROM games WHERE id = (:game_no)"
    game = await db.execute(query=query, value=game_no)
    if game == None:
        return Quart.Response(status=HTTPStatus.METHOD_NOT_FOUND)
    if request.method == "POST":
        recvd = request.form
        if "guess" not in recvd.keys():
            return Quart.Response(status=HTTPStatus.BAD_REQUEST)
        guess = recvd['guess']
        valid_query = "SELECT * FROM valid WHERE word = (:guess)"
        valid_match = db.execute(query=valid_query, value=guess)
        if valid_match == None:
            return Quart.Response(status=HTTPStatus.BAD_REQUEST)
        if guess == game.correct:
            return Quart.Response(status=HTTPStatus.OK)
        else:
            return Quart.Response(status=HTTPStatus.OK)
    pass

@app.route("/game/new", methods=["POST"])
async def new_game():
    pass

@app.route("/user/<user_name>")
async def get_game(username):

    pass

