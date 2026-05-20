import os
import time
from datetime import datetime
from dotenv import load_dotenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from weather_widget import WeatherWidget
from volumio_widget import VolumioWidget
from widget_manager import WidgetManager

# Load environment variables
load_dotenv()

# 1. Hardware Configuration
options = RGBMatrixOptions()
options.rows = int(os.getenv("SIZE", "64"))
options.cols = int(os.getenv("SIZE", "64"))
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = os.getenv("HARDWARE_MAPPING", "adafruit-hat")
options.pwm_bits = 11

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# 2. Font Setup
base_path = "./fonts/"
font = graphics.Font()
font.LoadFont(base_path + "6x10.bdf")
font_sm = graphics.Font()
font_sm.LoadFont(base_path + "4x6.bdf")
font_md = graphics.Font()
font_md.LoadFont(base_path + "5x7.bdf")

# 3. Colors
white = graphics.Color(255, 255, 255)
orange = graphics.Color(255, 165, 0)
green = graphics.Color(0, 255, 0)
blue = graphics.Color(0, 100, 255)
yellow = graphics.Color(255, 200, 0)

# Layout configuration
LAYOUT = {
    "pos_1": (2, 11),  # Day
    "pos_2": (2, 21),  # Time
    "pos_3": (2, 30),  # Date
}

# 4. Widget Orchestration
weather_w = WeatherWidget(font_sm, blue, yellow)
volumio_w = VolumioWidget(font_sm, font_md, blue, white, yellow)

# Initialize WidgetManager with Weather as fallback (index 0)
manager = WidgetManager([weather_w, volumio_w])

def get_current_data(now):
    return {
        "day": now.strftime("%A"),
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%d/%m/%Y")
    }

def update_brightness(matrix, now):
    hour = now.hour
    if 0 <= hour < 5:
        brightness = 10
    elif 5 <= hour < 9:
        brightness = 40
    elif 9 <= hour < 19:
        brightness = 70
    else: # 19:00 - 23:59
        brightness = 40
    
    if matrix.brightness != brightness:
        matrix.brightness = brightness

def draw_app(canvas, data, timestamp):
    # Global Clock Layout
    x1, y1 = LAYOUT["pos_1"]
    graphics.DrawText(canvas, font_md, x1, y1, orange, data["day"])
    x2, y2 = LAYOUT["pos_2"]
    graphics.DrawText(canvas, font, x2, y2, green, data["time"])
    x3, y3 = LAYOUT["pos_3"]
    graphics.DrawText(canvas, font_md, x3, y3, white, data["date"])
    
    # Update and Draw Widgets via Manager
    manager.update(data, timestamp)
    manager.draw(canvas, timestamp)

# 5. Main Loop
try:
    while True:
        now = datetime.now()
        timestamp = time.time()
        update_brightness(matrix, now)
        data = get_current_data(now)
        
        canvas.Clear()
        draw_app(canvas, data, timestamp)
        canvas = matrix.SwapOnVSync(canvas)
except KeyboardInterrupt:
    matrix.Clear()
