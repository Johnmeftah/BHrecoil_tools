import pynbody as pn
import numpy as np
import pandas as pd
import sys
from collections import Counter
import matplotlib.pyplot as plt


h = 0.7299  # Hubble param to convert M_sun/h to M_sun

# load snapshot + AHF 
def load_snapshot():
    s = pn.load('pioneer50h243.1536gst1bwK1BH.000384')
    s.physical_units()  # converting code units to physical units 
    return s 

def load_AHF():
    AHF = pd.read_csv('pioneer50h243.1536gst1bwK1BH.000384.z4.584.AHF_halos', sep='\t', header=0)
    return AHF
   



# functions 
# listing the keys in the snapshot
def snap_keys(s):
    print(f"keys inside the snapshot are: {s.loadable_keys()}")

# printing min and max DM particle mass and their ratio
def dm_minmax(s):
    print(f" minimum DM particle mass: {s.dm['mass'].min(): .3e}")
    print(f" max DM particle mass: {s.dm['mass'].max(): .3e}")
    print(f" ratio: {s.dm['mass'].min() / s.dm['mass'].max(): .3e}")

# printing the entire dictionary in AHF
def AHF_keys(AHF):
    print(f"keys inside the AHF are: {AHF.columns.tolist()}")

# finding the total number of halos in AHF
def AHF_halo_info(AHF):
    print(f"total number of halos: {len(AHF)}")

# printing the corrected halo masses and the most and least massive halos
def AHF_halo_mass(AHF):
    AHF = AHF[AHF['#ID(1)'] != 0]
    correct_masses = AHF[AHF['fMhires(38)'] > 0.90][['#ID(1)', 'Mhalo(4)']].copy()
    correct_masses['Mhalo(4)'] = correct_masses['Mhalo(4)'] / h
    ids = correct_masses['#ID(1)']
    masses = correct_masses['Mhalo(4)']
    print(correct_masses.to_string(index=False, formatters={'Mhalo(4)': '{:.3e} M_sun'.format}))
    print(f"most massive:  halo {ids[masses.idxmax()]} with {masses.max():.3e} M_sun")
    print(f"least massive: halo {ids[masses.idxmin()]} with {masses.min():.3e} M_sun")

 

# counting BHs in the snapshot
def BH_count(s):
    bhs = s.star[s.star['tform'] < 0]
    print(f'total number of BHs: {len(bhs)}')

# counting & IDing how many halos have BHs in them
def BH_halos(s, AHF):
    bhs = s.star[s.star['tform'] < 0]  
    bh_grp = bhs['amiga.grp']  # halo ID each BH belongs to
    counts = Counter(bh_grp)   # number of BHs per halo

    for halo_id, n in sorted(counts.items()):
        if halo_id == 0:
            continue  # skip halo 0
        mass = AHF.loc[AHF['#ID(1)'] == halo_id, 'Mhalo(4)'].values[0] / h 
        print(f"halo {halo_id} has {n} BH(s) with {mass:.3e} M_sun")


# checking the mass range of the halos in CSV
def mass_range():
    df = pd.read_csv('halo_masses.csv')
    masses = df['Mhalo(4)'] / h
    print(f"mass range of clean halos (fMhires > 0.90) in halo_masses.csv:") 
    print(f"min mass: {masses.min():.3e} M_sun")
    print(f"max mass: {masses.max():.3e} M_sun")

# writing the full halos + BHs csv (will be used for the occupation fraction plot)
def write_csvs():
    ahf = load_AHF()
    s = load_snapshot()
    correct_masses = ahf[(ahf['#ID(1)'] != 0) & (ahf['fMhires(38)'] > 0.90)][['#ID(1)', 'Mhalo(4)']].copy()
    df = pd.DataFrame({'#ID(1)': correct_masses['#ID(1)'], 'Mhalo(4)': correct_masses['Mhalo(4)']})
    df.to_csv('halo_masses.csv', index=False)

    bhs = s.star[s.star['tform'] < 0]
    counts = Counter(bhs['amiga.grp'])
    BH_halo_id, BH_halo_masses = [], []
    for halo_id, n in sorted(counts.items()):
        if halo_id == 0:
            continue
        row = ahf.loc[ahf['#ID(1)'] == halo_id]
        if row.empty or row['fMhires(38)'].values[0] <= 0.90:
            continue
        mass = row['Mhalo(4)'].values[0] / h
        BH_halo_id.append(halo_id)
        BH_halo_masses.append(mass)

    dfBH = pd.DataFrame({'halo_id': BH_halo_id, 'Mhalo(4)': BH_halo_masses})
    dfBH.to_csv('BH_masses.csv', index=False)
    print("saved halo_masses.csv and BH_masses.csv")

