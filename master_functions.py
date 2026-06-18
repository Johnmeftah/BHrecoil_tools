import pynbody as pn
import numpy as np
import pandas as pd
import sys
import os 
from collections import Counter
import matplotlib.pyplot as plt
import glob 

h = 0.67 # Hubble param to convert M_sun/h to M_sun
hi_res_cut = 0.1  # fMhires threshold

snapshot = 'pioneer50h243.1536gst1bwK1BH.000345' 
print(f"Using snapshot: {snapshot}")

# load snapshot + AHF 
def load_snapshot(snapshot):
    s = pn.load(snapshot)
    s.physical_units()  # converting code units to physical units 
    return s 

def load_AHF(snapshot):
    AHF_file = glob.glob(snapshot + "*.AHF_halos")[0] 
    AHF = pd.read_csv(AHF_file, sep='\t', header=0) 
    return AHF
   



# functions 
# listing the keys in the snapshot
def snap_keys(s):
    print(f"keys inside the snapshot are: {s.loadable_keys()}")

# printing min and max DM particle mass and their ratio
def dm_minmax(s):
    print(f" minimum DM particle mass: {s.dm['mass'].min(): .3e}")
    print(f" max DM particle mass: {s.dm['mass'].max(): .3e}")
    print(f" ratio: {s.dm['mass'].max() / s.dm['mass'].min(): .3e}")
    

# printing the entire dictionary in AHF
def AHF_keys(AHF):
    print(f"keys inside the AHF are: {AHF.columns.tolist()}")

# finding the total number of halos in AHF
def AHF_halo_info(AHF):
    print(f"total number of halos: {len(AHF)}")

# printing the corrected halo masses and the most and least massive halos
def AHF_halo_mass(AHF):
    unique_vals = sorted(AHF['fMhires(38)'].unique())
    AHF = AHF[(AHF['#ID(1)'] != 0) & (AHF['fMhires(38)'] >= hi_res_cut)].copy()
    if AHF.empty:
        print(f"No halos matched hi_res_cut = {hi_res_cut} (fMhires >= {hi_res_cut}).")
        print(f"fMhires range in catalog: {unique_vals[0]:.3f} – {unique_vals[-1]:.3f}")
        return
    AHF['Mhalo(4)'] = AHF['Mhalo(4)'] / h

    ids = AHF['#ID(1)']
    masses = AHF['Mhalo(4)']

    print(AHF[['#ID(1)', 'Mhalo(4)']].to_string(index=False, formatters={'Mhalo(4)': '{:.3e} M_sun'.format}))
    print(f"most massive: halo {ids[masses.idxmax()]} with {masses.max():.3e} M_sun")
    print(f"least massive: halo {ids[masses.idxmin()]} with {masses.min():.3e} M_sun")

 

# counting BHs in the snapshot
def BH_count(s):
    bhs = s.star[s.star['tform'] < 0]
    print(f'total number of BHs: {len(bhs)}')

# counting & IDing how many halos have BHs in them
def BH_halos(s, AHF):
    bhs = s.star[s.star['tform'] < 0]
    bh_grp = bhs['amiga.grp']  # halo ID each BH belongs to
    counts = Counter(bh_grp)   # number of BHs per halo [halo_id: count] 

    for halo_id, n in sorted(counts.items()): # unpacking the dictionary into halo ID and count (key, value)
        if halo_id == 0:
            continue  # skip halo 0
        mass = AHF.loc[AHF['#ID(1)'] == halo_id, 'Mhalo(4)'].values[0] / h # selecting data by location, true/fals mask, true for halo ID matches the loop
        print(f"halo {halo_id} has {n} BH(s) with {mass:.3e} M_sun")


# checking the mass range of the halos in CSV
def mass_range():
    df = pd.read_csv('halo_masses.csv')
    masses = df['Mhalo(4)'] / h
    print(f"mass range of clean halos in halo_masses.csv:") 
    print(f"min mass: {masses.min():.3e} M_sun")
    print(f"max mass: {masses.max():.3e} M_sun")

