# Phase 6 - Interpolating the halo center

**Goal:** Measure how far the BH is from its moving host halo center over time.

### What it does:

- Reads the BH position history from `.BlackHoles`.
- Sorts the BH positions by scale factor `a`.
- Converts BH coordinates to physical kpc.
- Finds the halo center at each snapshot.
- Uses PCHIP interpolation to estimate the halo center between snapshots.
- Calculates the difference between the BH and halo center:

\[
dx = x_{\rm BH} - x_{\rm halo}
\]

\[
dy = y_{\rm BH} - y_{\rm halo}
\]

\[
dz = z_{\rm BH} - z_{\rm halo}
\]

- Calculates the total 3D separation:

\[
r = \sqrt{dx^2 + dy^2 + dz^2}
\]

- Checks which halo the BH is in at each snapshot.
- Compares the BH separation with the halo `Rvir`.
- Plots `r`, `dx`, `dy`, and `dz` over time.

**Why interpolate?**  
BH positions are saved more often than halo centers, so interpolation fills in the halo position between snapshots.

**Current issue:**  
For now, this is tested on one merger and a limited number of snapshots.