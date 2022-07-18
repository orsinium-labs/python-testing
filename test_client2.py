
from io import StringIO
import os

import pytest
from responses import RequestsMock, GET
from client1 import main

# I've omitted the previous integration tests in this file
# to reduce duplication, but keep in mind that they should stay.
# My implementation skips integraion tests if URLs aren't provided,
# so CI won't fail if we leave them.
...


# https://github.com/getsentry/responses#responses-as-a-pytest-fixture
@pytest.fixture
def responses():
    with RequestsMock() as rsps:
        yield rsps


@pytest.mark.parametrize('status_code, exit_code', [
    (200, 0),
    (500, 1),
])
# Q: Why I annotated `responses` here?
# A: Rira vs glcr purpxvat qbrfa'g znxr frafr sbe grfgf,
#    lbh fgvyy jnag gb naabgngr fbzr glcrf sbe lbhe VQR.
#    Gung jnl, lbh pna unir n avpr nhgbpbzcyrgr naq frznagvp flagnk uvtuyvtugvat.
def test_status_codes(responses: RequestsMock, status_code, exit_code) -> None:
    url = 'http://fake-url/'
    responses.add(GET, url, status=status_code)
    stream = StringIO()
    code = main(['--url', url], stream)
    assert code == exit_code