# writing the full halos + BHs csv (will be used for the occupation fraction plot)
def write_csvs():
    ahf = load_AHF(snapshot)
    s = load_snapshot(snapshot)
    correct_masses = ahf[(ahf['#ID(1)'] != 0) & (ahf['fMhires(38)'] >= hi_res_cut)][['#ID(1)', 'Mhalo(4)']].copy()
    mass_of_halo_1 = ahf['Mhalo(4)'][1]
    print(f" mass of halo 1 is: {mass_of_halo_1}") 
   # correct_masses = correct_masses[correct_masses <= mass_of_halo_1] # this might compare the whole df to one mass, can it corrupt the filtering?
    correct_masses = correct_masses[correct_masses['Mhalo(4)'] <= mass_of_halo_1] # this only compares the mass column
    correct_masses.to_csv('halo_masses.csv', index=False)
    # s['amiga.grp']  # pre loading group array
    bhs = s.star[s.star['tform'] < 0]
    counts = Counter(bhs['amiga.grp']) # counting how many BHs are in each halo, returns a dictionary {halo_id: count}
    print (f" the val of counts is: {counts}")


    BH_halo_id, BH_halo_masses = [], []
    #for halo_id, n in sorted(counts.items()):
     #   if halo_id == 0:
      #      continue

        # need to print the counts 
      #  row = ahf.loc[ahf['#ID(1)'] == halo_id] # select the row in AHF catalog where halo ID matches current halo ID in loop
       # print(f" the val of row is {row}") # print the row to check if it's selecting the correct halo
       # if row.empty or row['fMhires(38)'].values[0] < hi_res_cut:
       #     continue
    BHhalos = bhs['amiga.grp']
    print(f" the value of BHhalos is {BHhalos}")
    halos = np.unique(BHhalos)
    halos = halos[halos != 0]
    print(f" the value of halos is {halos}")
       
    # getting halo masses 

    for halo_id in halos:
        row = ahf.loc[ahf['#ID(1)'] == halo_id]

        mass = row['Mhalo(4)'].values[0] # take out halo mass from that row 
        BH_halo_id.append(halo_id) # add the halo ID and mass to the BH halo lists
        BH_halo_masses.append(mass)

    dfBH = pd.DataFrame({'halo_id': BH_halo_id, 'Mhalo(4)': BH_halo_masses})
    dfBH.to_csv('BH_masses.csv', index=False)
    print("saved halo_masses.csv and BH_masses.csv")


# making  OF plot
def plot_of(n):
    halo_mass = pd.read_csv('halo_masses_from_amiga.csv')['Mvir'] 
    BH_halo_mass = pd.read_csv('BH_masses.csv')['Mhalo(4)'] / h 
    log_min = np.log10(halo_mass.min()) # find log 10 of the least massive halo, round down to nearest integer for min edge 
    log_max = np.log10(halo_mass.max()) # find log 10 of the most massive halo, round up to nearest integer for max edge
     
    bin_edges = np.logspace(log_min, log_max, n + 1)

    

    #def count_in_bins(m, e, label=''):
     #   counts = []
      #  for lo, hi in zip(e[:-1], e[1:]): # loop through the bin edges, take the lower and upper edge of each bin
       #     c = np.count_nonzero((m >= lo) & (m <= hi)) # count # of halos in that bin using boolean mask 
        #    print(f"  {label} bin [{lo:.3e}, {hi:.3e}]: {c}") # print the count for that bin with the bin edges
         #   counts.append(c) 
        #return np.array(counts) 
    def count_in_bins(m, e, label=''):
        counts = []

        for i, (lo, hi) in enumerate(zip(e[:-1], e[1:])): # glue the 2 (lo & hi) lists together 
            if i == 0: # if 1st bin = 0
                c = np.count_nonzero((m >= lo) & (m <= hi)) # include both edges 
            else: # the rest of the bins 
                c = np.count_nonzero((m > lo) & (m <= hi)) # don't include to avoid dbl count
            print(f" {label} bin [{lo:.3e}, {hi:.3e}]: {c}")
            counts.append(c)

        return np.array(counts)
    
    print("ALL halos per bin:")
    count_all = count_in_bins(halo_mass, bin_edges, label='ALL')
    print("BH halos per bin:")
    count_BH  = count_in_bins(BH_halo_mass, bin_edges, label='BH')

    occ_frac = np.where(count_all > 0, count_BH / count_all, 0.0) # where condition is true, calc the fraction, where false, == 0
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:]) # geometric mean for log bins 


    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(bin_centers, occ_frac, lw=2, zorder=2)
    ax.scatter(bin_centers, occ_frac, s=80, zorder=3)

    for x, y, n_all, n_bh in zip(bin_centers, occ_frac, count_all, count_BH):
        ax.annotate(
            f'{n_bh}/{n_all}',
            xy=(x, y),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            fontsize=9
        )

    ax.set_xscale('log')
