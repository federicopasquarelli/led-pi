import threading
import requests
import time
import io
from PIL import Image
from datetime import datetime
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import config  # Import the file you just created
from scroll_utils import ScrollText

# ... [Keep your existing RGBMatrixOptions and Font setup here] ...
# 1. Hardware Configuration Optimized for Pi 3 Stability
options = RGBMatrixOptions()
options.rows = config.SIZE
options.cols = config.SIZE
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = config.HARDWARE_MAPPING

# Performance Tweaks to stop "flashiness"
options.pwm_bits = 11               # Lower bit-depth = higher refresh rate


matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# 2. Font Setup (Absolute Path)
# Ensure these files exist in this exact directory
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
# Shared Global Data
# Shared Global Data
weather_data = {"temp": "--", "text": "Loading...", "icon": None}
music_scroller = ScrollText("Artist - Title", font_sm, yellow, 60, 16, 60, speed=0.2)

def fetch_weather_background():
    URL = f"http://api.weatherapi.com/v1/current.json?key={config.WEATHER_API_KEY}&q={config.CITY}&aqi=no"
    
    # Define the target icon size (matches your layout)
    TARGET_ICON_SIZE = (14, 14)
    
    while True:
        try:
            response = requests.get(URL, timeout=10).json()
            
            # 1. Update Text Data
            weather_data["temp"] = f"{response['current']['temp_c']}C"
            weather_data["text"] = response['current']['condition']['text']
            
            # 2. Download and Process Icon
            icon_url = "https:" + response['current']['condition']['icon']
            icon_res = requests.get(icon_url, timeout=5)
            
            # Open image and keep it in RGBA format (handles transparency)
            with Image.open(io.BytesIO(icon_res.content)).convert('RGBA') as img:
                # Resize the icon first
                img = img.resize(TARGET_ICON_SIZE, Image.Resampling.LANCZOS)
                
                # Create a solid black background of the same size
                # 'RGBA' with (0,0,0,255) ensures it's opaque black
                bg = Image.new('RGBA', TARGET_ICON_SIZE, (0, 0, 0, 255))
                
                # Paste the icon onto the black background. 
                # The third argument 'img' acts as the mask (crucial for transparency).
                bg.paste(img, (0, 0), img)
                
                # Convert the final composite to RGB for the matrix library
                weather_data["icon"] = bg.convert('RGB')
            
            time.sleep(300)  # Update every 5 minutes
        except Exception as e:
            print(f"Weather Icon Error: {e}")
            time.sleep(60)

t = threading.Thread(target=fetch_weather_background, daemon=True)
t.start()

try:
    while True:
        now = datetime.now()

        # Strings
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        day_str = now.strftime("%A")
        status_str = weather_data["text"]
        temp_str = weather_data["temp"]

        canvas.Clear()

        # --- LAYOUT (64x64) ---
        # 1. Day
        graphics.DrawText(canvas, font_md, 2, 15, orange, day_str)

        # 2. Date (Below Day)
        graphics.DrawText(canvas, font, 2, 25, white, date_str)
        
        # 3. Time (Below Date)
        graphics.DrawText(canvas, font, 2, 37, green, time_str)
        
        # music_scroller.update_text(f"testokjfsdjhfsdoifsjhosdjoifsdjofijsodijfosijfoisjdofjosdijfoisdjfoij oijsdofijfdoijfoijifjsoifs")
        # music_scroller.draw(canvas)
        
        # 4. Icon (Middle-Left)
        if weather_data["icon"]:
            canvas.SetImage(weather_data["icon"], 2, 45)

        # 5. Temp (Middle-Right, next to icon)
        graphics.DrawText(canvas, font_sm, 16, 50, blue, temp_str)

        # 6. Weather Text (Bottom)
        graphics.DrawText(canvas, font_sm, 16, 60, yellow, status_str)
        # music_scroller.update_text(status_str)
        # music_scroller.draw(canvas)

        canvas = matrix.SwapOnVSync(canvas)

except KeyboardInterrupt:
    matrix.Clear()