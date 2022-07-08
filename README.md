# why?
Do you love lifting weights and HATE doing plate math? I certainly do. So, instead of trying to do math and percentages on the fly, let's pre-compute our warmup sets instead!

# how to

`pip install tabulate`, install pandoc for html rendering: https://pandoc.org/installing.html

if needed, change in main.py:

      # how many on one side of the bar
      my_weights: Dict[Numeric, int] = {
        5: 3,
        10: 1,
        15: 1,
        25: 1,
        35: 1,
        45: 1
      }

run main.py then o.cmd

# algorithm

the general idea is to evenly divide the jumps between 45 and the target weight and do a full search to see what
combinations of adds and removes touch those intermediate steps. also, do +/- 5 to the steps (15 -> 10, 15, 20) because
that's close enough and can sometimes result in a better path.

"better" (or "ranking") is done by:

1. the fewest # of moves
2. the lowest total weight touched (adds + removes)
3. the lowest amount of weight removed (slightly redundant)
4. the lowest "centeredness" to prefer heavier weights being closer to the center of the bar

(avg_gap, max_gap, min_gap, and mse are informational.) to some extent, this is just a personal preference. my goal is
to avoid thinking about it, so I just picked this as the "canonical" solution.

## example intermediate table for 155:

|   # |   t |   - |   center | final           | sequence                                             | steps        |   avg_gap |   max_gap |   min_gap |   mse |
|-----|-----|-----|----------|-----------------|------------------------------------------------------|--------------|-----------|-----------|-----------|-------|
|   4 |  55 |   0 |   380.78 | (25, 15, 10, 5) | [(25, 0), (15, 0), (10, 0), (5, 1)]                  | (25, 40, 55) |     18.33 |        25 |        15 | 16.67 |
|   4 |  55 |   0 |   407.25 | (25, 10, 15, 5) | [(25, 0), (10, 0), (15, 0), (5, 1)]                  | (25, 35, 55) |     18.33 |        25 |        10 |  8.33 |
|   4 |  55 |   0 |   447.68 | (15, 25, 10, 5) | [(15, 0), (25, 0), (10, 0), (5, 1)]                  | (15, 40, 55) |     18.33 |        25 |        15 | 16.67 |
|   4 |  55 |   0 |   448.14 | (25, 5, 15, 10) | [(25, 0), (5, 1), (15, 0), (10, 0)]                  | (25, 30, 55) |     18.33 |        25 |         5 | 16.67 |
|   4 |  55 |   0 |   654.88 | (15, 10, 5, 25) | [(15, 0), (10, 0), (5, 1), (25, 0)]                  | (15, 30, 55) |     18.33 |        25 |        15 | 16.67 |
|   4 |  55 |   0 |   675.32 | (15, 5, 10, 25) | [(15, 0), (5, 1), (10, 0), (25, 0)]                  | (20, 30, 55) |     18.33 |        25 |        10 |  8.33 |
|   5 |  85 | -15 |   599.59 | (5, 35, 15)     | [(5, 1), (15, 0), (-15, 0), (35, 0), (15, 0)]        | (20, 40, 55) |     18.33 |        20 |        15 |  8.33 |
|   6 |  65 |  -5 |   500.63 | (10, 25, 15, 5) | [(10, 0), (5, 1), (-5, 1), (25, 0), (15, 0), (5, 1)] | (15, 35, 55) |     18.33 |        20 |        15 |  8.33 |
|   6 |  65 |  -5 |   675.32 | (15, 5, 10, 25) | [(15, 0), (5, 1), (10, 0), (5, 0), (-5, 0), (25, 0)] | (20, 35, 55) |     18.33 |        20 |        15 |  0    |

# hacks

bar weight is hardcoded to 45 and modifying to use kilograms is left as an exercise for the reader.

130 is modeled as the same solutions as 125 + adding a 2.5 at the end of the path: this reduces the search space and
speeds things up considerably. (see `compute_wrapper` in `main.py`.) modifying to support 131, 132, 132.5, etc. is also
left as an exercise for the reader.

it'd be really cool to color-code the output in renderer.py...

# files

* main.py - main program, generates output.pkl (takes ~3 minutes)
    * tests.py - some unit tests
* renderer.py - input is output.pkl, displays markdown to the console
* o.cmd - runs renderer.py and then pandoc to generate html
* extra.html - extra CSS to align the HTML table more nicely and make printing easier
* output.html - generated output
* output.pdf - chrome print output (1 weight per page)
* output4.pdf - chrome print output (4 weights per page)

# example renderer.py output:

    # 335
    
    ## 1 warmup set
    
    | set   |   total |   side | add                 |
    |-------|---------|--------|---------------------|
    | e     |      45 |        |                     |
    | A     |     185 |     70 | 45, 25              |
    | W     |     335 |    145 | 35, 15, 10, 5, 5, 5 |
    
    ## 2 warmup sets
    
    | set   |   total |   side | add             |
    |-------|---------|--------|-----------------|
    | e     |      45 |        |                 |
    | A     |     135 |     45 | 45              |
    | B     |     235 |     95 | 35, 15          |
    | W     |     335 |    145 | 25, 10, 5, 5, 5 |
    
    ## 3 warmup sets
    
    | set   |   total |   side | add         |
    |-------|---------|--------|-------------|
    | e     |      45 |        |             |
    | A     |     115 |     35 | 35          |
    | B     |     185 |     70 | 25, 10      |
    | C     |     275 |    115 | 45          |
    | W     |     335 |    145 | 15, 5, 5, 5 |

# example html

# 335

## 1 warmup set

| set   |   total |   side | add                 |
|-------|---------|--------|---------------------|
| e     |      45 |        |                     |
| A     |     185 |     70 | 45, 25              |
| W     |     335 |    145 | 35, 15, 10, 5, 5, 5 |

## 2 warmup sets

| set   |   total |   side | add             |
|-------|---------|--------|-----------------|
| e     |      45 |        |                 |
| A     |     135 |     45 | 45              |
| B     |     235 |     95 | 35, 15          |
| W     |     335 |    145 | 25, 10, 5, 5, 5 |

## 3 warmup sets

| set   |   total |   side | add         |
|-------|---------|--------|-------------|
| e     |      45 |        |             |
| A     |     115 |     35 | 35          |
| B     |     185 |     70 | 25, 10      |
| C     |     275 |    115 | 45          |
| W     |     335 |    145 | 15, 5, 5, 5 |
