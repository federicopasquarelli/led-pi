# Project Context: led-py

This project manages a 64x64 RGB LED Matrix display using a Raspberry Pi. It features a clock with weather updates and scrolling Volumio playback information.

## Hardware & Environment
- **Matrix Size**: 64x64 (configured in `config.py`).
- **Hardware Mapping**: `adafruit-hat`.
- **Optimization**: PWM bits are set to 11 for Pi 3 stability to prevent flickering.

## Architecture
- `clock.py`: Main entry point. Handles the display loop, brightness management, and widget orchestration.
- `base_widget.py`: Defines the `Widget` interface for modular display components.
- `weather_widget.py`: Fetches and displays weather data (temp, condition, icon).
- `volumio_widget.py`: Real-time playback info via SocketIO. Features integrated progress/volume text and state-driven colors.
- `scroll_utils.py`: Provides the `ScrollText` class for horizontal scrolling within defined bounds.
- `config.py`: Centralized configuration for API keys, city, and hardware settings.
- `fonts/`: Directory containing `.bdf` font files.

## Engineering Standards
- **Widget Transitions**: Dashboard automatically switches to `VolumioWidget` on 'play' or 'pause' states and returns to `WeatherWidget` only when status is 'stop'.
- **Volumio UI**: 
    - **Header**: Displays a play/pause icon at `(2, 38)` with the current playback time (MM:SS / MM:SS) next to it.
    - **Colors**: Elements turn **Blue** when playing and **Red** when paused.
    - **Volume**: When volume changes, the playback time is temporarily replaced by "VOL: X/100" (in the current state color) for 10 seconds.
    - **Scrolling**: Track info (Artist - Title) scrolls at `y=54` for better readability.
- **Scrolling Behavior**: Text starts at `start_x`, scrolls left, and resets to `end_x` once fully invisible on the left.
- **Weather Updates**: Fetched in a background thread every 5 minutes. Icons are processed into RGBA with a black background before being converted to RGB for the matrix.
- **Layout Integrity**: Maintain the 64x64 grid layout. Day, Date, Time, and widget-specific elements have fixed positions to prevent overlapping.
- **Performance**: Use `SwapOnVSync` for smooth transitions. Avoid heavy processing within the main loop.


Session Id gemini --resume 1c8a05ed-5f07-4bfb-98d6-d8572999d39f