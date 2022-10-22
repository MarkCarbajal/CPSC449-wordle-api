from dataclasses import dataclass
from typing import Optional

@dataclass
class AuthRequest:
    user_name: str
    password: str


@dataclass
class FullGameRequest:
    userID: int

@dataclass
class GuessRequest:
    userID: int
    guess: str

