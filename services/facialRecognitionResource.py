import face_recognition
import cv2
import os


def checkFaceInImage(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return len(face_locations) > 0


def compareFaces(credential_image_path, user_image_path):
    credential_image = face_recognition.load_image_file(credential_image_path)
    user_image = face_recognition.load_image_file(user_image_path)

    try:
        credential_encoding = face_recognition.face_encodings(credential_image)[0]
        user_encoding = face_recognition.face_encodings(user_image)[0]
    except IndexError:
        return False  

    results = face_recognition.compareFaces([credential_encoding], user_encoding)
    return results[0]


def extractFace(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) > 0:
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]

        
        _, buffer = cv2.imencode('.jpg', face_image)
        return buffer.tobytes() 
    return None


def removeTempImages(*image_paths):
    for image_path in image_paths:
        if os.path.exists(image_path):
            os.remove(image_path)
