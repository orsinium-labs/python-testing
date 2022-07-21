from io import StringIO
import os

import pytest
from client1 import main


# Q: why to specify the default value?
# A: V jnag gur glcr bs gur inevnoyr gb or `fge` vafgrnq bs `fge | Abar`.
#    Gung jnl, zlcl jba'g pbzcynva nobhg vg jura V cnff vg vagb `znva`.
GOOD_URL = os.environ.get('GOOD_URL', '')
BAD_URL = os.environ.get('BAD_URL', '')


# Q: why to skip?
# A: V jnag gurfr grfg gb or fxvccrq vs gurer vf ab freire ninvynoyr va gur raivebazrag.
#    Vg jvyy uryc hf ba gur arkg fgntr, jura jr nqq havg grfgf.
@pytest.mark.skipif(not GOOD_URL, reason="no GOOD_URL")
# Q: why to specify the return value for tests?
# A: Ol qrsnhyg, zlcl jba'g glcr purpx shapgvbaf jvgubhg nal glcrf naabgngrq.
#    Naq V jnag grfgf gb or glcr-purpxrq gbb. N orggre bcgvba jbhyq or gb
#    nqq n zlcl pbasvt naq sbepr vg gb glcr purpx nyy shapgvbaf.
def test_good() -> None:
    stream = StringIO()
    code = main(['--url', GOOD_URL], stream)
    assert code == 0


@pytest.mark.skipif(not BAD_URL, reason="no BAD_URL")
def test_bad() -> None:
    stream = StringIO()
    code = main(['--url', BAD_URL], stream)
    assert code == 1