#    ax.set_yscale('log')
    ax.set_xlabel(r'$M_\mathrm{halo}\ [M_\odot]$', fontsize=13)
    ax.set_ylabel('BH occupation fraction', fontsize=13)
    ax.set_title(f'BH occupation fraction vs halo mass ({n} bins)', fontsize=13)
    ax.set_ylim(-0.05, 1.15)

    plt.tight_layout()
    plt.show()

    # converting kick velocity from code units to km/s
def conv_vkick(value):
    G_CGS = 6.674e-8
    MSOL_CGS = 1.989e33
    KPC_CGS = 3.086e21
    M_unit = 1.84793e16
    r_unit = 50000.0
    dKmPerSecUnit = (1.0 / 1e5) * np.sqrt(G_CGS * M_unit * MSOL_CGS / (r_unit * KPC_CGS))
    print(f"{value} code units = {value * dKmPerSecUnit:.4f} km/s")

# manually checking the fMhires values 
def check_fMhires(AHF):
    print(AHF[['#ID(1)', 'Mhalo(4)', 'fMhires(38)']].head(10).to_string())
        
# checking snapshots for zeros
def check_snapshot_zeros(s):
    print(f"Checking snapshot: {s.filename}")
    # checking for 0 mass particles 
    zero_dm = np.sum(s.dm['mass'] == 0)
    zero_gas = np.sum(s.gas['mass'] == 0)
    zero_star = np.sum(s.star['mass'] == 0)
    nan_mass = np.sum(np.isnan(s.dm['mass'])) + np.sum(np.isnan(s.gas['mass'])) + np.sum(np.isnan(s.star['mass']))

    print(f"Number of zero mass DM particles: {zero_dm}")
    print(f"Number of zero mass gas particles: {zero_gas}")
    print(f"Number of zero mass star particles: {zero_star}")
    print(f"Number of NaN mass particles:{nan_mass}")

    if zero_dm > 0:
        print(f"  WARNING: {zero_dm} zero mass DM particles found")
    else:
        print("  OK: No zero mass DM particles found.")
    if zero_gas > 0:
        print(f"  WARNING: {zero_gas} zero mass gas particles found")
    else:
        print("  OK: No zero mass gas particles found.")
    if zero_star > 0:
        print(f"  WARNING: {zero_star} zero mass star particles found")
    else:
        print("  OK: No zero mass star particles found.")
    if nan_mass > 0:
        print(f"  WARNING: {nan_mass} NaN mass particles found")
    else:
        print("  OK: No NaN mass particles found.")

# removing zero mass particles from the snapshot + updating the startrun 

