from spakky.domain.error import SpakkyDomainError


class FileNameAlreadyExistsError(SpakkyDomainError):
    message = "이미 존재하는 파일입니다."


class FileNameNotFoundError(SpakkyDomainError):
    message = "존재하지 않는 파일입니다."


class FileNameMustNotBeEmptyError(SpakkyDomainError):
    message = "파일 이름은 필수입니다."


class MediaTypeMustNotBeEmptyError(SpakkyDomainError):
    message = "파일 미디어 유형은 필수입니다."


class FileSizeMustNotBeEmptyError(SpakkyDomainError):
    message = "파일 크기는 필수입니다."
