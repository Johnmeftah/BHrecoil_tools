import pynbody as pn
import glob
import sys
import numpy as np
import os

# phase 1
mergers_data = np.loadtxt(glob.glob('*.BHmergers')[0])

# making a dictionary: z-values to snapshot IDs
def make_dict():
    snapshot_dict = {}

    # going through every snapshot
    for snap_file in sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]')):
        snap = pn.load(snap_file)
        snap_id = snap_file.split('.')[-1]  # getting the last part of the filename
        z = snap.properties['z']
        snapshot_dict[z] = snap_id  # storing z as the key and snapshot ID as the value

    return snapshot_dict

# getting snapshots below the merger z
def get_snaps_below(target, snapshot_dict):
    sorted_keys = sorted(snapshot_dict.keys())  # sorting the redshifts
    snapshot_ids = []

    # going through every redshift
    for z_value in sorted_keys:
        if z_value < target:
            snapshot_ids.append(snapshot_dict[z_value])

    return snapshot_ids

# getting the closest snapshot before the merger
def get_snap_before(target, snapshot_dict):
    sorted_keys = sorted(snapshot_dict.keys())

    for z_value in sorted_keys:
        if z_value > target:
            return snapshot_dict[z_value]

    return None

# phase 2
# going through real mergers and matching them with snapshots
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

        # getting all snapshots after the merger
        snapshot_ids = get_snaps_below(merger_z, snapshot_dict)

        # getting the closest snapshot after the merger
        if len(snapshot_ids) > 0:
            merger_snapshot = snapshot_ids[-1]
        else:
            merger_snapshot = None

        # getting the closest snapshot before the merger
        pre_merger_snapshot = get_snap_before(merger_z, snapshot_dict)

        matched_mergers.append({'bh1': bh1, 'bh2': bh2, 'merger_z': merger_z, 'pre_merger_snapshot': pre_merger_snapshot, 'merger_snapshot': merger_snapshot, 'snapshots': snapshot_ids})

    return matched_mergers

###########################################################################################################################
# phase 3
# finding all BHs in a snapshot
def find_BH(snapshot):
    BH_filter = pn.filt.LowPass('tform', 0.0)
    BHs = snapshot.stars[BH_filter]
    return BHs

# finding the center of one halo
def find_halo_center(snapshot, halo_id):
    snapshot.physical_units()
    halos = snapshot.halos()

    # finding the halo center using shrinking sphere center 
    halo_center = pn.analysis.halo.center(halos[int(halo_id)], mode='ssc', retcen=True)
    return halo_center

######################################################################
# loading BHs from one snapshot
def load_pre_merger_BHs(snapshot_id):
    snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snapshot_id
    amiga_file = snapshot_file + '.amiga.grp'
    iord_file = snapshot_file + '.iord'

    # skipping snapshots without needed files
    if not os.path.exists(amiga_file):
        print("no amiga.grp for snapshot:", snapshot_id)
        return None, None

    if not os.path.exists(iord_file):
        print("no .iord file for snapshot:", snapshot_id)
        return None, None

    snapshot = pn.load(snapshot_file)

    # loading auxiliary arrays
    snapshot['iord']
    snapshot['amiga.grp']

    BHs = find_BH(snapshot)

    return snapshot, BHs

###############################################
# phase 4
# finding bh1's halo before the merger
def get_pre_merger_halo(match):
    snapshot_id = match['pre_merger_snapshot']

    if snapshot_id is None:
        print("no pre-merger snapshot found")
        return None

    snapshot, BHs = load_pre_merger_BHs(snapshot_id)

    if BHs is None:
        return None

    for i in range(len(BHs)):
        bh_id = int(BHs['iord'][i])

        if bh_id != match['bh1']:
            continue

        halo_id = int(BHs['amiga.grp'][i])  # keeping halo_id even if it is 0

        print("pre merger halo for BH:", bh_id, "is halo_id:", halo_id)

        return {'snapshot_id': snapshot_id, 'bh_id': bh_id, 'halo_id': halo_id}

    return None

#############################################
# finding bh1's halo after the merger
def get_post_merger_halo(match):
    snapshot_id = match['merger_snapshot']

    if snapshot_id is None:
        print("no merger snapshot found")
        return None

    snapshot, BHs = load_pre_merger_BHs(snapshot_id)

    if BHs is None:
        return None

    for i in range(len(BHs)):
        bh_id = int(BHs['iord'][i])

        if bh_id != match['bh1']:
            continue

        halo_id = int(BHs['amiga.grp'][i])  # keeping halo_id even if it is 0

        print("post merger halo for BH:", bh_id, "is halo_id:", halo_id)

        return {'snapshot_id': snapshot_id, 'bh_id': bh_id, 'halo_id': halo_id}

    return None
##########################################################
# tracking bh1 before and after the merger, W/O halo 0
def track_BHs(match):
    print("merger z:", match['merger_z'])
    print("merger snapshot:", match['merger_snapshot'])
    print("pre-merger snapshot:", match['pre_merger_snapshot'])

    pre_merger = get_pre_merger_halo(match)
    post_merger = get_post_merger_halo(match)

    return pre_merger, post_merger

########################################################################################################################
# phase 5
# tracing bh1 including halo 0
def trace_BHs(match):
    pre_merger, post_merger = track_BHs(match)
    return pre_merger, post_merger




# printing every BH and halo ID in one snapshot
# this function must specify which halo is it listing ######
def print_all_BH_halos(snapshot_id):
    snapshot, BHs = load_pre_merger_BHs(snapshot_id)

    if BHs is None:
        return

    for i in range(len(BHs)):
        bh_id = int(BHs['iord'][i])
        halo_id = int(BHs['amiga.grp'][i])

        print("BH:", bh_id, "halo_id:", halo_id)

