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
        snap_id = snap_file.split('.')[-1]  # getting the last part of the filename
        z = snap.properties['z']
        snapshot_dict[z] = snap_id  # z is the key and snapshot ID is the value

    return snapshot_dict


# getting snapshots belo merger z; given a target z, return every snapshot with a smaller z
def get_snaps_below(target, snapshot_dict):
    sorted_keys = sorted(snapshot_dict.keys()) # the sorted z -> snap keys and values 
    snapshot_ids = []

    for z_value in sorted_keys:
        if z_value < target:
            snapshot_ids.append(snapshot_dict[z_value])

    return snapshot_ids


# getting the closest snapshot before the merger
def get_snap_before(target, snapshot_dict):
    sorted_keys = sorted(snapshot_dict.keys())

    for z_value in sorted_keys:
        if z_value > target: # one snap above the target snap
            return snapshot_dict[z_value]

    return None


# phase 2

# go through real mergers and match them with snapshots
def match_mergers():

    snapshot_dict = make_dict()
    matched_mergers = []

    for row in mergers_data:

        if row[6] < 0:
            continue

        bh1 = int(row[0])
        bh2 = int(row[1])

        # converting scale factor to redshift
        merger_z = 1 / row[7] - 1

        # snapshots after the merger
        snapshot_ids = get_snaps_below(merger_z, snapshot_dict)

        # closest snapshot after the merger
        if len(snapshot_ids) > 0: # if list is not empty
            merger_snapshot = snapshot_ids[-1] # grap the last snapshot (-1)
        else:
            merger_snapshot = None # if no snapshot, set it = none 

        # closest snapshot before the merger
        pre_merger_snapshot = get_snap_before(merger_z, snapshot_dict)

        matched_mergers.append({'bh1': bh1, 'bh2': bh2, 'merger_z': merger_z, 'pre_merger_snapshot': pre_merger_snapshot, 'merger_snapshot': merger_snapshot, 'snapshots': snapshot_ids})

    return matched_mergers


# phase 3

# finding all BHs in a snapshot
def find_BH(snapshot):
    BH_filter = pn.filt.LowPass('tform', 0.0)
    BHs = snapshot.stars[BH_filter]

    return BHs


# finding the coordinates of the center of one halo
def find_halo_center(snapshot, halo_id):
    halos = snapshot.halos()
    snapshot.physical_units()

    # using PN's Shrinking Sphere Center algorithm (ssc)
    # halo_id is just an input, it assumes it would found later, no specific halos 
    halo_center = pn.analysis.halo.center(halos[int(halo_id)], mode='ssc', retcen=True)

    return halo_center


# load the BHs from the pre-merger snapshot
#def load_pre_merger_BHs(snapshot_id):
 #   snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snapshot_id
  #  amiga_file = snapshot_file + '.amiga.grp'

    # skipping snapshots that don't have amiga files yet 
   # if not os.path.exists(amiga_file): 
    #    print("no amiga.grp for snapshot:", snapshot_id)
     #   return None, None

    #snapshot = pn.load(snapshot_file)
    #BHs = find_BH(snapshot)

   # if 'iord' not in BHs.loadable_keys() and 'iord' not in BHs.keys():
    #    print("no iord found in snapshot:", snapshot_id)
     #   return None, None

   # return snapshot, BHs

def load_pre_merger_BHs(snapshot_id):

    snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snapshot_id
    amiga_file = snapshot_file + '.amiga.grp'

    if not os.path.exists(amiga_file):
        print("no amiga.grp for snapshot:", snapshot_id)
        return None, None

    snapshot = pn.load(snapshot_file)

    # explicitly load iord
    try:
        snapshot['iord']
    except KeyError:
        print("no iord found in snapshot:", snapshot_id)
        return None, None

    BHs = find_BH(snapshot)

    return snapshot, BHs

# finding the host halo of bh1 right before the merger

# finding the host halo of bh1 before and after the merger
def find_remnant_pre_merger_halo(match):

    snapshot_id = match['pre_merger_snapshot']
    merger_snapshot = match['merger_snapshot']
    merger_z = match['merger_z']

    if snapshot_id is None:
        print("no pre-merger snapshot found")
        return []

    if merger_snapshot is None:
        print("no merger snapshot found")
        return []

    print()
    print("merger z:", merger_z)
    print("merger snapshot:", merger_snapshot)
    print("pre-merger snapshot:", snapshot_id)

    results = []
   
    # pre-merger snapshot

    snapshot, BHs = load_pre_merger_BHs(snapshot_id)

    if BHs is not None:

        for i in range(len(BHs)):
            bh_id = int(BHs['iord'][i])

            # keeping bh1 only
            if bh_id != match['bh1']:
                continue

            halo_id = int(BHs['amiga.grp'][i])

            print("pre merger halo for BH:", bh_id, "is halo_id:", halo_id)

            results.append({'snapshot_id': snapshot_id, 'bh_id': bh_id, 'halo_id': halo_id, 'halo_center': None, 'pre_merger': True})

            break

  
    # post-merger snapshot

    snapshot, BHs = load_pre_merger_BHs(merger_snapshot)

    if BHs is not None:

        for i in range(len(BHs)):

            bh_id = int(BHs['iord'][i])

            # keeping bh1 only
            if bh_id != match['bh1']:
                continue

            halo_id = int(BHs['amiga.grp'][i])

            print("post merger halo for BH:", bh_id, "is halo_id:", halo_id)

            results.append({'snapshot_id': merger_snapshot, 'bh_id': bh_id, 'halo_id': halo_id, 'halo_center': None, 'pre_merger': False})

            break

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
        print()
        print("MERGER")
        print("BH1:", match['bh1'])
        print("BH2:", match['bh2'])
        print("merger z:", match['merger_z'])
        print("pre-merger snapshot:", match['pre_merger_snapshot'])
        print("merger snapshot:", match['merger_snapshot'])
        print("post-merger snapshots:", match['snapshots'])


elif command == 'track_BHs':
    for match in match_mergers():
        print()
        print("MERGER:", match['bh1'], "+", match['bh2'])
        find_remnant_pre_merger_halo(match)


else:
    print("For the z-to-filename dictionary, use: make_dict")
    print("For snapshots below a target z, use: below <target_z>")
    print("For matching mergers to snapshots, use: match")
    print("To find the remnant's pre-merger host halo, use: track_BHs")