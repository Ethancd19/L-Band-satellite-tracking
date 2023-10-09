import time
import math
import busio
import board
from py_qmc5883l import QMC5883L
import adafruit_ssd1306

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
sensor = QMC5883L()

def draw_progress_bar(percentage):
    bar_width = 120
    bar_height = 8
    border_thickness = 1
    x_start = (oled.width - bar_width) // 2
    y_start = oled.height - bar_height - 2

    oled.fill_rect(x_start, y_start, bar_width, bar_height, 0)  # Clear the area
    oled.rect(x_start, y_start, bar_width, bar_height, 1)  # Draw border

    fill_width = int((bar_width - 2 * border_thickness) * percentage)
    oled.fill_rect(x_start + border_thickness, y_start + border_thickness, fill_width, bar_height - 2 * border_thickness, 1)
    oled.show()

# Variables for calibration
max_x = float('-inf')
max_y = float('-inf')
min_x = float('inf')
min_y = float('inf')

DECLINATION = -8.5 

# Clear display
oled.fill(0)
oled.show()

# Initiate calibration
print("Starting calibration...")
oled.text("Calibrating...", 0, 0, 1)

calibration_duration = 30
start_time = time.time()

while time.time() - start_time < calibration_duration:
    elapsed_time = time.time() - start_time
    percentage = elapsed_time / calibration_duration

    draw_progress_bar(percentage)

    x, y, z = sensor.get_magnet_raw()
    max_x = max(max_x, x)
    min_x = min(min_x, x)
    max_y = max(max_y, y)
    min_y = min(min_y, y)
    time.sleep(0.1)

offset_x = (max_x + min_x) / 2
offset_y = (max_y + min_y) / 2

print("Calibration complete.")
oled.fill(0)
oled.text("Calibration complete!", 0, 0, 1)
oled.show()
time.sleep(2)
oled.fill(0)

# Function to get calibrated magnetometer values
def get_calibrated_data():
    x, y, z = sensor.get_magnet_raw()
    return x - offset_x, y - offset_y

# Function to get bearing
def get_bearing():
    x, y = get_calibrated_data()
    bearing = math.degrees(math.atan2(y, -x))  # Notice -x
    bearing += DECLINATION  # Adjust for declination here
    if bearing < 0:
        bearing += 360.0
    return bearing

def get_cardinal_direction(bearing):
    """Return the 2-letter cardinal direction based on the bearing."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int(((bearing + 22.5) % 360) / 45)
    return directions[index]


# Display bearing
# Display bearing
while True:
    bearing = get_bearing()
    direction = get_cardinal_direction(bearing)
    oled.fill(0)  # Clear screen
    text = "Bearing: {:.2f}°".format(bearing)
    oled.text(text, 0, 0, 1)
    oled.text(direction, 0, 15, 1)  # Display cardinal direction below the bearing
    oled.show()
    time.sleep(1)