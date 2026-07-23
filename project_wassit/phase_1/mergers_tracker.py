import pynbody as pn 
import glob
import sys
import numpy as np
import csv 

mergers_data = np.loadtxt(glob.glob('*.BHmergers')[0])

# printing mergers info & their z
def mergers():
    count = 0
    for row in mergers_data:
        if row[6] < 0:
            continue  
        bh1, bh2 = int(row[0]), int(row[1])
        z = 1 / row[7] - 1
        count += 1
        print(f"BH {bh1} merged with BH {bh2}, z = {z:.3f}")
    print(f"\nreal mergers total: {count}")



# printing snapshots info, their z, and cosmic age 
def snapshot():
    for snap_lists in sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]')):
        snap = pn.load(snap_lists)
        z = snap.properties['z']
        age = pn.analysis.cosmology.age(snap)
        print(f"{snap_lists}: z = {z:.3f}, age = {age:.3f} Gyr")



# matching mergers z W/ snapshots' z
def match_dict():
    snap_z_list = []
    for snap_list in sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]')):
        snap = pn.load(snap_list)
        snap_id = snap_list.split('.')[-1]
        snap_z_list.append((snap_id, snap.properties['z']))

    matched_mergers = []
    for row in mergers_data:
        if row[6] < 0:
            continue
        bh1, bh2 = int(row[0]), int(row[1])
        merger_z = 1 / row[7] - 1 
        snap_id, snap_z = min(snap_z_list, key=lambda s:abs(s[1] - merger_z)) # matching snap's z W/ ,merger's z, I used GPT for this line

        matched_mergers.append(({
            'bh1': bh1,
            'bh2': bh2,
            'merger_z': merger_z,
            'snapshot': snap_id,
            'snapshot_z': snap_z
        }))
    return matched_mergers
    






command = sys.argv[1] if len(sys.argv) > 1 else None

if command == 'mergers':
    mergers()

if command == 'snapshots':
    snapshot()

if command == 'match':
    for m in match_dict():
        print(m)


else:
    print("For mergers info, use: mergers")
    print("For snapshots info, use: snapshots")
    print("For matching mergers to snapshots, use: match")
