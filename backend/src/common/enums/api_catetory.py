from enum import StrEnum


class ApiCatetory(StrEnum):
    BACKOFFICE = "관리자 API"
    AUTH = "인증 API"
    USERS = "사용자 API"
    FILES = "파일 API"
