Phase 3 — Find halo centers for the merger BHs

Checks which BHs are the two BHs from the merger.
Gets the halo ID each merger BH belongs to.
If halo_id == 0, it means the BH is not assigned to an identified halo, so it records that and skips centering.
If the BH is inside a halo, it loads that halo.
Converts the snapshot to physical units.
Finds the halo center using Pynbody's ssc centering method.
Saves the snapshot ID, BH ID, halo ID, and halo center for each merger BH.
