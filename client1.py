# Q: what is this __future__ import?
from __future__ import annotations
from argparse import ArgumentParser
import sys
from typing import NoReturn, TextIO

import requests


# Q: why to require argv and stream as arguments?
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
# Q: Why entrypoint is a function?
#    Why not to put it directly into the block below?
def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:], sys.stdout))


# Q: what is this condition? Why is it here?
if __name__ == '__main__':
    entrypoint()
