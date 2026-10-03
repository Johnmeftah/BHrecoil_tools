import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# known data (our snaps & BH positions)
time = np.array([0, 10, 20])
position = np.array([0, 5, 12])

# make interpolation function
f = interp1d(time, position)

# estimate more points between 0 and 20 
new_time = np.linspace(0, 20, 100)
new_position = f(new_time)


plt.scatter(time, position, label="known snapshots")

# Jillian and I changed this from a line (.plot) to a (.scatter) to better see the figure 
plt.scatter(new_time, new_position, label="interpolated")



plt.xlabel("t")
plt.ylabel("BH position")
plt.legend()
plt.show()
