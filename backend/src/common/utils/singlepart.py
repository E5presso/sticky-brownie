from copy import deepcopy
from typing import AsyncGenerator
from dataclasses import dataclass

from multipart.multipart import parse_options_header


@dataclass
class FileInfo:
    name: str | None
    filename: str | None
    content_type: str | None


class AsyncSinglePartStream:
    start_header: bytes
    end_header: bytes
    end_file: bytes
    __stream: AsyncGenerator[bytes, None]
    __buffer: bytearray
    __file_info: FileInfo | None

    def __init__(self, boundary: bytes, stream: AsyncGenerator[bytes, None]) -> None:
        self.start_header = b"--" + boundary + b"\r\n"
        self.end_header = b"\r\n\r\n"
        self.end_file = b"\r\n--" + boundary + b"--\r\n"
        self.__stream = stream
        self.__buffer = bytearray()
        self.__file_info = None

    def __parse_file_info(self, header: str) -> FileInfo:
        header = header.replace("\r\n", "; ").replace(": ", "=")
        _, params = parse_options_header(header)
        encoded: dict[str, str] = {
            k.decode().lower(): v.decode() for k, v in params.items()
        }
        return FileInfo(
            name=encoded.get("name"),
            filename=encoded.get("filename"),
            content_type=encoded.get("content-type"),
        )

    async def get_file_info(self) -> FileInfo:
        if self.__file_info is not None:
            return self.__file_info
        chunk: bytes = await anext(self.__stream)
        header_start: int = chunk.find(self.start_header)
        header_end: int = chunk.find(self.end_header, header_start)
        self.__buffer.extend(chunk[header_end + len(self.end_header) :])
        header: str = chunk[header_start + len(self.start_header) : header_end].decode()
        self.__file_info = self.__parse_file_info(header)
        return self.__file_info

    async def stream(self) -> AsyncGenerator[bytes, None]:
        while True:
            if len(self.__buffer) > 0:
                yield bytes(deepcopy(self.__buffer))
                self.__buffer.clear()
                continue
            try:
                chunk: bytes = await anext(self.__stream)
            except StopAsyncIteration:
                break
            if (header_start := chunk.find(self.start_header)) > -1:
                if (header_end := chunk.find(self.end_header, header_start)) > -1:
                    header = chunk[header_start + len(self.start_header) : header_end]
                    self.__file_info = self.__parse_file_info(header.decode())
                    yield chunk[header_end + len(self.end_header) :]
                    continue
            if (end_boundary := chunk.find(self.end_file)) > -1:
                yield chunk[:end_boundary]
                break
            yield chunk
