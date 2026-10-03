import pynbody as pn
import glob
import sys
import numpy as np
import os
from scipy import interpolate
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt

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

    # pulling out the BHs 
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

################################################################################################################################

# phase 6: interpolation 

# for now, working with 1 merger, we loop over the rest later, this is a test

merger_index = 6 # this mumber depends on the "match" function

# fast grid, BH position history 

def get_bh_positions(BH_id):
    BH_data = np.loadtxt(glob.glob('*BlackHoles')[0])

    mask = BH_data[:,0] == BH_id
    bh_rows = BH_data[mask]

    # putting rows in time order (col 17 = a in .BlackHoles)
    bh_rows = bh_rows[np.argsort(bh_rows[:, 17])] # argsort:  get the indices in sorted order
    bh_scalefac = bh_rows[:,17]
    dKpcUnit = 50000.0  # from .param, line 15 (box size)

    bh_x = bh_rows[:, 4] * dKpcUnit * bh_scalefac
    bh_y = bh_rows[:, 5] * dKpcUnit * bh_scalefac
    bh_z = bh_rows[:, 6] * dKpcUnit * bh_scalefac

    return bh_scalefac, bh_x, bh_y, bh_z

######################################################

# halo center (at one snapshot)

def get_halo_center_at_snap(snap_id, halo_id):
    snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snap_id
    snapshot = pn.load(snapshot_file)
    snapshot.physical_units()

    return find_halo_center(snapshot, halo_id) # calling prev ssc function 

####################################################

# which halo is the BH in 

def get_halo_id_at_snap(snap_id, BH_id):
    snapshot, BHs = load_pre_merger_BHs(snap_id) # pulling out all the BHs in snapshot

    if BHs is None:
        return None

    for bh_row in range(len(BHs)):
        if (BHs['iord'][bh_row]) == BH_id: 
            return (BHs['amiga.grp'][bh_row]) # .grp tells us which halo this BH is in
        
    # if no BH in snapshot
    return None
    #############################################################################

    # slow grid: host halo center at every snapshot in the list
    # getting halo x, y, z arrays sorted in time order 

def get_halo_centers(snap_ids, host_halo_id):
    snap_scalefac = []
    halo_centers = []

# loop thru the snapshots, call get halo center to run SSC
    for snap_id in snap_ids:
        snapshot_file = 'pioneer50h243.1536gst1bwK1BH.' + snap_id
        snapshot = pn.load(snapshot_file)

        a = snapshot.properties['a']
        snap_scalefac.append(a)
        halo_centers.append(get_halo_center_at_snap(snap_id, host_halo_id))

        print("snapshot", snap_id, "a", round(a,3), "center", halo_centers[-1])

    # convert lists to NP arrays so we can sort and index them easily
    snap_scalefac = np.array(snap_scalefac)
    halo_centers = np.array(halo_centers)

    # snapshots may be in any order, sort them by scale factor (time)
    # PchipInterpolator requires its x values to be increasing
    time_order = np.argsort(snap_scalefac)

    # applying the same ordering to all four arrays so they stay lined up
    # halo_centers is an (n_snapshots, 3) array, cols 0,1,2 are x,y,z
    return (snap_scalefac[time_order], halo_centers[time_order, 0], halo_centers[time_order, 1], halo_centers[time_order, 2])

###########################################################################
# evaluating halo center at ever BH time 
# one interpolater per coordinate, built from the snapshot values 

def interp_halo_centers(snap_scalefac, halo_x, halo_y, halo_z, bh_scalefac):
    # keeping only BH times inside the snapshot 
    # anything outside that range is a guess, not interpolating 

    # boolean array, one entry per BH row, True = BH time falls between the 1st and last snapshot 
    # only keeping BHs that fall between 1st and last snapshot
    bh_times_in_range = ((bh_scalefac >= snap_scalefac.min()) & (bh_scalefac <= snap_scalefac.max()))
    bh_scalefac_in_range = bh_scalefac[bh_times_in_range] # surviving times 

    # bulding the three curves through the shanpshot points 
    # drawing a smooth line thru the snapshot x,y,z
    
    fx = PchipInterpolator(snap_scalefac, halo_x)
    fy = PchipInterpolator(snap_scalefac, halo_y)
    fz = PchipInterpolator(snap_scalefac, halo_z)

    return bh_times_in_range, fx(bh_scalefac_in_range), fy(bh_scalefac_in_range), fz(bh_scalefac_in_range)

