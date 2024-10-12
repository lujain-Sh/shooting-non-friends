import cv2
from simple_facerec import SimpleFacerec
import serial
import time
import threading
# import shutil
# import os
import gmail
# Open video capture (0 for webcam)
cap = cv2.VideoCapture(0)

thread = threading.Thread()
# Encode faces from a folder7
sfr = SimpleFacerec()
sfr.load_encoding_images("save_directory/")
sent=True
# Open serial port (adjust the COM port to match your setup)
# Replace 'COM11' with your correct port
ser = serial.Serial('COM10', 9600, timeout=.1)
time.sleep(2)  # Give the connection a moment to initialize
seconds=time.time()
frame_count = 0
fps = 0
prev_time = time.time()  # To track time
last_time = time.time()  # To track time for the sent flag reset
tar = 300

output = {
    'faces_locations':[],
    
    'face_names':[]

}
lock = threading.Lock()


def face(output ,frame, ser):
    with lock:
     face_locations, face_names = sfr.detect_known_faces(frame, ser)
     output['faces_locations'] = face_locations
     output['face_names'] = face_names

name=None
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()    

    # Only process face detection every 100 frames for efficiency
    face_locations=sfr.face_location(frame)
    if frame_count % 20 == 0:
        thread = threading.Thread(target=face, args=(output,frame, ser))
        thread.start()
    
    face_names = output['face_names']
    
    for face_loc, name in zip(face_locations, face_names):
            face_locations = output['faces_locations']
            
            
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
           
    if(name=='Unknown' and sent ):
                
                
                sent=False
                
                thread1 = threading.Thread(target=gmail.send)
                thread1.start()
                print('An Email has been sent')
    # Calculate FPS                     
    current_time = time.time()
    elapsed_time = current_time - prev_time
    fps = 1 / elapsed_time  # FPS is inverse of time taken per frame
    prev_time = current_time

    if current_time - last_time >= tar:
        sent = True
        last_time = current_time  # Reset the timer
        # print("Sent flag reset")

    # Display FPS on the frame
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Show the frame with the FPS and detected faces
    cv2.imshow("Frame", frame)

    # Increment frame counter
    frame_count += 1

    # Exit on pressing the "ESC" key
    key = cv2.waitKey(1)
    if key == 27:  # ESC key
        # if os.path.exists("unKnown"):
        #     shutil.rmtree("unknown")  # Deletes the folder and all its contents
        break

# Release the video capture and close windows
ser.close()
cap.release()
cv2.destroyAllWindows()