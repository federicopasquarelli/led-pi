import os
import threading
import time
from datetime import datetime
from socketIO_client import SocketIO
from rgbmatrix import graphics
from scroll_utils import ScrollText
from base_widget import Widget

class VolumioWidget(Widget):
    def __init__(self, font_sm, font_md, blue, white, yellow, on_state_change):
        self.font_sm = font_sm
        self.font_md = font_md
        self.blue = blue
        self.white = white
        self.yellow = yellow
        self.red = graphics.Color(255, 0, 0)
        self.on_state_change = on_state_change
        self.last_pause_time = None
        self.volumio_host = os.getenv("VOLUMIO_HOST")
        self.data = {
            "text": "stop",
            "status": "stop",
            "seek": 0,
            "duration": 0,
            "volume": None,
            "volume_update_time": 0,
            "last_update": time.time()
        }
        # Use font_md for track scrolling
        self.scroller = ScrollText(self.data["text"], font_md, yellow, 54, 2, 62, speed=0.5)
        self.thread = threading.Thread(target=self.run_client, daemon=True)
        self.thread.start()

    def run_client(self):
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Volumio: Connecting to {self.volumio_host}:3000...")
                socketIO = SocketIO(self.volumio_host, 3000)
                
                def on_connect():
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Volumio: Connected! Fetching initial state...")
                    socketIO.emit('getState')

                def on_disconnect():
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Volumio: Disconnected.")
                    self.data["status"] = "stop"
                    self.data["text"] = "stop"
                    self.last_pause_time = None
                    self.on_state_change("stop")

                def on_push_state(*args):
                    data = args[0]
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Volumio: Received state update - Status: {data.get('status', 'N/A')}, Artist: {data.get('artist', 'N/A')}, Title: {data.get('title', 'N/A')}, Duration: {data.get('duration', 'N/A')}, Seek: {data.get('seek', 'N/A')}, Volume: {data.get('volume', 'N/A')}, Service: {data.get('service', 'N/A')}")
                    
                    new_status = data.get('status', 'stop')
                    self.data["status"] = new_status
                    self.data["seek"] = data.get('seek', 0)
                    self.data["duration"] = data.get('duration', 0)
                    self.data["last_update"] = time.time()

                    # Handle Volume change notification
                    new_volume = data.get('volume', 0)
                    if new_volume != self.data["volume"]:
                        # Only show if it's a real change (not the initial state fetch)
                        if self.data["volume"] is not None:
                            self.data["volume_update_time"] = time.time()
                        self.data["volume"] = new_volume

                    if new_status in ['play', 'pause']:
                        artist = data.get('artist', 'Unknown Artist')
                        title = data.get('title', 'Unknown Title')
                        self.data["text"] = f"{artist} - {title}"
                        
                        if new_status == 'play':
                            self.last_pause_time = None
                            self.on_state_change("play")
                        elif new_status == 'pause':
                            if self.last_pause_time is None:
                                self.last_pause_time = time.time()
                            self.on_state_change("pause")
                    else:
                        self.data["text"] = "stop"
                        self.last_pause_time = None
                        self.on_state_change("stop")

                socketIO.on('connect', on_connect)
                socketIO.on('disconnect', on_disconnect)
                socketIO.on('pushState', on_push_state)
                socketIO.wait()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Volumio: Error - {e}. Retrying in 60 seconds...")
                self.data["status"] = "stop"
                self.data["text"] = "stop"
                self.last_pause_time = None
                self.on_state_change("stop")
                time.sleep(60)

    def activate(self): pass
    def deactivate(self): pass

    def update(self, data, timestamp):
        self.scroller.update_text(self.data["text"])
        
        # Handle pause timeout (return to weather after 5 minutes)
        if self.data["status"] == 'pause' and self.last_pause_time:
            if timestamp - self.last_pause_time > 300:
                self.on_state_change("stop")
                self.last_pause_time = None

    def _draw_play_icon(self, canvas, x, y, color):
        # Simple 4x6 triangle
        graphics.DrawLine(canvas, x, y, x, y + 5, color)
        graphics.DrawLine(canvas, x + 1, y + 1, x + 1, y + 4, color)
        graphics.DrawLine(canvas, x + 2, y + 2, x + 2, y + 3, color)
        graphics.DrawLine(canvas, x + 3, y + 2, x + 3, y + 3, color)

    def _draw_pause_icon(self, canvas, x, y, color):
        # Two 2-pixel wide bars
        graphics.DrawLine(canvas, x, y, x, y + 5, color)
        graphics.DrawLine(canvas, x + 1, y, x + 1, y + 5, color)
        graphics.DrawLine(canvas, x + 3, y, x + 3, y + 5, color)
        graphics.DrawLine(canvas, x + 4, y, x + 4, y + 5, color)

    def draw(self, canvas, timestamp):
        # Determine color based on status
        current_color = self.red if self.data["status"] == 'pause' else self.blue

        # Icon Header
        if self.data["status"] == 'play':
            self._draw_play_icon(canvas, 2, 38, self.blue)
        else:
            self._draw_pause_icon(canvas, 2, 38, current_color)
        
        # Artist - Title (Scrolling)
        self.scroller.draw(canvas)
        
        # Display Volume or Time Progress
        if timestamp - self.data["volume_update_time"] < 10:
            # Show Volume
            vol_str = f"VOL: {self.data['volume']}/100"
            graphics.DrawText(canvas, self.font_sm, 10, 44, current_color, vol_str)
        elif self.data["duration"] > 0:
            # Show Time Progress
            # Interpolate current seek position
            elapsed_since_update = (timestamp - self.data["last_update"]) if self.data["status"] == 'play' else 0
            curr_ms = self.data["seek"] + (elapsed_since_update * 1000)
            curr_s = int(curr_ms / 1000)
            tot_s = int(self.data["duration"])
            
            # MM:SS / MM:SS
            time_str = f"{curr_s//60:02}:{curr_s%60:02} / {tot_s//60:02}:{tot_s%60:02}"
            
            # Position next to icon (Icon is at x=2, y=38)
            graphics.DrawText(canvas, self.font_sm, 10, 44, current_color, time_str)
