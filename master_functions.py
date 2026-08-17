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
    BH_halo_mass = pd.read_csv('BH_masses.csv')['Mhalo(4)']  / h 
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
    # checking for 0 mass / NaN particles
    zero_dm = np.sum(s.dm['mass'] == 0)
    zero_gas = np.sum(s.gas['mass'] == 0)
    zero_star = np.sum(s.star['mass'] == 0)
    nan_mass = (
        np.sum(np.isnan(s.dm['mass']))
        + np.sum(np.isnan(s.gas['mass']))
        + np.sum(np.isnan(s.star['mass']))
    )

    return {
        'zero_dm': int(zero_dm),
        'zero_gas': int(zero_gas),
        'zero_star': int(zero_star),
        'nan_mass': int(nan_mass),
    }


def check_all_snapshots_zeros():
    
    snapshots = sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]'))

    if not snapshots:
        print("No snapshots found in the current directory.")
        return

    print(f"Checking {len(snapshots)} snapshots...\n")

    clean_count = 0
    problem_snapshots = []
    error_snapshots = []

    for snapshot_path in snapshots:
        step = snapshot_path.split('.')[-1]

        try:
            s = load_snapshot(snapshot_path)
            result = check_snapshot_zeros(s)
        except Exception as exc:
            print(f"{step}  ERROR: could not load/check snapshot ({exc})")
            error_snapshots.append(step)
            continue

        has_problem = any(result.values())

        if not has_problem:
            print(f"{step}  OK")
            clean_count += 1
            continue

        print(f"{step}  WARNING")
        print(f"zero-mass DM: {result['zero_dm']}")
        print(f"zero-mass gas: {result['zero_gas']}")
        print(f"zero-mass stars: {result['zero_star']}")
        print(f"NaN masses: {result['nan_mass']}")
        problem_snapshots.append(step)

    print("\n--------------------------------")
    print(f"Snapshots checked: {len(snapshots)}")
    print(f"Clean snapshots: {clean_count}")
    print(f"Problem snapshots: {len(problem_snapshots)}")
    print(f"Load/check errors: {len(error_snapshots)}")

    if problem_snapshots:
        print("\nSnapshots with problems:")
        for step in problem_snapshots:
            print(step)

    if error_snapshots:
        print("\nSnapshots with load/check errors:")
        for step in error_snapshots:
            print(step)

    print("--------------------------------")

# removing zero mass particles from the snapshot + updating the startrun 

def fix_snapshot_zeros(s, snapshot_path):
    if snapshot_path.endswith('.original'):
        return {'status': 'skipped_backup', 'removed': 0}

    step = snapshot_path.split('.')[-1]
    startrun_path = f"{step}.startrun"
    original_path = snapshot_path + ".original"

    # never overwrite an existing backup
    if os.path.exists(original_path):
        return {'status': 'backup_exists', 'removed': 0}

    before = check_snapshot_zeros(s)
    zero_total = before['zero_dm'] + before['zero_gas'] + before['zero_star']

    # fixing zero-mass particles, not NaNs.
    if zero_total == 0:
        return {'status': 'clean', 'removed': 0, 'before': before}

    # renaming the untouched snapshot to .original before writing anything new
    os.rename(snapshot_path, original_path)

    try:
        s_raw = pn.load(original_path)
        clean = s_raw[s_raw['mass'] != 0]
        clean.write(filename=snapshot_path, fmt=pn.tipsy.TipsySnap)
    except Exception:
        # if writing failed before a replacement snapshot exists, restore the original name
        if not os.path.exists(snapshot_path) and os.path.exists(original_path):
            os.rename(original_path, snapshot_path)
        raise

    startrun_status = 'not_found'
    if os.path.exists(startrun_path):
        with open(startrun_path, 'r') as f:
            content = f.read()
        content = content.replace(
            f"ic_filename = {original_path}",
            f"ic_filename = {snapshot_path}"
        )
        content = content.replace(
            f"ic_filename = {snapshot_path}.clean",
            f"ic_filename = {snapshot_path}"
        )
        with open(startrun_path, 'w') as f:
            f.write(content)
        startrun_status = 'updated'

    # reloading the newly written snapshot and independently verify the repair
    s_fixed = load_snapshot(snapshot_path)
    after = check_snapshot_zeros(s_fixed)
    remaining_zeros = after['zero_dm'] + after['zero_gas'] + after['zero_star']

    return {
        'status': 'fixed' if remaining_zeros == 0 else 'verification_failed',
        'removed': zero_total,
        'before': before,
        'after': after,
        'backup': original_path,
        'startrun': startrun_status,
    }


