import face_recognition
import cv2
import numpy as np
import os
from tinydb import TinyDB, Query
import datetime


class FacialRecognition:

    def __init__(self):
        video_capture = cv2.VideoCapture(0)

        # Create arrays of known face encodings and their names
        loading_faces = self.load_faces()
        known_face_encodings = loading_faces[0]
        known_face_names = loading_faces[1]

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        recent_faces = {}
        print('Active scanning')

        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            try:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Only process every other frame of video to save time
                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        # # If a match was found in known_face_encodings, just use the first one.
                        # if True in matches:
                        #     first_match_index = matches.index(True)
                        #     name = known_face_names[first_match_index]

                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                process_this_frame = not process_this_frame


                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Display the resulting image (DEBUGGING CAMERA VIEW)
                # cv2.imshow('Video', frame)

                # Proccess people
                # TODO: Improve
                for name in face_names:
                    if name not in recent_faces:
                        self.process_person(name, frame)
                        recent_faces[name] = 0
                    elif name in recent_faces:
                        recent_faces[name] = 0


                face_names_to_delete = []
                for name in recent_faces:
                    if recent_faces[name] > 60:
                        face_names_to_delete.append(name)
                    
                    # detect bodies if bodies = faces stay same
                    hog = cv2.HOGDescriptor()
                    hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )
                    found,w=hog.detectMultiScale(frame, winStride=(8,8), padding=(32,32), scale=1.05)
                    if len(found) != len(recent_faces):
                        recent_faces[name] += 1

                for name in face_names_to_delete:
                    del recent_faces[name]
            except Exception as e:
                print(str(e))

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()

    def load_faces(self):
        filenames = []
        for root, dirs, files in os.walk("./known_pictures/"):
            for filename in files:
                filenames.append(filename)
        filenames.remove(".DS_Store")

        encoding_list = []
        name_list = []
        for index, file in enumerate(filenames):
            # Load a sample picture and learn how to recognize it.
            face_image = face_recognition.load_image_file("./known_pictures/"+file)
            index = face_recognition.face_encodings(face_image)[0]
            encoding_list.append(index)
            name_list.append(os.path.splitext(file)[0])

        return (encoding_list, name_list)

    def load_blacklist(self):
        db = TinyDB('log_list.json')
        table = db.table('blacklist')

        blacklist = []
        for name in table.all():
            blacklist.append(name['name'])

        return blacklist

    def fix_date_time(self, object):
        if isinstance(object, (datetime.date, datetime.datetime)):
                return object.isoformat()

    def process_person(self, name, frame):
        db = TinyDB('log_list.json')
        table = db.table('history')
        blacklisted_names = self.load_blacklist()

        is_blacklisted = False
        if name in blacklisted_names:
            is_blacklisted = True

        proper_name = self.fix_date_time(datetime.datetime.now()).replace('/', '')+".jpg"
        filename = "./web-app/public/logged_frames/"+proper_name

        cv2.imwrite(filename, frame)

        table.insert({'timestamp': self.fix_date_time(datetime.datetime.now()), 'name': name, 'is_blacklisted': is_blacklisted, 'filename': proper_name})
        

testrun = FacialRecognition()