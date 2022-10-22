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

#games = sqlalchemy.Table(
#        "games",
#        metadata,
#        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
#        sqlalchemy.Column(