# plotting the occupation fraction of BHs in halos as a function of halo mass
def plot_of(n):
    halo_mass = pd.read_csv('halo_masses.csv')['Mhalo(4)'] / h
    BH_halo_mass = pd.read_csv('BH_masses.csv')['Mhalo(4)']

    log_min = np.floor(np.log10(halo_mass.min()))
    log_max = np.ceil(np.log10(halo_mass.max()))
    bin_edges = np.logspace(log_min, log_max, n + 1)

    def count_in_bins(m, e):
        return np.array([np.count_nonzero((m > lo) & (m <= hi)) for lo, hi in zip(e[:-1], e[1:])])

    count_all = count_in_bins(halo_mass, bin_edges)
    count_BH  = count_in_bins(BH_halo_mass, bin_edges)
    occ_frac  = np.where(count_all > 0, count_BH / count_all, 0.0)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])

    print("all halos per bin:", count_all)
    print("BH  halos per bin:", count_BH)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(bin_centers, occ_frac, lw=2, zorder=2)
    ax.scatter(bin_centers, occ_frac, s=60, zorder=3)
    ax.set_xscale('log')
    ax.set_xlabel(r'$M_\mathrm{halo}\ [M_\odot]$', fontsize=13)
    ax.set_ylabel('BH occupation fraction', fontsize=13)
    ax.set_title(f'BH occupation fraction vs halo mass ({n} bins)', fontsize=13)
    ax.set_ylim(-0.05, 1.05)
    plt.tight_layout()
    plt.show()


# making fancy OF plot
def plot_of_pretty(n):
    halo_mass = pd.read_csv('halo_masses.csv')['Mhalo(4)'] / h
    BH_halo_mass = pd.read_csv('BH_masses.csv')['Mhalo(4)']

    log_min = np.floor(np.log10(halo_mass.min()))
    log_max = np.ceil(np.log10(halo_mass.max()))
    bin_edges = np.logspace(log_min, log_max, n + 1)

    def count_in_bins(m, e, label=''):
        counts = []
        for lo, hi in zip(e[:-1], e[1:]):
            c = np.count_nonzero((m > lo) & (m <= hi))
            print(f"  {label} bin [{lo:.3e}, {hi:.3e}]: {c}")
            counts.append(c)
        return np.array(counts)

    print("ALL halos per bin:")
    count_all = count_in_bins(halo_mass, bin_edges, label='ALL')
    print("BH  halos per bin:")
    count_BH  = count_in_bins(BH_halo_mass, bin_edges, label='BH')

    occ_frac  = np.where(count_all > 0, count_BH / count_all, 0.0)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])


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
        




















# main 
command = sys.argv[1] if len(sys.argv) > 1 else None

if command == "snap_keys":
    snap_keys(load_snapshot())

elif command == "dm_minmax":
    dm_minmax(load_snapshot())

elif command == "AHF_keys":
    AHF_keys(load_AHF())

elif command == "halo_count":
    AHF_halo_info(load_AHF())

elif command == "halo_mass":
    AHF_halo_mass(load_AHF())

elif command == "BH_count":
    BH_count(load_snapshot())

elif command == "BH_halos":
    BH_halos(load_snapshot(), load_AHF())

elif command == "mass_range":
    mass_range() 

elif command == "write_csv":
    write_csvs()    

elif command == "plot_of":
    n = int(sys.argv[2].replace('-n', ''))
    plot_of(n)

elif command == "plot_of_pretty":
    n = int(sys.argv[2].replace('-n', ''))
    plot_of_pretty(n)

elif command == "conv_vkick":
    value = float(sys.argv[2])
    conv_vkick(value)

elif command == "check_hires":
    check_fMhires(load_AHF())   

   

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
    print("python master_functions.py plot_of -n5  — plot BH occupation fraction with n bins")
    print("python master_functions.py plot_of_pretty -n5 — same but with bin counts annotated and color coding") # example with 5 bins for the OF
    print("python master_functions.py conv_vkick <comoving velocity> — convert a kick velocity from code units to km/s")
    print("python master_functions.py check_hires — print fMhires values for the first few halos to verify their values")


    
