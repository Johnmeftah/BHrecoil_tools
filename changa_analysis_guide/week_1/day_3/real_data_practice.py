# 1. load a snapshot
# 2. call .families() on it — returns a list of family objects (gas, dm, star), stored as particles_type
# 3. write a for loop over particles_type
# 4. inside the loop, for each particle (family), print its name and its particle count
#    (hint: len(snapshot[particle]) gives you the count for that specific family)
# 5. inside the same loop, add an if/else: if particle_count > 1000000, print "Large family",
#    otherwise print "Small family"

# 1
import pynbody as pn
snapshot = pn.load("/home/jmeftah/python/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000136")

# 2
particles_type = snapshot.families()

# 3, 4, & 5
for particle in particles_type: #3
    particle_count = len(snapshot[particle]) #4
    print(f"Particle type: {particle}, count {particle_count}")

    #5 
    if particle_count > 1000000:
        print("Large family")
    else:
        print("Small family")
  


