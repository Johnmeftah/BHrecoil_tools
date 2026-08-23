# part 1:  functions on real data — (empty parameters)
# write a script from scratch that does the following:
# write a function called load_and_report that takes no parameters (empty ())
# inside the function: hard-code a path to one of your real snapshots, print its total particle count
# call load_and_report() once, at the bottom of the script

import pynbody as pn 

def load_and_report():
    snapshot = pn.load("/home/jmeftah/python/BHrecoil_tools/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000640")
    total_particle_count = len(snapshot)
    print(f"Total particle count in snapshot: {total_particle_count}")
load_and_report()


# part 2: functions on real data — (one parameter)
# write a script from scratch that does the following:
# write a function called load_and_report that takes one parameter, path
# instead of hard-coding the snapshot path inside the function, use path to load whichever snapshot is passed in
# inside the function: load the snapshot from path, and print its total particle count
# call load_and_report() twice, passing in two different real snapshot paths

def load_and_report(path):
    snapshot = pn.load(path)
    total_particle_count = len(snapshot)
    print(f"Total particle count:{total_particle_count}")

# note we're calling 2 snapshots, still not the best way, getting there
load_and_report("/home/jmeftah/python/BHrecoil_tools/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000640")
load_and_report("/home/jmeftah/python/BHrecoil_tools/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000345")

# part 3: functions on real data — (two parameters)
# write a script from scratch that does the following:
# write a function called load_and_report that takes two parameters: path and threshold
# inside the function: load the snapshot from path, get its total particle count,
# then check if that count is greater than threshold — return "large" if so, else return "small"
# call load_and_report() twice with two different real snapshot paths, using 1e7 as the threshold both times
# store each result in a variable, then print both

def load_and_report(path, threshold):
    snapshot = pn.load(path)
    total_particle_count = len(snapshot)
    print(f"Total particle count: {total_particle_count}")

    if total_particle_count > threshold:
        return ("Large snapshot")
    else:
        return ("small snapshot")

result_1 = load_and_report("/home/jmeftah/python/BHrecoil_tools/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000640", 1e7)    
result_2 = load_and_report("/home/jmeftah/python/BHrecoil_tools/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000345", 1e7)

print(f"Snapshot 1 is: {result_1}")
print(f"Snapshot 2 is: {result_2}")

# part 4: functions on real data — (command-line dispatch)
# write a script from scratch that does the following:
# write a function called load_and_report that takes two parameters: path and threshold
# inside the function: load the snapshot from path, get its total particle count,
# then check if that count is greater than threshold — return "large" if so, else return "small"
# set up command = sys.argv[1] if len(sys.argv) > 1 else None (this will be a one time thing you need to write)
# if command == "check": grab sys.argv[2] as path and sys.argv[3] as threshold (convert threshold with float())
# call load_and_report() with those values, and print the result
# else: print a usage message explaining how to use the script

import sys 

path = "/home/jmeftah/python/BHrecoil_tools/changa_analysis_guide/sample_data/JM_recoil0/pioneer50h243.1536gst1bwK1BH.000640"
threshold = 1e7 

def load_and_report(path, threshold):
    snapshot = pn.load(path)
    total_number_of_particles = len(snapshot)
    print (f"Total number of particles: {total_number_of_particles}")

    if total_number_of_particles > threshold:
        return "Large snapshot"
    else:
        return "Small snapshot"

command = sys.argv[1] if len(sys.argv) > 1 else None 

if command == "check_threshold": 
   # path = sys.argv[2] # turn this on if you want to manually check a snapshot by path: py script_name.py check path/to/snap
   # threshold = float(sys.argv[3]) # turn this on if you want to check for a particular threshold py script_name.py check path/to/snap 1e7
    results = load_and_report(path, threshold)
    print(results)
else:
    print("To check the snapshot's threshold, use argument <check_threshold>")