def fix_snapshot_zeros(s, snapshot_path):
    if snapshot_path.endswith('.original'):
        print("Snapshot is already a backup (.original), skipping.")
        return

    step = snapshot_path.split('.')[-1] # split by . and take the last part (the 6 digits) 
    startrun_path = f"{step}.startrun"
    original_path = snapshot_path + ".original"

    # rename the original snapshot to .original
    os.rename(snapshot_path, original_path)
    print(f"Original snapshot backed up to: {original_path}")

    # load the backup and strip zero-mass particles
    s_raw = pn.load(original_path)
    print(f"Fixing snapshot: {snapshot_path}")
    clean = s_raw[s_raw['mass'] != 0]

    # write clean snapshot back to the original name
    clean.write(filename=snapshot_path, fmt=pn.tipsy.TipsySnap)
    print(f"Cleaned snapshot saved to: {snapshot_path}")

    # update startrun — the name stays the same so this is mostly a no-op,
    with open(startrun_path, 'r') as f:
        content = f.read()
    content = content.replace(
        f"ic_filename = {original_path}",
        f"ic_filename = {snapshot_path}"
    )
    # also catch the case where it previously pointed to a .clean path
    content = content.replace(
        f"ic_filename = {snapshot_path}.clean",
        f"ic_filename = {snapshot_path}"
    )
    with open(startrun_path, 'w') as f:
        f.write(content)
    print(f"Updated startrun: {startrun_path}")

# getting halo masses from the .stat file instead of ahf 
def read_amiga_stat(snapshot):
    stat_file = snapshot + ".amiga.stat"
    names = ['Grp','N_tot','N_gas','N_star','N_dark','Mvir','Rvir','GasMass','StarMass','DarkMass','V_max','R@V_max','VelDisp','Xc','Yc','Zc','VXc','VYc','VZc','Contam','Satellite?','False?']
    stat_file = pd.read_table(stat_file, names=names, header=0, dtype='str', sep=r'\s+') # needed an r 
    return stat_file

def write_csvs_from_amiga_stat(snapshot):
    stat_file = read_amiga_stat(snapshot)
    halomasses = stat_file['Mvir']
    halomasses.to_csv('halo_masses_from_amiga.csv', index=False)

# plotting all the sims in one place 

def plot_of_combined(n):
    # 
    sims = [
    {'path': '/mnt/data0/jmeftah/changa_runs/sand_boxes/notmy_pioneer', 'label': 'No kicks', 'color': 'black'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil0', 'label': 'Aligned spin','color': 'blue'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil1', 'label': 'Anti-aligned', 'color': 'red'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil2', 'label': 'Random alignment', 'color': 'green'},
]
    # load each sim's halo masses and BH halo masses, and keep a running list of all
    # halo masses so we can build one shared set of bin edges (same x-grid for every curve)
    all_halo_mass = []
    for sim in sims:
        sim['halo_mass'] = pd.read_csv(os.path.join(sim['path'], 'halo_masses_from_amiga.csv'))['Mvir']
        sim['BH_halo_mass'] = pd.read_csv(os.path.join(sim['path'], 'BH_masses.csv'))['Mhalo(4)'] / h
        all_halo_mass.append(sim['halo_mass'])

    combined_halo_mass = pd.concat(all_halo_mass)
    log_min = np.log10(combined_halo_mass.min())
    log_max = np.log10(combined_halo_mass.max())
    bin_edges = np.logspace(log_min, log_max, n + 1)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])  # geometric mean for log bins

    def count_in_bins(m, e):
        counts = []
        for i, (lo, hi) in enumerate(zip(e[:-1], e[1:])):
            if i == 0:  # first bin includes both edges
                c = np.count_nonzero((m >= lo) & (m <= hi))
            else:  # rest of the bins, don't double count the shared edge
                c = np.count_nonzero((m > lo) & (m <= hi))
            counts.append(c)
        return np.array(counts)

    fig, ax = plt.subplots(figsize=(7, 5))

    for sim in sims:
        count_all = count_in_bins(sim['halo_mass'], bin_edges)
        count_BH = count_in_bins(sim['BH_halo_mass'], bin_edges)
        occ_frac = np.where(count_all > 0, count_BH / count_all, 0.0)

        ax.plot(bin_centers, occ_frac, lw=2, color=sim['color'], label=sim['label'], zorder=2)
        ax.scatter(bin_centers, occ_frac, s=60, color=sim['color'], zorder=3)

    ax.plot([], [], ' ', label='z = 5')  

    ax.set_xscale('log')
    ax.set_yscale('symlog', linthresh=0.01)
    ax.set_xlabel(r'$M_\mathrm{halo}\ [M_\odot]$', fontsize=13)
    ax.set_ylabel('BH occupation fraction', fontsize=13)
     # ax.set_title(f'BH occupation fraction vs halo mass, z=5 ({n} bins)', fontsize=13)
    ax.set_ylim(-0.05, 1.15)
    ax.legend()
    plt.tight_layout()
    plt.show()



  







