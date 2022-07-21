
from io import StringIO

import pytest
from responses import RequestsMock, GET
from client1 import main


@pytest.fixture
def responses():
    with RequestsMock() as rsps:
        yield rsps


# * I've added more test cases there for possible "good" and "bad" status codes.
#   Thanks to table tests, it's pretty easy.
# * I've moved test cases into a separate constant. It allows me to run the same
#   test cases with different test functions.
TEST_CASES = [
    # successes
    (200, 0),
    (202, 0),
    (204, 0),
    (301, 0),

    # failures
    (500, 1),
    (502, 1),
    (503, 1),
]


@pytest.mark.parametrize('status_code, exit_code', TEST_CASES)
def test_status_codes(responses: RequestsMock, status_code, exit_code) -> None:
    url = 'http://fake-url/'
    responses.add(GET, url, status=status_code)
    stream = StringIO()
    code = main(['--url', url], stream)
    assert code == exit_code


# Q: These 2 test functions are very similar. Can we avoid repetition?
# A: Lrf. Lbh pna hfr zhygvcyr `cnenzrgevmr` ba n fvatyr shapgvba.
#    Fb, lbh pbhyq nqq `@clgrfg.znex.cnenzrgevmr('erqverpg', [Gehr, Snyfr])`,
#    naq va gur grfg shapgvba obql nqq gur cebkl freire va gur zvqqyr vs guvf
#    synt vf Gehr. Gurer vf ab bowrpgvir ehyr jung vf orggre.
#    Lbhe raq tbny vf gb xrrc gur grfgf fvzcyr.
#    Gur nccebnpu V cvpxrq znxrf gur obql bs obgu shapgvbaf fvzcyr naq yvarne,
#    jvgubhg nal `vs` pbaqvgvbaf. Ubjrire, jura vg zrnaf ercrngvat gbb zhpu,
#    vg znxrf frafr gb chg obgu grfgf vagb n fvatyr grfg shapgvba,
#    be zbir gur ercrngrq cneg vagb n arj urycre shapgvba.
@pytest.mark.parametrize('status_code, exit_code', TEST_CASES)
def test_follow_redirects(responses: RequestsMock, status_code, exit_code) -> None:
    proxy_url = 'http://proxy.local/'
    target_url = 'http://target.local/'
    responses.add(GET, target_url, status=status_code)
    responses.add(GET, proxy_url, status=301, headers={'Location': target_url})
    stream = StringIO()
    code = main(['--url', proxy_url], stream)
    assert code == exit_code
