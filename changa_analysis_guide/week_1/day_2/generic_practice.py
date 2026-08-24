particle_mass = 2.3e6 
if particle_mass > 1e7: # if this is true 
    print("high mass particle")
elif particle_mass > 1e6: # if this frist condition is false and this is true
    print("medium mass particle")
else: # otherwise 
    print("low mass particle")


num_particles = 30687651
has_BHs = True 

if num_particles > 1e7 and has_BHs:
    print("large sim with a BH present")

sim_type = "cosmological"

if sim_type == "cosmological":
    print("sim type is cosmological")
    