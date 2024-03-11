from spakky.domain.error import SpakkyDomainError


class FileNameAlreadyExistsError(SpakkyDomainError):
    message = "이미 해당 이름의 파일이 존재합니다."


class FileNameNotFoundError(SpakkyDomainError):
    message = "존재하지 않는 파일입니다."


class FileNameMustNotBeEmptyError(SpakkyDomainError):
    message = "파일 이름은 필수입니다."


class MediaTypeMustNotBeEmptyError(SpakkyDomainError):
    message = "파일 미디어 유형은 필수입니다."
