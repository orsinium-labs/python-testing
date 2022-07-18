
from io import StringIO
import os

import pytest
from client1 import main


# Q: why to specify the default value?
GOOD_URL = os.environ.get('GOOD_URL', '')
BAD_URL = os.environ.get('BAD_URL', '')


# Q: why to skip?
@pytest.mark.skipif(not GOOD_URL, reason="no GOOD_URL")
# Q: why to specify the return value for tests?
def test_good() -> None:
    stream = StringIO()
    code = main(['--url', GOOD_URL], stream)
    assert code == 0


@pytest.mark.skipif(not BAD_URL, reason="no BAD_URL")
def test_bad() -> None:
    stream = StringIO()
    code = main(['--url', BAD_URL], stream)
    assert code == 1
