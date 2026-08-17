import pynbody as pn 
import glob
import sys
import numpy as np
import os 


# phase I
mergers_data = np.loadtxt(glob.glob('*.BHmergers')[0])

# making a dictionary: z-values to snapshot filename
def make_dict():
    snapshot_dict = {}
    for snap_file in sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]')):
        snap = pn.load(snap_file)
        snap_id = snap_file.split('.')[-1] # getting the numbers at the end 
        z = snap.properties['z']
        snapshot_dict[z] = snap_id # saving, z is the key, filemae is the value 
    return snapshot_dict


# given a target z, return the filenames of every snapshot W/ a smaller z
def get_snaps_below(target, snapshot_dict):
    sorted_keys = sorted(snapshot_dict.keys()) # z vals in order 
    files = []
    for z_value in sorted_keys:
        if z_value < target: # keeping snapshots below our target z
            files.append(snapshot_dict[z_value])
    return files 

# go through real merger & find the snapshots that come after it
def match_mergers():
    snapshot_dict = make_dict()
    matched_mergers = []
    for row in mergers_data:
        if row[6] < 0: # skipping fake mergers 
            continue
        bh1, bh2 = int(row[0]), int(row[1])
        merger_z = 1 / row[7] - 1 # scaler factor to z
        files = get_snaps_below(merger_z, snapshot_dict) # snapshots below this merger's z
        matched_mergers.append({
            'bh1': bh1,
            'bh2': bh2,
            'merger_z': merger_z,
            'snapshots': files
        })
    return matched_mergers

# phase II
# BHs def
def findBH(snapshot):
    BHfilter = pn.filt.LowPass('tform', 0.0)
    BHs = snapshot.stars[BHfilter]
    return BHs

# tracking BHs in halos 
def trackBHs(match):
    print("merger:", match['bh1'], match['bh2'], "z =", match['merger_z'])

    for step in match['snapshots']:
        print("checking snapshot:", step)
        snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + step
        amiga_file = snapshot_file + '.amiga.grp'

        if not os.path.exists(amiga_file):
            print(step, "no amiga.grp")
            continue

        snapshot = pn.load(snapshot_file)
        BHs = findBH(snapshot)
        print("snapshot:", step)

        for i in range(len(BHs)):
            bh_id = BHs['iord'][i]
            halo_id = BHs['amiga.grp'][i]

            print("BH:", bh_id, "halo:", halo_id)




command = sys.argv[1] if len(sys.argv) > 1 else None

if command == 'make_dict':
    snapshot_dict = make_dict()
    for z, snap_id in snapshot_dict.items():
        print(f"{snap_id}: z = {z:.3f}")

elif command == 'below':
    target = float(sys.argv[2])
    snapshot_dict= make_dict()
    files = get_snaps_below(target, snapshot_dict)
    print(files)

elif command == 'match':
    for m in match_mergers():
        print(m)

elif command == "track_BHs":
    for match in match_mergers():
        trackBHs(match)


else:
    print("For the z-to-filename dictionary, use: make_dict")
    print("For the snapshots below a target z, use: below <target_z>")
    print("For matching mergers to snapshots below their z, use: match")
    print("To track BHs and their halos, use: track_BHs")
