import pynbody as pn 

# loading the snapshot 
snapshot = pn.load("/home/jmeftah/python/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000128")

print(f'Snapshot type: {type(snapshot)}') # checking the type of snapshot
print(f'Total number of particles in this snapshot: {len(snapshot)}') 