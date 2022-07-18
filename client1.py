# Q: what is this __future__ import?
from __future__ import annotations
from argparse import ArgumentParser
import sys
from typing import NoReturn, TextIO

import requests


# Q: why to require argv and stream as arguments?
# A: Gung jnl, jr pna grfg bhe pbqr jvgubhg zbpxvat nalguvat be hfvat fhocebprff.
#    Lbh'yy frr jura jr jevgr fbzr grfgf.
def main(argv: list[str], stream: TextIO) -> int:
    parser = ArgumentParser()
    parser.add_argument('--url', required=True)
    args = parser.parse_args(argv)

    resp = requests.get(args.url)
    if resp.ok:
        print('ok', file=stream)
        return 0
    else:
        print(f'unexpected status code: {resp.status_code}', file=stream)
        return 1


# Q: what is NoReturn? Why not None?
# A: AbErghea vf hfrq jura gur shapgvba arire ergheaf nalguvat.
#    Vg rvgure ehaf sberire be envfrf na rkprcgvba.
#    Va bhe pnfr, vg nyjnlf envfrf FlfgrzRkvg.
#
# Q: Why entrypoint is a function?
#    Why not to put it directly into the block below?
# A: Lbh znl jnag gb cebivqr __znva__.cl be frghcgbbyf ragelcbvag.
#    Naq gurl nyy jvyy erhfr guvf pbqr. Jr pnyy vg bayl va bar cynpr va guvf rknzcyr,
#    ohg va erny jbeyq lbh bsgra jnag gb pnyy vg sebz zhygvcyr cynprf.
def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:], sys.stdout))


# Q: what is this condition? Why is it here?
# A: Vg jvyy or rkrphgrq bayl jura jr qverpgyl pnyy gur fpevcg.
#    V jvyy or fxvccrq vs jr vzcbeg vg nf n zbqhyr. Sbe rknzcyr, sebz grfgf.
if __name__ == '__main__':
    entrypoint()
