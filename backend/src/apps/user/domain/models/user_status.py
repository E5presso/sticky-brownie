from enum import StrEnum


class UserStatus(StrEnum):
    GREEN = "GREEN"
    WARNED = "WARNED"
    BANNED = "BANNED"
    DORMANT = "DORMANT"
