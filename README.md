# led-py: 64x64 LED Matrix Dashboard

A modular dashboard for a 64x64 RGB LED Matrix controlled by a Raspberry Pi. It features a real-time clock, weather updates, and live playback information from a Volumio music server.

## Features
- **Real-time Clock**: Displays Day, Time, and Date with high-visibility fonts.
- **Weather Widget**: Background-fetched weather data (Condition icon, Temperature, and Condition text).
- **Volumio Widget**: Live playback info via SocketIO.
    - Automatic takeover when music is playing or paused.
    - Displays artist and track name with horizontal scrolling.
    - Live progress bar and volume change notifications.
    - Automatic return to Weather widget after 5 minutes of being paused or on 'stop' state.
- **Dynamic Brightness**: Automatically adjusts display brightness based on the time of day.
- **Smooth Transitions**: Utilizes `SwapOnVSync` for flicker-free rendering.

## Hardware Requirements
- **Raspberry Pi** (Pi 3 or newer recommended).
- **64x64 RGB LED Matrix** (P3/P4/P5).
- **Adafruit RGB Matrix HAT** or similar hardware mapping.
- **Power Supply**: Dedicated 5V supply for the LED matrix.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/led-py.git
cd led-py
```

### 2. Install System Dependencies
Ensure you have the `rpi-rgb-led-matrix` library installed. Follow the [official instructions](https://github.com/hzeller/rpi-rgb-led-matrix) to compile the Python bindings.

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy the example environment file and fill in your details:
```bash
cp .env.example .env
```
Edit `.env` with your API keys and configuration:
- `WEATHER_API_KEY`: Get one for free at [WeatherAPI.com](https://www.weatherapi.com/).
- `CITY`: Your city name for weather updates.
- `VOLUMIO_HOST`: The IP address of your Volumio server.
- `SIZE`: 64 (for 64x64 matrix).
- `HARDWARE_MAPPING`: e.g., `adafruit-hat`.

## Usage
Run the main script with root privileges (required for GPIO access):
```bash
sudo python clock.py
```

## Directory Structure
- `clock.py`: Main entry point and display loop.
- `base_widget.py`: Widget interface.
- `weather_widget.py`: Weather data fetching and rendering.
- `volumio_widget.py`: Volumio SocketIO client and rendering.
- `scroll_utils.py`: Text scrolling helper.
- `fonts/`: BDF font files.

## License
[MIT](LICENSE) (or specify your license)
