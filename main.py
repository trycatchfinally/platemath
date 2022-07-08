import collections
import itertools
import math
import pickle
import pprint
from collections import defaultdict
from functools import lru_cache
from itertools import chain, combinations
from typing import Set, Tuple, Union, Dict, FrozenSet, Any, Iterable, List, Deque, Optional, Sequence

import tabulate

Numeric = Union[float, int]
Weight = Tuple[Numeric, int]
WeightSet = FrozenSet[Weight]

MAX_SEARCH_DEPTH = 10
TABLEFMT = "github"


def get_weights() -> WeightSet:
  # how many on one side of the bar
  my_weights: Dict[Numeric, int] = {
    5: 3,
    10: 1,
    15: 1,
    25: 1,
    35: 1,
    45: 1
  }
  return to_weight_set(my_weights)


def powerset(iterable: Iterable[Any]) -> Iterable[Any]:
  """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
  s = list(iterable)
  return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def totals(seq: Iterable[Weight]) -> Iterable[Numeric]:
  t: Numeric = 0
  for w, _id in seq:
    t += w
    yield t


def only_ascending(seq: Iterable[Numeric]) -> List[Numeric]:
  keep: List[Numeric] = []
  for s in seq:
    if not keep or s > keep[-1]:
      keep.append(s)
  return keep


def wsum(values: Iterable[Weight]) -> Numeric:
  t: Numeric = 0
  for w, _id in values:
    t += w
  return t


def print_powersets(weights: WeightSet) -> None:
  rows = []
  seen = set()
  options = defaultdict(list)
  for s in powerset(weights):
    ws = wsum(s)
    simpler = tuple(sorted(x[0] for x in s))
    if simpler not in seen:
      seen.add(simpler)
      rows.append((45 + 2 * ws, ws, simpler))
    options[ws].append(s)
  rows.sort()
  print(tabulate.tabulate(rows, headers=["total", "side", "weights"], tablefmt=TABLEFMT))
  print(len(rows))


def to_weight_set(my_weights: Dict[Numeric, int]) -> WeightSet:
  temp: Set[Tuple[Union[float, int], int]] = set()
  for weight, count in my_weights.items():
    for i in range(count):
      temp.add((weight, i))
  return frozenset(temp)


def is_valid(seq: List[Weight]) -> bool:
  stack = []
  for w, w_id in seq:
    if w > 0:
      stack.append((w, w_id))
    else:
      if stack[-1][0] == -w and stack[-1][1] == w_id:
        stack.pop()
      else:
        return False
  return True


def final_load(weights: List[Weight]) -> Tuple[Numeric, ...]:
  stack = []
  for w, w_id in weights:
    if w > 0:
      stack.append((w, w_id))
    else:
      if stack[-1][0] == -w and stack[-1][1] == w_id:
        stack.pop()
      else:
        assert False, stack
  return tuple(x[0] for x in stack)


def final_weights(weights: List[Weight]) -> Tuple[Weight, ...]:
  stack = []
  for w, w_id in weights:
    if w > 0:
      stack.append((w, w_id))
    else:
      if stack[-1][0] == -w and stack[-1][1] == w_id:
        stack.pop()
      else:
        assert False, stack
  return tuple(x for x in stack)


def myround(x: Numeric, base: Numeric = 5) -> Numeric:
  return base * round(x / base)


def main() -> None:
  max_weight_target = int(sum(w[0] for w in get_weights()) * 2 + 45)
  display = True
  results = {}
  for target in range(55, max_weight_target + 5, 5):
    s = compute_wrapper(target, display)
    if s:
      results[target] = s
      print(target)
      pprint.pprint(s)
  with open('output.pkl', 'wb') as output:
    pickle.dump(results, output)


def compute_wrapper(target: Numeric, display: bool = False) -> Dict[Numeric, Tuple[Any, Any]]:
  if target % 10 == 0:  # we'd need a 2.5
    sol = compute_for_size(target - 5, display)
    ret = dict()
    for size, (seq, steps) in sol.items():
      ls = list(steps)
      ls[-1] += 2.5
      ret[size] = seq + [(2.5, 0)], ls
    return ret
  return compute_for_size(target, display)


@lru_cache
def compute_for_size(target: Numeric, display: bool = False) -> Dict[Numeric, Tuple[Any, Any]]:
  bar = 45
  total = target - bar
  total_side = total / 2
  weights = get_weights()
  sorted_weights = list(sorted(set(x[0] for x in weights)))
  ideal_for_size = dict()
  best_for_size: Dict[Numeric, Tuple[Any, Any]] = dict()
  for warmup_sets in [0, 1, 2, 3]:
    solutions: Dict[Any, Any] = dict()

    jumps = warmup_sets + 1
    each_jump = total_side / jumps
    tsteps = []
    for i in range(1, jumps + 1):
      ss = myround(i * each_jump, sorted_weights[0])
      if int(ss) == math.floor(ss):
        ss = int(ss)
      tsteps.append(ss)
    # don't round the last one
    assert int(total_side) == math.floor(total_side)
    tsteps[-1] = int(total_side)
    tsteps = [x for x in tsteps if x != 0]
    ideal_for_size[len(tsteps)] = tuple(tsteps)

    def mse(xx: Tuple[Numeric, ...]) -> Numeric:
      ideal = ideal_for_size[len(xx)]
      return round(sum((xx[ii] - ideal[ii]) ** 2 for ii in range(len(xx))) / len(xx), 2)

    # offsets = [sorted_weights[0], sorted_weights[1]]
    offsets = [5]

    if display:
      print(warmup_sets, tsteps, total_side)
    for offset in offsets:
      for variant in loosen(tsteps, offset):
        tv = tuple(sorted(set(variant)))

        m5 = set(t % 5 for t in tv) - {0}
        if m5:
          assert m5 == {sorted_weights[0]}, (m5, weights, tv)

        if tv not in solutions:
          sol = run_search(tv, weights)
          if not sol:
            print('not solved: ', tv, "solutions so far: ", len(solutions))
            continue
          solutions[tv] = sol
    all_values = [v + (k, calc_avg_gap(k), max(deltas(k)), min(deltas(k)), mse(k)) for k, v in solutions.items() if v]
    all_values.sort()
    if display:
      print(tabulate.tabulate(all_values, headers=[
        "#", "t", "-", "center", "final", "sequence", "steps", "avg_gap", "max_gap", "min_gap", "mse"
      ], tablefmt=TABLEFMT))
    if all_values:
      best_for_size[warmup_sets] = (all_values[0][5], all_values[0][6])

  if display:
    pprint.pprint(best_for_size)
  return best_for_size


def calc_avg_gap(seq: Tuple[Any, ...]) -> Numeric:
  d = deltas(seq)
  return round(sum(d) / len(d), 2)


def run_search(tsteps: Sequence[Numeric], weights: WeightSet, display: bool = False) -> Optional[Tuple[Any, ...]]:
  total_side = tsteps[-1]
  assert len(set(tsteps)) == len(tsteps), tsteps
  assert 0 not in tsteps, tsteps
  search: Deque[Tuple[Tuple[Numeric, ...], List[Weight]]] = collections.deque()
  search.append((tuple(tsteps), []))
  seen: Set[Tuple[Numeric, ...]] = set()
  best_touch: Numeric = 2.0 * sum(w[0] for w in weights)
  all_steps = frozenset(tsteps)
  solutions = []
  while search:
    targets, current = search.popleft()
    seq = tuple(x[0] for x in current)
    if seq in seen:
      continue
    seen.add(seq)
    # costly: assert is_valid(current), current
    current_sum = wsum(current)
    assert current_sum <= total_side
    touches = sum(abs(x[0]) for x in current)
    if touches > best_touch:
      continue
    assert current_sum > 0 if current else True, current
    if current_sum == total_side:
      assert not targets, (current, targets)
      totals_hit = list(totals(current))
      relevant_totals = [t for t in totals_hit if t in all_steps]
      asc_rel = only_ascending(relevant_totals)
      if len(asc_rel) != len(all_steps):
        continue

      if touches <= best_touch:
        fl = final_load(current)
        cfl = centeredness(fl)
        removed = sum(x[0] for x in current if x[0] < 0)
        solutions.append((len(current), touches, removed, cfl, fl, current))
        best_touch = min(best_touch, touches)
        if display:
          key = tuple(sorted(x[0] for x in current))
          print(format(len(search), ","), touches, len(current), asc_rel, totals_hit, current, key)
          print(list(to_chunks(current, tsteps)), fl, cfl)
      continue

    if len(current) >= MAX_SEARCH_DEPTH:
      continue

    if targets[0]:
      assert current_sum < targets[0], (current_sum, targets, current)

    already_used = set(current)
    for uw, uid in already_used:
      opp = (-uw, uid)
      if uw > 0 and current_sum - uw > 0 and opp not in current:
        cand = current + [opp]
        if is_valid(cand):
          search.append((targets, cand))

    # only uses a weight once even if it's free: avail1 = (weights - already_used)
    avail2 = weights - set(final_weights(current))
    for w in avail2:
      next_w = current + [w]
      if current_sum + w[0] == targets[0]:
        # we've hit it, go to the next target
        search.append((targets[1:], next_w))
      elif current_sum + w[0] < targets[0]:
        # still haven't found what we're looking for
        search.append((targets, next_w))

  solutions.sort()
  if display:
    print(tabulate.tabulate(solutions[:10], tablefmt=TABLEFMT))
  if not solutions:
    return None
  return solutions[0]


def centeredness(vals: Iterable[Numeric]) -> Numeric:
  t: Numeric = 0
  for i, w in enumerate(vals, start=1):
    t += (i * w * math.sqrt(w))
  return round(t, 2)


def to_chunks(current: Sequence[Weight], steps: Sequence[Numeric]) -> Iterable[Tuple[Numeric, List[Numeric]]]:
  stepc: List[Numeric] = list(steps)
  stepc.sort()
  temp: List[Numeric] = []
  total: Numeric = 0
  for c, _id in current:
    total += c
    temp.append(c)
    if total == stepc[0]:
      yield stepc[0], temp
      temp = []
      stepc.pop(0)


def loosen(steps: List[Numeric], val: Numeric) -> List[Tuple[Numeric, ...]]:
  scopy: List[List[Numeric]] = [[] for _ in steps]
  scopy[-1] = [steps[-1]]
  for i, s in enumerate(steps):
    if i == len(steps) - 1: break
    scopy[i] = [s - val, s, s + val]

  return list(sorted(set(x for x in itertools.product(*scopy) if min(deltas(x)) >= val)))


def deltas(seq: Tuple[Any, ...]) -> Tuple[Numeric, ...]:
  d = [seq[0]]
  for i in range(1, len(seq)):
    d.append(seq[i] - seq[i - 1])
  return tuple(d)


if __name__ == '__main__':
  main()

  # See PyCharm help at https://www.jetbrains.com/help/pycharm/
