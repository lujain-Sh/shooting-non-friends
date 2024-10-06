import cv2
import face_recognition
import os
import glob
import time
 # Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

save_directory="save_directory"
os.makedirs(save_directory, exist_ok=True)

# url='https://192.168.0.112:8080/video'

cap = cv2.VideoCapture(0)
images_path = glob.glob(os.path.join("save_directory/", "*.*"))#back

i=len(images_path)+1

last_time=time.time()
tar=5
# j=True
while True:
    
    ret, frame = cap.read()
    current_time=time.time()
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8, minSize=(30, 30))
    

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        if len(faces) > 0 and current_time - last_time >= tar:
            file_path = os.path.join(save_directory,f' {i} friend.jpg' )
            cv2.imwrite(file_path, frame)  
            print(f"Frame saved as '{file_path}'")
            i+=1
            last_time = current_time
       
        if cv2.waitKey(1) & 0xFF == ord('s'):
         file_path = os.path.join(save_directory,f' {i} friend.jpg' )
         cv2.imwrite(file_path, frame)  
         print(f"Frame saved as '{file_path}'")
         i+=1
       
    # Display the resulting frame
    cv2.imshow('Face Detection', frame)

    key = cv2.waitKey(1)
    if key == 27:#"esc"
        break

# Release the capture and close the window
cap.release()
cv2.destroyAllWindows()