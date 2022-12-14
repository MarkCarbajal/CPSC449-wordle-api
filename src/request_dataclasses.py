from dataclasses import dataclass
from typing import Optional

@dataclass
class AuthRequest:
    username: str
    password: str


@dataclass
class FullGameRequest:
    userID: int

@dataclass
class GuessRequest:
    userID: int
    guess: str

