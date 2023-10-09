import compass
import gps
import time

offsets = compass.calibrate_compass()
gps_instance = gps.init_gps()

while True:
    bearing = compass.get_bearing(*offsets)
    lat, lon = gps.get_coordinates(gps_instance)

    print(f"Bearing: {bearing:.2f}°")
    if lat and lon:
        print(f"Latitude: {lat:.6f}, Longitude: {lon:.6f}")
    else:
        print("Waiting for fix...")
    time.sleep(1)