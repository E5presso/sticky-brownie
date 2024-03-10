from enum import StrEnum, auto


class UserStatus(StrEnum):
    GREEN = auto()
    WARNED = auto()
    BANNED = auto()
    DORMANT = auto()
