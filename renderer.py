import pickle
import pprint
import math
from typing import Sequence, Any, Union

import tabulate

from main import to_chunks


def f(vals: Sequence[Any]) -> str:
  return ", ".join(str(v) for v in vals)


def fix(x: Union[float, int]) -> Union[float, int]:
  if x == math.floor(x):
    return int(x)
  return x


def main() -> None:
  solutions = pickle.load(open('output.pkl', 'rb'))
  # pprint.pprint(solutions)

  for weight, table in solutions.items():
    print("# ", weight)  # , " (each side = ", table[0][1][0], ")")
    for i, (seq, steps) in table.items():
      if weight < 65 and i == 1:
        print("## full load")
      elif i == 0:
        continue
      else:
        print("## ", i, "warmup set" if i == 1 else "warmup sets")
      chunks = list(to_chunks(seq, steps))
      rows = []
      if len(table) > 1:
        # None so tabulate type inference works
        rows.append(["e", 45, None, None])
      for xi, (t, s2) in enumerate(chunks, start=0):
        rows.append([chr(ord('A') + xi), 45 + 2 * t, fix(t), f(s2)])
      rows[-1][0] = "W"
      print(tabulate.tabulate(rows, headers=["set", "total", "side", "add"], tablefmt="github"))
    print()


if __name__ == '__main__':
  main()
