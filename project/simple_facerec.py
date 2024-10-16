import face_recognition
import cv2
import os
import glob
import numpy as np
import serial
import time
import threading
import gmail

class SimpleFacerec:
    
    def __init__(self):
        self.known_face_encodings = []
        self.unknown_face_encodings = []
        self.known_face_names = []
        self.unknown_face_names = []
        # Resize frame for a faster speed
        self.frame_resizing = 0.35  
        # self.save_directory="unknown"
        # os.makedirs(self.save_directory, exist_ok=True)
        # self.i=1

    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        # Load Images
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        print("{} encoding images found.".format(len(images_path)))

        # Store image encoding and names
        for img_path in images_path:
            img = cv2.imread(img_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get the filename only from the initial file path.
            basename = os.path.basename(img_path)
            (filename, ext) = os.path.splitext(basename)
            # Get encoding
            try:
                img_encoding = face_recognition.face_encodings(rgb_img)[0]
            except IndexError:
                 # Catch the IndexError if no face is found in the image
                print(f"No face found in {filename}. Skipping this image.")
                continue  # Skip to the next image if no face is detected

            # Store file name and file encoding
            self.known_face_encodings.append(img_encoding)
            self.known_face_names.append(filename)
        print("Encoding images loaded")

    def detect_known_faces(self, frame, ser):
        # Find all the faces and face encodings in the current frame of video
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        small_frame = cv2.resize(
            frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)

        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame,2)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, 0.55)
            name = "Unknown"
            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)
            x1=None
            
            x1 =  face_locations[0][3]
            
            middle=True
            if(x1<90 and name=='Unknown' ):
                 print('left')
                 ser.write(b'2')
                 print(x1)
                 middle=False
            elif(x1>140 and name=='Unknown' and middle):
                
                ser.write(b'7')
                print('right')
                print(x1)
                middle=False

            elif (name == 'Unknown'):
                ser.write(b'1')
                # ser.write(b'x1')
                # print(10)
                print(x1)
            else:
                ser.write(b'5')
                print(5)
        if  len(face_names)==0:
            ser.write(b'5') 
            print(5)

        # Convert to numpy array to adjust coordinates with frame resizing quickly
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names


    def face_location(self , frame):
        small_frame = cv2.resize(
            frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame,2)
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int)