############################################################################################################

# finding distance between the BH & halo ceneter at each time 

def get_separation(bh_x, bh_y, bh_z, halo_x, halo_y, halo_z):
    dx = bh_x - halo_x
    dy = bh_y - halo_y
    dz = bh_z - halo_z

    r = np.sqrt(dx**2 + dy**2 + dz**2)

    return dx, dy, dz, r

###############################################################################
# reading Rvir for one halo from the .stat file
# returns the virial radius in kpc, or None if the halo is not listed
def get_rvir(snap_id, halo_id):
    stat_file = 'pioneer50h243.1536gst1bwK1BH.' + snap_id + '.amiga.stat'

    with open(stat_file) as stat_lines:
        next(stat_lines) # skipping the column header line

        for halo_line in stat_lines:
            halo_columns = halo_line.split()  # spliting on whitespace

            grp = int(halo_columns[0]) # col 0 = Grp, the halo id
            if grp == halo_id:
                return float(halo_columns[6])  # col 6 = Rvir(kpc)

    # halo id not found in this snapshot
    return None


################################################################################

# running all the steps for one merger

def run_trajectory(match):
    print("\n=== MERGER ===")
    print("BH1:", match['bh1'], "  BH2:", match['bh2'])
    print("merger z:", match['merger_z'])
    print("merger snapshot:", match['merger_snapshot'])
    print("pre-merger snapshot:", match['pre_merger_snapshot'])
    BH_id = match['bh1']
    print(f"\nchecking where BH {BH_id} is ...")

    pre_merger = get_pre_merger_halo(match)
    host_halo_id = pre_merger['halo_id']
    

