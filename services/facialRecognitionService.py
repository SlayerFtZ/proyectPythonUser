import face_recognition


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

    results = face_recognition.compare_faces([credential_encoding], user_encoding)
    return results[0]