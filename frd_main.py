"""
Main script for First Response Drone control program.
"""
import sys
sys.path.append("C:/Users/nickm/Desktop/pyparrot")
from Bebop import Bebop
from DroneVision import DroneVision
import threading
# import cv2
import time
import face_recognition
from PIL import Image, ImageDraw


isAlive = False

def distance_to_camera(perWidth):
    # compute and return the distance from the maker to the camera in inches
    return (6.10236 * 412.37069424715907) / perWidth
# http://personal.cityu.edu.hk/~meachan/Online%20Anthropometry/Chapter2/Ch2-27.htm

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
biden_image = face_recognition.load_image_file("biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden"
]

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def face_detect(self, args):
        print("Accessed face_detect function")
        frame = self.vision.get_latest_valid_picture()
        if frame is not None: # and self.vision.drone_object.ready:
            print("Got a frame!")
            # Load an image with an unknown face
            path = "C:/Users/Desktop/pyparrot/frd/imagesimage_{0:0=3d}.png".format(self.index)
            print(path)
            unknown_image = face_recognition.load_image_file(frame)

            # Find all the faces and face encodings in the unknown image
            face_locations = face_recognition.face_locations(unknown_image)
            face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

            # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
            # See http://pillow.readthedocs.io/ for more about PIL/Pillow
            pil_image = Image.fromarray(unknown_image)
            # Create a Pillow ImageDraw Draw instance to draw with
            draw = ImageDraw.Draw(pil_image)

            # Loop through each face found in the unknown image
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                name = "Unknown"

                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                # Draw a box around the face using the Pillow module
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

                # Draw a label with a name below the face
                text_width, text_height = draw.textsize(name)
                draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
                draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))


            # Remove the drawing library from memory as per the Pillow docs
            del draw

            # Display the resulting image
            # pil_image.show()

            # You can also save a copy of the new image to disk if you want by uncommenting this line
            pil_image.save("C:/Users/nickm/Desktop/image_{0:0=3d}.png".format(i))

# -------
# make my bebop object
bebop = Bebop()
bebop.set_video_stream_mode('high_reliability')
# safely initialize control var
bebop.ready = True
# connect to the bebop
success = bebop.connect(5)

if success:
    # start up the video
    bebopVision = DroneVision(bebop, is_bebop=True)
    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.face_detect, user_callback_args=None)
    success = bebopVision.open_video()

    try:
        if (success):
            print("Vision successfully started!")
            bebop.ask_for_state_update()
            print("Taking off!")
            # bebop.safe_takeoff(10)
            bebop.smart_sleep(5)
            # bebop.ready = True

            # bebop.safe_land(10)
    except Exception as e:
        print("Error encountered: {}".format(e))

    # disconnect nicely so we don't need a reboot
    if not bebop.is_landed():
        bebop.safe_land(10)
    bebopVision.close_video()
    bebop.disconnect()
else:
    print("Error connecting to bebop.  Retry")