# main 
command = sys.argv[1] if len(sys.argv) > 1 else None

if command == "snap_keys":
    snap_keys(load_snapshot(snapshot))

elif command == "dm_minmax":
    dm_minmax(load_snapshot(snapshot))

elif command == "AHF_keys":
    AHF_keys(load_AHF(snapshot))

elif command == "halo_count":
    AHF_halo_info(load_AHF(snapshot))

elif command == "halo_mass":
    AHF_halo_mass(load_AHF(snapshot))

elif command == "BH_count":
    BH_count(load_snapshot(snapshot))

elif command == "BH_halos":
    BH_halos(load_snapshot(snapshot), load_AHF(snapshot))

elif command == "mass_range":
    mass_range() 

elif command == "write_csv":
    write_csvs()    


elif command == "plot_of":
    n = int(sys.argv[2].replace('-n', ''))
    plot_of(n)

elif command == "conv_vkick":
    value = float(sys.argv[2])
    conv_vkick(value)

elif command == "check_hires":
    check_fMhires(load_AHF(snapshot))  

elif command == "check_zeros":
    check_snapshot_zeros(load_snapshot(snapshot))

elif command == "fix_zeros":
    s = load_snapshot(snapshot)
    fix_snapshot_zeros(s, s.filename)

elif command == "write_halo_csv_amiga":
    write_csvs_from_amiga_stat(snapshot)    

elif command == "write_csv_amiga":
    write_csvs_from_amiga_stat(snapshot)
    # write_BH_halo_masses_from_amiga_stat(snapshot)

elif command == "plot_of_all":
    n = int(sys.argv[2].replace('-n', ''))
    plot_of_combined(n)


else:   
    print("Please enter one of the following commands:")
    print("python master_functions.py snap_keys — list all loadable keys in the snapshot")
    print("python master_functions.py dm_minmax — print min/max DM particle mass and their ratio")
    print("python master_functions.py AHF_keys  — list all columns in the AHF halo catalog")
    print("python master_functions.py halo_count — print total number of halos in AHF")
    print("python master_functions.py halo_mass — print halo masses and most/least massive halo")
    print("python master_functions.py BH_count — print total number of black holes in the snapshot")
    print("python master_functions.py BH_halos — print which halos contain BHs and their masses")
    print("python master_functions.py mass_range — print min/max halo mass from the saved CSV")
    print("python master_functions.py write_csv — write halo_masses.csv and BH_masses.csv")
    print("python master_functions.py plot_of_pretty -n5 — same but with bin counts annotated and color coding") # example with 5 bins for the OF
    print("python master_functions.py conv_vkick <comoving velocity> — convert a kick velocity from code units to km/s")
    print("python master_functions.py check_hires — print fMhires values for the first few halos to verify their values")
    print("python master_functions.py check_zeros — check for zero mass particles in the snapshot")
    print("python master_functions.py fix_zeros — create a cleaned snapshot without zero mass particles and update startruns.txt to use it")
