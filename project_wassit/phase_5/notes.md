Phase 5 - BH displacement after merger

Goal: Measure how far a BH is from its pre-merger host halo center.

What it does:

- Manually selects a merger.
- Finds the merger time from .BHmergers file.
- Gets the pre-merger host halo center.
- Finds the BH position in .BlackHoles closest to the merger time.
- Converts the BH coordinates to physical kpc.
- Calculates dx, dy, and dz between the BH and halo center.
- Calculates the total 3D displacement:

$$
r = \sqrt{dx^2 + dy^2 + dz^2}
$$

Current issue: The BH position is taken from the closest available time in `.BlackHoles`, so it may not exactly match the merger time.
