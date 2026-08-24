import pynbody as pn 
import glob
import sys
import numpy as np
import os 


# phase 1

mergers_data = np.loadtxt(glob.glob('*.BHmergers')[0])

# making a dictionary: z-values to snapshot filename
def make_dict():
    snapshot_dict = {}

    # going through every snapshot
    for snap_file in sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]')):
        snap = pn.load(snap_file)
        snap_id = snap_file.split('.')[-1] # -1 to get the last piece of the split 
        z = snap.properties['z'] 
        snapshot_dict[z] = snap_id #storing: z is the key, snapshot ID is the value

    return snapshot_dict


# given a target z, return every snapshot with a smaller z
def get_snaps_below(target, snapshot_dict):
    sorted_keys = sorted(snapshot_dict.keys())
    snapshot_ids = []

    for z_value in sorted_keys:
        if z_value < target:
            snapshot_ids.append(snapshot_dict[z_value])

    return snapshot_ids 

# phase 2
# go through real mergers and find the snapshots that come after them
def match_mergers():
    snapshot_dict = make_dict()
    matched_mergers = []

    for row in mergers_data:
        if row[6] < 0: # skipping fake mergers
            continue

        bh1, bh2 = int(row[0]), int(row[1]) 
        merger_z = 1 / row[7] - 1 # scale factor to z
        snapshot_ids = get_snaps_below(merger_z, snapshot_dict) # snapshots after the merger

        matched_mergers.append({'bh1': bh1, 'bh2': bh2, 'merger_z': merger_z, 'snapshots': snapshot_ids})

    return matched_mergers


# phase 3
# finding all BHs in a snapshot
def find_BH(snapshot):
    BH_filter = pn.filt.LowPass('tform', 0.0) 
    BHs = snapshot.stars[BH_filter]
    return BHs

# finding the center of one halo
def find_halo_center(snapshot, halo_id):
    halos = snapshot.halos() # loading the halos
    snapshot.physical_units() 
    halo_center = pn.analysis.halo.center(halos[int(halo_id)], mode='ssc', retcen=True) # finding the halo center
    return halo_center


# tracking the merger BHs, their halos, and halo centers in one pass per snapshot
def track_BHs_and_centers(match):
    results = []

    print("merger:", match['bh1'], match['bh2'], "z =", match['merger_z'])

    for snapshot_id in match['snapshots']: 
        snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snapshot_id
        amiga_file = snapshot_file + '.amiga.grp'

        if not os.path.exists(amiga_file): # skipping snapshots without amiga.grp
            continue

        snapshot = pn.load(snapshot_file)
        BHs = find_BH(snapshot) # find the BHs in the loaded snap

        # checking if each BH is one of the 2 mergers, if not, ignore
        for i in range(len(BHs)): 
            bh_id = BHs['iord'][i] # BH ID indexing
            halo_id = BHs['amiga.grp'][i] # halo the BH belongs to

            if bh_id != match['bh1'] and bh_id != match['bh2']:
                continue

            print("BH:", bh_id, "halo:", halo_id)

            if halo_id == 0: # BH is not in an identified halo, just record it, don't call centering function
                results.append({'snapshot_id': snapshot_id, 'bh_id': bh_id, 'halo_id': halo_id, 'halo_center': None})
                continue

            halo_center = find_halo_center(snapshot, halo_id) # anything above halo 0, trigger finc_halo_center 
            print("BH:", bh_id, "halo:", halo_id, "center:", halo_center)

            results.append({'snapshot_id': snapshot_id, 'bh_id': bh_id, 'halo_id': halo_id, 'halo_center': halo_center})

    return results


# CMDS
command = sys.argv[1] if len(sys.argv) > 1 else None


if command == 'make_dict':
    snapshot_dict = make_dict()

    for z, snap_id in snapshot_dict.items():
        print(f"{snap_id}: z = {z:.3f}")


elif command == 'below':
    target = float(sys.argv[2])
    snapshot_dict = make_dict()
    snapshot_ids = get_snaps_below(target, snapshot_dict)
    print(snapshot_ids)


elif command == 'match':
    for match in match_mergers():
        print(match)


elif command == "track_BHs":
    for match in match_mergers():
        track_BHs_and_centers(match)


else:
    print("For the z-to-filename dictionary, use: make_dict")
    print("For the snapshots below a target z, use: below <target_z>")
    print("For matching mergers to snapshots below their z, use: match")
    print("To track BHs, their halos, and halo centers, use: track")
