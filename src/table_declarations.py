import sqlalchemy

metadata = sqlalchemy.MetaData()

valid = sqlalchemy.Table(
        "valid",
        metadata,
        sqlalchemy.Column("words", sqlalchemy.String(length=5)),
)

correct = sqlalchemy.Table(
        "correct",
        metadata,
        sqlalchemy.Column("words", sqlalchemy.String(length=5)),
)

users = sqlalchemy.Table(
        "users",
        metadata,
        sqlalchemy.Column("userid", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("username", sqlalchemy.String),
        sqlalchemy.Column("password", sqlalchemy.String),
)

games = sqlalchemy.Table(
        "games",
        metadata,
        sqlalchemy.Column("gameid", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("userid", sqlalchemy.Integer),
        sqlalchemy.Column("correctword", sqlalchemy.String(length=5)),
        sqlalchemy.Column("guesses", sqlalchemy.String(length=30)),
        sqlalchemy.Column("gamewin", sqlalchemy.Boolean),
        sqlalchemy.Column("guessnum", sqlalchemy.Integer),
)

