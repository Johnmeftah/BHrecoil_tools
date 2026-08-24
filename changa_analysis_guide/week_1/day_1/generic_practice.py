# integers & float 
num_particles = 50000000
particle_mass = 2.3e6 

# strings 
sim_name = "Aligned BHs with maximum spin"

# booleans 
has_BHs = True 

# checking types 
print(type(num_particles))
print(type(particle_mass))
print(type(sim_name))
print(type(has_BHs))

# basic math with variables 
total_mass = num_particles * particle_mass
print(f'Total mass: {total_mass}')
print(f'Number of particles in this sim: {num_particles}')
print(f'The sim name is: {sim_name}')
print(f'Does the sim have BHs?: {has_BHs}')