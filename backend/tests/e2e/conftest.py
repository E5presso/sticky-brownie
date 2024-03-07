from typing import Any, Generator

import pytest
from fastapi import FastAPI

from main import app


@pytest.fixture(name="app", scope="session")
def get_app_fixture() -> Generator[FastAPI, Any, None]:
    yield app
