from spakky.domain.error import SpakkyDomainError


class AuthenticationFailedError(SpakkyDomainError):
    message = "아이디 또는 비밀번호가 잘못되었습니다."


class InvalidPasswordResetTokenError(SpakkyDomainError):
    message = "잘못된 비밀번호 재설정 토큰입니다."


class UsernameAlreadyExistsError(SpakkyDomainError):
    message = "이미 사용중인 아이디입니다."


class PhoneNumberAlreadyExistsError(SpakkyDomainError):
    message = "이미 사용중인 휴대폰 번호입니다."


class CannotRegisterWithoutAgreementError(SpakkyDomainError):
    message = "약관 동의를 체크해주세요."
