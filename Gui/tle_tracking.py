import re

# Example list of TLEs
tle_list = [
    "ISS (ZARYA)             ",
    "1 25544U 98067A   21108.51781045  .00001884  00000-0  44291-4 0  9998",
    "2 25544  51.6447 339.3909 0001602 157.5906 348.5798 15.48909983286163",
    "FLOCK 4P-20             ",
    "1 45855U 20008S   21108.21758105  .00001027  00000-0  56803-4 0  9995",
    "2 45855  97.4271 231.6195 0001505  85.4804 274.6522 15.12490638 25477"
]

# Initialize empty arrays for satellite names and corresponding TLE data
sat_names = []
sat_tles = []

# Iterate through TLE list and extract satellite names
for i in range(len(tle_list)):
    # Check if the line contains a satellite name (letters followed by parentheses)
    if re.match(r"[a-zA-Z]+\s*\(\w*\)\s*", tle_list[i]):
        # If we've already found a satellite name, append a copy of the current TLE data to the sat_tles array
        if i > 0:
            sat_tles.append(tle_list[i-2:i+1][:])
        # Add the current satellite name to the sat_names array
        sat_names.append(tle_list[i].strip())
    # If we're at the end of the TLE list, append a copy of the last set of TLE data to the sat_tles array
    elif i == len(tle_list) - 1:
        sat_tles.append(tle_list[i-2:i+1][:])

# Print the satellite names and corresponding TLE data
for i in range(len(sat_names)):
    print("Satellite Name: " + sat_names[i])
    print("TLE Data: ")
    for tle in sat_tles[i]:
        print(tle)
    print("--------------")