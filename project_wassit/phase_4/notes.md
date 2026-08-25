Phase 4 - Halo matching around BH mergers

Goal:
Find the host halo of bh1 immediately before and after each merger.

What it does:
- Finds the closest pre-merger snapshot.
- Finds the closest post-merger snapshot.
- Loads BH particles.
- Uses iord to identify bh1.
- Uses amiga.grp to get the host halo ID.
- Includes a shrinking-sphere halo center function.

Current issue:
Some snapshots have a .iord file, but Pynbody does not always load it as snapshot['iord'], causing KeyError: 'iord'.

Will talk to Jillian about this.
