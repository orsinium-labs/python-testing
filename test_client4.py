from io import StringIO
import os
from pathlib import Path

import pytest
from vcr import VCR
from client1 import main


GOOD_URL = os.environ.get('GOOD_URL', '')
BAD_URL = os.environ.get('BAD_URL', '')
ROOT = Path(__file__).parent


@pytest.fixture
def record_resp(request: pytest.FixtureRequest):
    path = ROOT / '.cassettes' / f'{request.node.name}.yaml'
    vcr = VCR(serializer='yaml')
    with vcr.use_cassette(str(path)):
        yield


def test_good(record_resp) -> None:
    stream = StringIO()
    code = main(['--url', GOOD_URL], stream)
    assert code == 0


def test_bad(record_resp) -> None:
    stream = StringIO()
    code = main(['--url', BAD_URL], stream)
    assert code == 1
