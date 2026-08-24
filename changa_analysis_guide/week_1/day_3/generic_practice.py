# writing a list of 5 numbers, let's say representing particle masses 

# list particles mass
particles_mass_list = [1,2,3,4,5]

# for loop it that way it prints each number in the list, add an if statement inside the loop

for mass in particles_mass_list: # the loop
    print(f"particle mass {mass}")

# if condition 
if mass > 6:
    print(f"particle mass is heavy")
else:
    print(f"particle mass is light")

# now write a while loop and make it break at a specific limit 
# note that this will NOT print anything
count = 10 
while count < 0: # this is false, 10 is NOT < 0
    print(count)
    count += 1

new_count = 0
while new_count < 10:
    print(new_count)
    new_count += 1

# now new count is gonna print from 0-9