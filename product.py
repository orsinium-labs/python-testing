from __future__ import annotations
from datetime import timedelta
import deal
import hypothesis


@deal.pure
@deal.post(lambda r: r >= 1)
@deal.ensure(lambda _: _.result >= max(_.numbers, default=1))
@deal.example(lambda: prod([]) == 1)
@deal.example(lambda: prod([2, 3, -4]) == 6)
def prod(numbers: list[int]) -> int:
    result = 1
    for n in numbers:
        if n > 0:
            result *= n
    return result


@deal.cases(
    prod,
    # our implementation is too slow, so we need to increase the timeout
    settings=hypothesis.settings(
        deadline=timedelta(seconds=1),
    ),
)
def test_prod(case):
    case()
