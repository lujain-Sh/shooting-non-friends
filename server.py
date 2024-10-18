from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import serial
import time
import logging
import sys
import os
import cv2
from simple_facerec import SimpleFacerec
import threading
import gmail  # Ensure you have a 'gmail.py' with a 'send' function

# ================================
# Configuration and Initialization
# ================================
name="main"
app = Flask(name)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Global serial object and lock for thread-safe communication
ser = None
serial_lock = threading.Lock()

def init_serial(port, baudrate=9600, timeout=1):
    global ser
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Wait for the serial connection to initialize
        logging.info(f"Serial connection established on {port}")
    except serial.SerialException as e:
        logging.error(f"Failed to open serial port {port}: {e}")
        ser = None

# ================================
# Flask Routes
# ================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Ensure 'index.html' is in the same directory

@app.route('/control', methods=['POST'])
def control():
    if ser is None or not ser.is_open:
        logging.error("Serial port not open")
        return jsonify({'status': 'error', 'message': 'Serial port not open'}), 500

    data = request.get_json()
    if not data:
        logging.warning("No JSON data received")
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    command = data.get('command')
    logging.info(f"Received command: {command}")

    # Define valid commands
    valid_commands = ['8', '9', '2']

    if command in valid_commands:
        try:
            with serial_lock:
                ser.write((command).encode())
                logging.info(f"Command '{command}' sent to Arduino")

                # Optional: Read Arduino's response
                time.sleep(0.05)  # Small delay to allow Arduino to respond
                if ser.in_waiting:
                    response = ser.read(ser.in_waiting).decode().strip()
                    logging.info(f"Arduino response: {response}")
                else:
                    response = 'No response from Arduino'
                    logging.warning("No response from Arduino")

            return jsonify({'status': 'success', 'command': command, 'response': response}), 200

        except serial.SerialException as e:
            logging.error(f"Failed to send command to Arduino: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to send command'}), 500
    else:
        logging.warning(f"Invalid command received: {command}")
        return jsonify({'status': 'error', 'message': 'Invalid command'}), 400

# ================================
# OpenCV Face Detection
# ================================

# Initialize face recognition
sfr = SimpleFacerec()
sfr.load_encoding_images("save_directory")  # Ensure this directory exists and has encoding images

# Initialize video capture (0 for default webcam)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.critical("Failed to open webcam")
    sys.exit(1)

# Initialize serial for face detection (ensure it's the same as Flask or different)
# To avoid conflict, it's better to have a single serial object; here, we'll use the global 'ser'

sent_flag = True
tar = 300  # Time in seconds before allowing another email
last_time = time.time()
lock = threading.Lock()

def face_detection():
    global sent_flag, last_time
    frame_count = 0
    fps = 0
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to read frame from webcam")
            break
# Detect faces every 20 frames for efficiency
        if frame_count % 20 == 0:
            face_locations, face_names = sfr.detect_known_faces(frame, ser)
            # Alternatively, adjust based on your SimpleFacerec implementation

            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc  # Adjust based on your face detection output
                cv2.putText(frame, name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

                if name == 'Unknown' and sent_flag:
                    sent_flag = False
                    thread1 = threading.Thread(target=gmail.send)
                    thread1.start()
                    logging.info('An email has been sent due to unknown face detection')

        # Calculate FPS
        current_time = time.time()
        elapsed_time = current_time - prev_time
        fps = 1 / elapsed_time if elapsed_time > 0 else 0
        prev_time = current_time

        # Reset sent_flag after 'tar' seconds
        if current_time - last_time >= tar:
            sent_flag = True
            last_time = current_time
            logging.info("Sent flag reset, ready to send another email")

        # Display FPS on the frame
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Show the frame with detections
        cv2.imshow("Frame", frame)

        # Increment frame counter
        frame_count += 1

        # Exit on pressing the "ESC" key
        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            logging.info("ESC pressed, exiting face detection")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

# ================================
# Main Function with Threading
# ================================

def main():
    # Initialize serial connection
    SERIAL_PORT = 'COM10'  # Replace with your confirmed port
    init_serial(SERIAL_PORT)

    if ser is None:
        logging.critical("Exiting due to serial port issues.")
        sys.exit(1)  # Exit the application if serial port failed to open

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    flask_thread.start()
    logging.info("Flask server started")

    # Start OpenCV face detection in the main thread or another thread
    face_thread = threading.Thread(target=face_detection)
    face_thread.start()
    logging.info("Face detection started")

    # Wait for both threads to finish
    flask_thread.join()
    face_thread.join()



if name == 'main':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received, exiting application.")
        if ser and ser.is_open:
            ser.close()
        sys.exit(0)        