##############################################

# real BH tracing 
# starting with choosing a merger after printing the necessary info 

# finding the BHs final x, y, z coords
def get_BH_fin_coords(BH_id, target_time):
    BH_data = np.loadtxt(glob.glob('*.BlackHoles')[0])

    # filtering the rows for the remnant 
    mask = BH_data[:, 0] == BH_id # setting col 0 = BH id 
    rows = BH_data[mask] # apply boolean mask 
   

    # claude code begins here:
    # distance from every logged time to target
    time_diff = np.abs(rows[:, 1] - target_time) # this is NOT by me, AI suggestion 

    # fiding the smalleset value in time_diff
    closest_time_index = np.argmin(time_diff) # this returns position idx, not value

    # checking if the time indexing by claud is matching the time in the .BHmergers 
    print(f"target time in .BHmergers: {target_time}")
    print(f"closest time in .BHs: {rows[closest_time_index, 1]}")
    print(f"difference: {time_diff[closest_time_index]}")
    row_at_target_time = rows[closest_time_index]

    
    # using the idx we found and pull out that row, iord, dTime, dDetStep, dM, dr[0] ...etc
    row_at_target_time = rows[closest_time_index]
    # claude code ends here


    # converting to physical units 
    # adding scale factor 
    a = row_at_target_time[17]

    # adding unit conv
    dKpcUnit = 50000.0 # from . param, line 15


    # finding BH's x, y, and z coords (this is our final positions in delta x, y, z)
    BH_x_fin = row_at_target_time[4] * dKpcUnit * a
    BH_y_fin = row_at_target_time[5] * dKpcUnit * a  
    BH_z_fin = row_at_target_time[6] * dKpcUnit * a

    return BH_x_fin, BH_y_fin, BH_z_fin
##########################################################


   




###################################################################

# getting pre-merger halo initial coords 

# getting snapshot ids, bh ids, and halo ids 
def get_halo_init_coords(pre_merger):  # from get_pre_merger_halo(match) function
    snap_id = pre_merger['snapshot_id'] # call pre_merger dict, pull out stored values (the snapshot ids), z = dict keys
    snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snap_id
    snapshot = pn.load(snapshot_file)
    snapshot.physical_units() # didn't change the output 
    halo_id = pre_merger['halo_id']
    halo_center = find_halo_center(snapshot, halo_id) # calling the centering function from phase 3, line 91 
    return halo_center

####################################################################

# getting remnant BH displaacement   

# manually selecting merger 
 
merger_selection = match_mergers()[0]

def get_BH_displacement(pre_merger, BH_id, target_time):
    halo_init_coords = get_halo_init_coords(pre_merger) # from halo pre merger, using ssc (line 91)
    BH_fin_coords = get_BH_fin_coords(BH_id, target_time) # from the .BlackHoles file 

    print(f"halo init coords:", halo_init_coords)
    print(f"BH final coords:", BH_fin_coords)

    dx = BH_fin_coords[0] - halo_init_coords[0]
    dy = BH_fin_coords[1] - halo_init_coords[1]
    dz = BH_fin_coords[2] - halo_init_coords[2]
    r = np.sqrt(dx**2 + dy**2 + dz**2)

    print(f"BH {BH_id} displacement at t = {target_time}:")
    print(f"dx = {dx}")
    print(f"dy = {dy}")
    print(f"dz = {dz}")
    print(f"r = {r} kpc")

    return dx, dy, dz

#######################################

def get_merger_time(merger_selection): # looping the .BHmergers file 
    bh1_match = mergers_data[:, 0] == merger_selection['bh1'] # matching BH1 to our merger 
    bh2_match = mergers_data[:, 1] == merger_selection['bh2'] # keeping rows where both match 
    row = mergers_data[bh1_match & bh2_match][0]
    return row[6] # coulmn 6 = dt 


  















#############################################################################################
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
        track_BHs(match)

elif command == 'trace_BHs':
    for match in match_mergers():
        print()
        print("MERGER:", match['bh1'], "+", match['bh2'])
        trace_BHs(match)

elif command == 'all_BHs':
    if len(sys.argv) < 3:
        print("use: all_BHs <snapshot_id>")
    else:
        snapshot_id = sys.argv[2]
        print_all_BH_halos(snapshot_id)

elif command == 'displacement':
    merger_selection = match_mergers()[7]  # manually chosen merger for now
    # run track_BHs on the merger, returns 2 dicts for both pre/post merger,  prints: z, snapshots, etc  
    pre_merger, post_merger = track_BHs(merger_selection) 
    # loop .BHmergers, match BH IDs, pull out column 6 or whatever is above, store dTime as merger time
    merger_time = get_merger_time(merger_selection)
    # call the function, pass pre merger halo info for x, y, z,  BH iord, and merger time
    # looks up BH position in .BlackHoles for x, y, z
    get_BH_displacement(pre_merger, merger_selection['bh1'], merger_time)








else:
    print("For the z-to-filename dictionary, use: make_dict")
    print("For snapshots below a target z, use: below <target_z>")
    print("For matching mergers to snapshots, use: match")
    print("For finding the pre/post merger halos, W/O halo 0, use: track_BHs")
    print("For tracing the BH, W/ halo 0, use: trace_BHs")
    print("For printing all BH halo IDs, use: all_BHs <snapshot_id>")
    print("For printing a single traced remnant coords + calculating r, use: displacement")



   
