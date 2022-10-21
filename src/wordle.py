import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

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
    pass

@app.route("/game/new", methods=["POST"])
async def new_game():
    pass

@app.route("/user")
async def get_game():
    pass
