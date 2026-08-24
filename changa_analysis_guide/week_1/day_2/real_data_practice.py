import pynbody as pn 

# loading the snapshot 
snapshot = pn.load("/home/jmeftah/python/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000128")


# storing particle count 
num_particles = len(snapshot)

# checking snaposhot's size 

if num_particles > 1e7:
    print("large snapshot")
else:
    print("small snapshot")

# checking for stars 
# use snapshot.stars 

if len(snapshot.stars) > 0:
    print("snapshot has stars")
else:
     print("snapshot has no stars")

