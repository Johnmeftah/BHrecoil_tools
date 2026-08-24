Day 3: loops (for & while).

Today, we will:
1. load a real Changa snapshot with pynbody
2. call .families() on it — returns a list of family objects (gas, dm, star), stored as particles_type
3. write a for loop over particles_type
4. inside the loop, for each particle (family), print its name and its particle count
(hint: len(snapshot[particle]) gives you the count for that specific family)
5. inside the same loop, add an if/else: if particle_count > 1000000, print "Large family", otherwise print "Small family"