from spakky.domain.error import SpakkyDomainError


class AuthenticationFailedError(SpakkyDomainError):
    message = "아이디 또는 비밀번호가 잘못되었습니다."


class InvalidPasswordResetTokenError(SpakkyDomainError):
    message = "잘못된 비밀번호 재설정 토큰입니다."