# cap the number of snapshots to be tested,[:n_snaps], drop the cap to read all the snaps 
    snap_ids = [match['pre_merger_snapshot']] + match['snapshots'][::-1][:8] 

    print("snapshots:", snap_ids)

    # slow grid
    print(f"\nfinding halo: {host_halo_id} center at each snapshot ...")
    snap_scalefac, halo_x, halo_y, halo_z = get_halo_centers(snap_ids, host_halo_id)

    # fast grid
    print(f"\nreading BH positions from .BlackHoles ...")
    bh_scalefac, bh_x, bh_y, bh_z = get_bh_positions(BH_id)
    print(f"{len(bh_scalefac)} logged positions for BH {BH_id}")

    # filling halo center at every BH time
    # bh_times_in_range is a mask marking which BH rows fell inside the snapshot range
    print(f"\ninterpolating halo center onto BH times ...")
    bh_times_in_range, halo_x_interp, halo_y_interp, halo_z_interp = interp_halo_centers(snap_scalefac, halo_x, halo_y, halo_z, bh_scalefac)
    print(f"{bh_times_in_range.sum()} BH times fall inside the snapshot range")

    print("\n=== UNITS CHECK ===")
    print(f"before the merger, at a = {snap_scalefac[0]:.3f}")
    print(f"halo {host_halo_id} center: {halo_x[0]:.1f}, {halo_y[0]:.1f}, {halo_z[0]:.1f}")
    print(f"BH {BH_id}: {bh_x[bh_times_in_range][0]:.1f}, {bh_y[bh_times_in_range][0]:.1f}, {bh_z[bh_times_in_range][0]:.1f}")

    # subtracting
    dx, dy, dz, r = get_separation(bh_x[bh_times_in_range], bh_y[bh_times_in_range], bh_z[bh_times_in_range], halo_x_interp, halo_y_interp, halo_z_interp)

    # where the BH actually is at each snapshot
    # if this leaves the host halo, the separation is measured against
    # a halo the BH no longer belongs to
    # Rvir is a second opinion: amiga.grp says which halo it belongs to,
    # Rvir says whether it is geometrically inside
    print(f"\nfinding BH {BH_id} location by snapshot:")
    for snap_index, snap_id in enumerate(snap_ids):
        bh_halo = get_halo_id_at_snap(snap_id, BH_id)
        rvir = get_rvir(snap_id, host_halo_id)

        # separation at this snapshot's scale factor
        r_at_snap = np.interp(snap_scalefac[snap_index], bh_scalefac[bh_times_in_range], r)
        inside = "inside Rvir" if r_at_snap < rvir else "outside Rvir"
        print(f"{snap_id}: halo {bh_halo}   r = {r_at_snap:.1f} kpc" f"Rvir = {rvir:.1f} kpc {inside}")

    print("\n=== RESULTS ===")
    print(f"checking how far BH {BH_id} traveled from the center of halo {host_halo_id}:")
    print(f"between a = {snap_scalefac.min():.3f} and a = {snap_scalefac.max():.3f}:")
    print(f"furthest from halo center: {r.max():.2f} kpc")
    print(f"closest to halo center: {r.min():.2f} kpc")
    print(f"distance from halo center at last checked snapshot: {r[-1]:.2f} kpc\n")

    # for printing age on the x-axis 
    snapshot_for_cosmology = pn.load('pioneer50h243.1536gst1bwK1BH.' + snap_ids[0])

    # convert the BH scale factors to age of the universe in Gyr
    bh_scalefac_in_range = bh_scalefac[bh_times_in_range]
    bh_redshift = 1.0 / bh_scalefac_in_range - 1.0
    bh_age_gyr = pn.analysis.cosmology.age(snapshot_for_cosmology, z=bh_redshift)

    return bh_age_gyr, dx, dy, dz, r
    

############################################################################################











































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
    merger_selection = match_mergers()[6]  # manually chosen merger for now
    # run track_BHs on the merger, returns 2 dicts for both pre/post merger,  prints: z, snapshots, etc  
    pre_merger, post_merger = track_BHs(merger_selection) 
    # loop .BHmergers, match BH IDs, pull out column 6 or whatever is above, store dTime as merger time
    merger_time = get_merger_time(merger_selection)
    # call the function, pass pre merger halo info for x, y, z,  BH iord, and merger time
    # looks up BH position in .BlackHoles for x, y, z
    get_BH_displacement(pre_merger, merger_selection['bh1'], merger_time)


elif command == 'trajectory':
    merger_selection = match_mergers()[merger_index]

    age, dx, dy, dz, r = run_trajectory(merger_selection)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(age, r, 'k')
    ax1.set_xlabel('age of universe (Gyr)')
    ax1.set_ylabel('separation (kpc)')
    ax1.set_title('distance from center')

    ax2.plot(age, dx, label='dx')
    ax2.plot(age, dy, label='dy')
    ax2.plot(age, dz, label='dz')
    ax2.axhline(0, color='gray', lw=0.5)
    ax2.set_xlabel('age of universe (Gyr)')
    ax2.set_ylabel('BH minus halo center (kpc)')
    ax2.set_title('components')
    ax2.legend()

    plt.tight_layout()
    plt.show()








else:
    print("For the z-to-filename dictionary, use: make_dict")
    print("For snapshots below a target z, use: below <target_z>")
    print("For matching mergers to snapshots, use: match")
    print("For finding the pre/post merger halos, W/O halo 0, use: track_BHs")
    print("For tracing the BH, W/ halo 0, use: trace_BHs")
    print("For printing all BH halo IDs, use: all_BHs <snapshot_id>")
    print("For printing a single traced remnant coords + calculating r, use: displacement")
    print("For the remnant BH trajectory, use: trajectory")



   