def fix_all_snapshots_zeros():
    # matching only normal snapshots ending in exactly six digits
    # excluding files that have *.original
    snapshots = sorted(glob.glob('*.[0-9][0-9][0-9][0-9][0-9][0-9]'))

    if not snapshots:
        print("No snapshots found in the current directory.")
        return

    print(f"Checking {len(snapshots)} snapshots and fixing zero-mass particles when needed:\n")

    clean_steps = []
    fixed_steps = []
    nan_steps = []
    backup_conflicts = []
    verification_failures = []
    error_steps = []

    for snapshot_path in snapshots:
        step = snapshot_path.split('.')[-1]

        try:
            s = load_snapshot(snapshot_path)
            before = check_snapshot_zeros(s)
        except Exception as exc:
            print(f"{step}  ERROR: could not load/check snapshot ({exc})")
            error_steps.append(step)
            continue

        zero_total = before['zero_dm'] + before['zero_gas'] + before['zero_star']

        # NaNs are only reported, if any
        if before['nan_mass'] > 0:
            print(f"{step}  NaN FOUND -> NOT MODIFIED ({before['nan_mass']} NaN mass particles)")
            nan_steps.append(step)
            continue

        if zero_total == 0:
            print(f"{step}  OK")
            clean_steps.append(step)
            continue

        original_path = snapshot_path + '.original'
        if os.path.exists(original_path):
            print(f"{step}  ZERO MASS FOUND -> NOT MODIFIED")
            print(f"existing backup: {original_path}")
            print("refusing to overwrite existing .original backup")
            backup_conflicts.append(step)
            continue

        print(f"{step}  ZERO MASS FOUND -> fixing...")
        print(f"zero-mass DM:{before['zero_dm']}")
        print(f"zero-mass gas: {before['zero_gas']}")
        print(f"zero-mass stars: {before['zero_star']}")

        try:
            result = fix_snapshot_zeros(s, snapshot_path)
        except Exception as exc:
            print(f"    ERROR while fixing: {exc}")
            error_steps.append(step)
            continue

        if result['status'] == 'fixed':
            print(f"removed: {result['removed']} particles")
            print(f"backup: {result['backup']}")
            if result['startrun'] == 'updated':
                print(f"startrun: {step}.startrun updated")
            else:
                print(f"startrun: {step}.startrun not found")
            print("    FIX VERIFIED")
            fixed_steps.append(step)
        else:
            after = result.get('after', {})
            print("WARNING: repair verification failed")
            if after:
                print(f"remaining zero-mass DM: {after['zero_dm']}")
                print(f"remaining zero-mass gas: {after['zero_gas']}")
                print(f"remaining zero-mass stars: {after['zero_star']}")
            verification_failures.append(step)

    print("\n--------------------------------")
    print(f"Snapshots checked: {len(snapshots)}")
    print(f"Already clean: {len(clean_steps)}")
    print(f"Snapshots fixed: {len(fixed_steps)}")
    print(f"NaN warnings: {len(nan_steps)}")
    print(f"Backup conflicts: {len(backup_conflicts)}")
    print(f"Verification failures: {len(verification_failures)}")
    print(f"Load/fix errors: {len(error_steps)}")

    if fixed_steps:
        print("\nFixed:")
        for step in fixed_steps:
            print(step)

    if nan_steps:
        print("\nNaNs found; not modified:")
        for step in nan_steps:
            print(step)

    if backup_conflicts:
        print("\nExisting .original backup; not modified:")
        for step in backup_conflicts:
            print(step)

    if verification_failures:
        print("\nRepair verification failed:")
        for step in verification_failures:
            print(step)

    if error_steps:
        print("\nLoad/fix errors:")
        for step in error_steps:
            print(step)

    print("--------------------------------")

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
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "mathtext.fontset": "cm",
    })

    sims = [
        {'path': '/mnt/data0/jmeftah/changa_runs/sand_boxes/notmy_pioneer', 'label': 'No Kicks', 'color': 'black'},
        {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil0', 'label': 'Aligned, random spin', 'color': 'blue'},
        {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil1', 'label': 'Anti-aligned, random spin', 'color': 'red'},
        {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil2', 'label': 'Random, random spin', 'color': 'green'},
        {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/max_spin/JM_recoil0', 'label': 'Aligned, max spin ', 'color': 'gray'},
        {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/max_spin/JM_recoil1', 'label': 'Anti-aligned, max spin ', 'color': 'purple'},
        {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/max_spin/JM_recoil2', 'label': 'Random, max spin ', 'color': 'orange'}
    ]

    all_halo_mass = []
    for sim in sims:
        sim['halo_mass'] = pd.read_csv(os.path.join(sim['path'], 'halo_masses_from_amiga.csv'))['Mvir']
        sim['BH_halo_mass'] = pd.read_csv(os.path.join(sim['path'], 'BH_masses.csv'))['Mhalo(4)']  / h
        all_halo_mass.append(sim['halo_mass'])
        all_halo_mass.append(sim['BH_halo_mass'])

    combined_halo_mass = pd.concat(all_halo_mass)
    log_min = np.log10(combined_halo_mass.min())
    log_max = np.log10(combined_halo_mass.max())
    bin_edges = np.logspace(log_min, log_max, n + 1)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])  # geometric mean for log bins
    log_bin_centers = np.log10(bin_centers)  # x-axis is now log10(M_halo/M_sun)

    def count_in_bins(m, e, label=''):
        counts = []
        for i, (lo, hi) in enumerate(zip(e[:-1], e[1:])):
            if i == 0:
                c = np.count_nonzero((m >= lo) & (m <= hi))
            else:
                c = np.count_nonzero((m > lo) & (m <= hi))
            print(f"  {label} bin [{lo:.3e}, {hi:.3e}]: {c}")
            counts.append(c)
        return np.array(counts)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=200)

    for sim in sims:
        print(f"{sim['label']}")
        count_all = count_in_bins(sim['halo_mass'], bin_edges, label='ALL')
        count_BH = count_in_bins(sim['BH_halo_mass'], bin_edges, label='BH')
        occ_frac = np.where(count_all > 0, count_BH / count_all, 0.0)

        ax.plot(log_bin_centers, occ_frac, lw=2, color=sim['color'], label=sim['label'], zorder=2)
        ax.scatter(log_bin_centers, occ_frac, s=60, color=sim['color'], zorder=3)

    ax.text(
        0.98, 0.98,
        'z = 5',
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=18,
        bbox=dict(facecolor='white', alpha=0.0, edgecolor='none'))

    ax.set_yscale('symlog', linthresh=0.01)
    ax.set_xlabel(r'$\log_{10}(M_\mathrm{halo}/M_\odot)$', fontsize=13)
    ax.set_ylabel('BH occupation fraction', fontsize=13)
    ax.set_ylim(-0.005, 1.15)
    ax.legend()
    plt.tight_layout()
    plt.show()

def write_BH_csv_from_amiga_stat(snapshot):
    stat = read_amiga_stat(snapshot)
    stat['Grp'] = stat['Grp'].astype(int)
    stat['Mvir'] = stat['Mvir'].astype(float)

    s = load_snapshot(snapshot)
    bhs = s.star[s.star['tform'] < 0]

    halos = np.unique(bhs['amiga.grp'])
    halos = halos[halos != 0]

    rows = []

    for halo_id in halos:
        row = stat[stat['Grp'] == int(halo_id)]

        if row.empty:
            print(f"WARNING: halo {halo_id} not found")
            continue

        rows.append({
            'halo_id': int(halo_id),
            'Mvir': row['Mvir'].values[0],
            'n_BH': np.count_nonzero(bhs['amiga.grp'] == halo_id)
        })

    df = pd.DataFrame(rows)
    print(df)
    df.to_csv('BH_masses_from_amiga_stat.csv', index=False)
    print("saved BH_masses_from_amiga_stat.csv")
  

def plot_of_all_new(n):
    
    sims = [
    {'path': '/mnt/data0/jmeftah/changa_runs/sand_boxes/notmy_pioneer', 'label': 'No kicks', 'color': 'black'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil0', 'label': 'Aligned, spin magnitude: random','color': 'blue'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil1', 'label': 'Anti-aligned, spin magnitude: random', 'color': 'red'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/rand_spin/JM_recoil2', 'label': 'Random, spin magnitude: random', 'color': 'green'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/max_spin/JM_recoil0', 'label': 'Aligned, spin magnitude: maximum','color': 'gray'},
    {'path': '/mnt/data0/jmeftah/changa_runs/mendel_runs/max_spin/JM_recoil1', 'label': 'Anti-aligned, spin magnitude: maximum','color': 'purple'},
    ]

    all_halo_mass = []

    for sim in sims:
        sim['halo_mass'] = pd.read_csv(os.path.join(sim['path'], 'halo_masses_from_amiga.csv'))['Mvir']
        sim['BH_halo_mass'] = pd.read_csv(os.path.join(sim['path'], 'BH_masses_from_amiga_stat.csv'))['Mvir']

        all_halo_mass.append(sim['halo_mass'])
        all_halo_mass.append(sim['BH_halo_mass'])

    combined_halo_mass = pd.concat(all_halo_mass)

    log_min = np.log10(combined_halo_mass.min())
    log_max = np.log10(combined_halo_mass.max())

    bin_edges = np.logspace(log_min, log_max, n + 1)

    # protects against dropping the exact max value because of roundoff
    bin_edges[0] = combined_halo_mass.min()
    bin_edges[-1] = combined_halo_mass.max()
    bin_edges[-1] = np.nextafter(bin_edges[-1], np.inf)

    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])

    def count_in_bins(m, e, label=''):
        counts = []

        for i, (lo, hi) in enumerate(zip(e[:-1], e[1:])):
            if i == 0:
                c = np.count_nonzero((m >= lo) & (m <= hi))
            else:
                c = np.count_nonzero((m > lo) & (m <= hi))

            print(f"  {label} bin [{lo:.3e}, {hi:.3e}]: {c}")
            counts.append(c)

        return np.array(counts)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=200)

    for sim in sims:
        print(f"\n{sim['label']}")

        count_all = count_in_bins(sim['halo_mass'], bin_edges, label='ALL')
        count_BH = count_in_bins(sim['BH_halo_mass'], bin_edges, label='BH')

        occ_frac = np.where(count_all > 0, count_BH / count_all, 0.0)

        ax.plot(bin_centers, occ_frac, lw=2, color=sim['color'], label=sim['label'], zorder=2)
        ax.scatter(bin_centers, occ_frac, s=60, color=sim['color'], zorder=3)

    ax.text(
        0.98, 0.98,
        'z = 5',
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=18,
        bbox=dict(facecolor='white', alpha=0.0, edgecolor='none')
    )

    ax.set_xscale('log')
    ax.set_yscale('symlog', linthresh=0.01)

    ax.set_xlabel(r'$M_\mathrm{halo}\ [M_\odot]$', fontsize=13)
    ax.set_ylabel('BH occupation fraction', fontsize=13)

    ax.set_ylim(-0.05, 1.15)
    ax.legend()

    plt.tight_layout()
    plt.show()

