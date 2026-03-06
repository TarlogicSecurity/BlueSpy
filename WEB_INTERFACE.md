# BlueSpy Web Interface

This is a web-based GUI for the BlueSpy application, which allows you to record audio from Bluetooth devices.

## Features

- Scan for Bluetooth devices
- Connect to devices
- Record audio
- Manage recordings (play, download, delete)
- View logs

## Requirements

- Python 3.11 or higher
- Flask
- All the requirements for the BlueSpy application

## Installation

1. Make sure you have all the required dependencies installed:

```bash
pip install flask
```

2. Ensure that your system has the necessary Bluetooth tools installed as mentioned in the main README.md.

## Usage

1. Start the web interface:

```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the interface to:
   - Scan for Bluetooth devices
   - Connect to a device
   - Start/stop recording
   - Manage your recordings

## Troubleshooting

- If you encounter issues with scanning or connecting to devices, ensure that your Bluetooth adapter is working correctly.
- Check the logs in the web interface for error messages.
- For more detailed troubleshooting, refer to the main README.md file.

## Security Considerations

This web interface is intended for local use only. Do not expose it to the internet without proper security measures in place.