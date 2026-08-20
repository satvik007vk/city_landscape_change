from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": [("authorization", "REDACTED")]}


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    module_name = Path(request.module.__file__).stem
    return str(Path(__file__).parent / "cassettes" / module_name)