# plot number of mergers 
def plot_merger_counts():
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "mathtext.fontset": "cm",
    })

    groups = [
        {'name': 'No Kicks', 'bars': [('No kicks', 9, 'black')]},
        {'name': 'Random spin\nmagnitude', 'bars': [('Aligned', 7, 'blue'), ('Anti-aligned', 3, 'red'), ('Random', 3, 'green')]},
        {'name': 'Max spin\nmagnitude', 'bars': [('Aligned', 5, 'gray'), ('Anti-aligned', 2, 'purple')]},
    ]

    bar_width = 0.6
    inner_gap = 0.15
    group_gap = 1.0

    x_ticks = []
    x_tick_labels = []
    legend_handles = {}

    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=200)

    x_cursor = 0.0
    for group in groups:
        n = len(group['bars'])
        group_width = n * bar_width + (n - 1) * inner_gap
        start_x = x_cursor
        for i, (label, count, color) in enumerate(group['bars']):
            x = start_x + i * (bar_width + inner_gap)
            bar = ax.bar(x, count, width=bar_width, color=color, edgecolor='black', linewidth=0.8)
            if color not in legend_handles:
                legend_handles[color] = (bar[0], label)
        group_center = start_x + group_width / 2 - bar_width / 2
        x_ticks.append(group_center)
        x_tick_labels.append(group['name'])
        x_cursor = start_x + group_width + group_gap

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels, fontsize=12)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, max(c for g in groups for _, c, _ in g['bars']) * 1.2)

    ax.text(
        0.98, 1.06,
        'z = 5',
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=18,
        bbox=dict(facecolor='white', alpha=0.0, edgecolor='none'))

    ax.set_ylabel('Number of mergers', fontsize=13)
    handles = [v[0] for v in legend_handles.values()]
    labels = [v[1] for v in legend_handles.values()]
    ax.legend(handles, labels, frameon=False, fontsize=11)
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
    check_all_snapshots_zeros()

elif command == "fix_zeros":
    fix_all_snapshots_zeros()

elif command == "write_halo_csv_amiga":
    write_csvs_from_amiga_stat(snapshot)    

# elif command == "write_csv_amiga":
  #  write_csvs_from_amiga_stat(snapshot)
    # write_BH_halo_masses_from_amiga_stat(snapshot)

elif command == "plot_of_all":
    n = int(sys.argv[2].replace('-n', ''))
    plot_of_combined(n)

elif command == "write_BH_csv_amiga":
    write_BH_csv_from_amiga_stat(snapshot)

elif command == "plot_of_all_new":
    n = int(sys.argv[2].replace('-n', ''))
    plot_of_all_new(n)

elif command == "plot_mergers_counts":
    plot_merger_counts()


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
    print("python master_functions.py fix_zeros — scan all snapshots and safely repair only those with zero-mass particles")
