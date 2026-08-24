Day 4: Functions

- def name(): sets up a function, but doesn't run it. You have to call it separately.
- Parameters are like blanks you fill in each time you call the function.
- print() inside a function just shows something on screen — it doesn't give you a value back. Use return for that.

What I practiced, step by step:
1. No parameters — path was hard-coded, function just printed the particle count
2. One parameter (path) — could reuse the function for different snapshots
3. Two parameters (path, threshold) — function returns "large" or "small" instead of printing
4. Ran it from the terminal using sys.argv — same pattern my BHmergers script uses (make_dict, below, match, track_BHs)

Watch out: reusing a function name overwrites the old one.

Next: Day 5 — lists and dictionaries. Ties into match['bh1'] and match['snapshots'] in my BHmergers script.
