import os
import threading
import requests
import time
import io
from PIL import Image
from rgbmatrix import graphics
from scroll_utils import ScrollText
from datetime import datetime
from base_widget import Widget

class WeatherWidget(Widget):
    def __init__(self, font_sm, blue, yellow):
        self.font_sm = font_sm
        self.blue = blue
        self.yellow = yellow
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.city = os.getenv("CITY", "Lanciano")
        self.data = {"temp": "--", "text": "Loading...", "icon": None}
        self.scroller = ScrollText(self.data["text"], font_sm, yellow, 60, 16, 64, speed=0.4)
        self.stop_event = threading.Event()
        self.thread = None

    def fetch_background(self):
        URL = f"http://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q={self.city}&aqi=no"
        TARGET_ICON_SIZE = (14, 14)
        while not self.stop_event.is_set():
            try:
                response = requests.get(URL, timeout=10).json()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Weather: Fetched - {response['current']['condition']['text']}, {response['current']['temp_c']}C")
                self.data["temp"] = f"{response['current']['temp_c']}C"
                self.data["text"] = response['current']['condition']['text']
                icon_url = "https:" + response['current']['condition']['icon']
                icon_res = requests.get(icon_url, timeout=5)
                with Image.open(io.BytesIO(icon_res.content)).convert('RGBA') as img:
                    img = img.resize(TARGET_ICON_SIZE, Image.Resampling.LANCZOS)
                    bg = Image.new('RGBA', TARGET_ICON_SIZE, (0, 0, 0, 255))
                    bg.paste(img, (0, 0), img)
                    self.data["icon"] = bg.convert('RGB')
                for _ in range(300):
                    if self.stop_event.is_set(): break
                    time.sleep(1)
            except Exception:
                for _ in range(60):
                    if self.stop_event.is_set(): break
                    time.sleep(1)

    def activate(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.fetch_background, daemon=True)
            self.thread.start()

    def deactivate(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=2)
            self.thread = None

    def update(self, data, timestamp):
        # Update scroller with internal data updated by thread
        self.scroller.update_text(self.data["text"])

    def draw(self, canvas, timestamp):
        if self.data["icon"]: canvas.SetImage(self.data["icon"], 2, 45)
        graphics.DrawText(canvas, self.font_sm, 16, 50, self.blue, self.data["temp"])
        self.scroller.draw(canvas)

    @property
    def should_show(self):
        return True

    @property
    def priority(self):
        return 0
