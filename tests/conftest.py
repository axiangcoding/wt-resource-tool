import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session")
def repo_path():
    load_dotenv()
    path = os.getenv("DATAMINE_REPO_PATH")
    if not path:
        raise ValueError("Environment variable DATAMINE_REPO_PATH is not set.")
    return path
