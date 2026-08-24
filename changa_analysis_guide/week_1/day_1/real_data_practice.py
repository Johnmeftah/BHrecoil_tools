import pynbody as pn 

# load the snapshot 
snapshot = pn.load("/home/jmeftah/python/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000128")

print(type(snapshot)) # confirm snapshot is loaded correctly 
print(len(snapshot)) # total particles count in the snapshot
 