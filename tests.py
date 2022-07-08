import pprint

import pytest
from main import *


def test_centers():
  assert True, (centeredness((15, 5, 35, 5)), centeredness((5, 35, 5, 15)))
  assert centeredness([15, 45]) == 661.83
  assert centeredness([45, 15]) == 418.06
  assert centeredness([5, 35, 10, 5, 5]) == 620.8
  assert centeredness([35, 5, 10, 5, 5]) == 424.91


def test_load():
  assert final_load([(15, 0), (5, 1), (-5, 1), (25, 0), (5, 0), (5, 2), (10, 0)]) == (15, 25, 5, 5, 10)


def test_valid():
  assert not is_valid([(15, 0), (5, 1), (25, 0), (-5, 1), (-25, 0), (45, 0)])
  assert is_valid([(15, 0), (5, 1), (25, 0), (-25, 0), (-5, 1), (45, 0)])
  assert is_valid([(5, 1), (15, 0), (10, 0), (5, 0), (5, 2), (-5, 2), (25, 0)])
  assert not is_valid([(5, 1), (15, 0), (10, 0), (5, 0), (5, 2), (-5, 1), (25, 0)])


def test_asc():
  assert only_ascending([1, 2, 1, 3, 1, 2, 4]) == [1, 2, 3, 4]


def test_chunks():
  tx = list(to_chunks([(15, 0), (5, 1), (-5, 1), (25, 0), (-25, 0), (45, 0)], [20, 40, 60]))
  assert tx == [(20, [15, 5]), (40, [-5, 25]), (60, [-25, 45])], tx


def test_delta_loosen():
  assert deltas((10, 25, 40, 60)) == (10, 15, 15, 20)
  assert loosen([15, 30, 45], 5) == [(10, 25, 45), (10, 30, 45), (10, 35, 45), (15, 25, 45), (15, 30, 45), (15, 35, 45), (20, 25, 45), (20, 30, 45),
                                     (20, 35, 45)]
  assert loosen([15, 30, 45], 0) == [(15, 30, 45)]


def test_compute_available():
  weights = {(5, 1), (2.5, 0), (2.5, 1), (5, 0)}
  current = [(5, 1), (2.5, 0), (2.5, 1), (5, 0), (-5, 0)]
  avail1 = weights - set(current)
  avail2 = weights - set(final_weights(current))
  assert avail1 == set()
  assert avail2 == {(5, 0)}


def test_avg_gap():
  c = calc_avg_gap((10.0, 35.0, 50.0, 60.0))
  assert c == 15


def test_weight_max():
  assert sum(w[0] for w in get_weights()) * 2 + 45 == 335


def test_powersets():
  print()
  print_powersets(get_weights())


def test_run():
  w = frozenset({(25, 0), (45, 0), (5, 1), (35, 0), (15, 0), (10, 0), (5, 0), (5, 2)})
  steps = [20, 40, 60]
  x = run_search(steps, w)
  final = x[-2]  # type: ignore
  seq = x[-1]  # type: ignore
  assert final == (5, 35, 15, 5)
  assert seq == [(5, 1), (15, 0), (-15, 0), (35, 0), (15, 0), (5, 0)]


def test_chunks2():
  seq = [(35, 0), (25, 0), (15, 0), (10, 0), (5, 0)]
  steps = (35, 60, 90)
  x = list(to_chunks(seq, steps))
  assert x == [(35, [35]), (60, [25]), (90, [15, 10, 5])]


if __name__ == '__main__':
  pytest.main()
