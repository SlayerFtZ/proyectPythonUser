import os
import firebase_admin
from firebase_admin import credentials, storage
from datetime import timedelta


def uploadToFirebase(file_path):
    bucket = storage.bucket()
    blob = bucket.blob(f'credential_images/{os.path.basename(file_path)}')

    try:
        with open(file_path, 'rb') as file:
            blob.upload_from_file(file, content_type='image/jpeg')
    except Exception as e:
        raise Exception(f"Error uploading image to Firebase: {str(e)}")

    return blob.generate_signed_url(timedelta(hours=1))

def deleteFromFirebase(file_path):
    bucket = storage.bucket()
    blob = bucket.blob(f'credential_images/{os.path.basename(file_path)}')

    try:
        blob.delete()
        print(f"The image{os.path.basename(file_path)} has been successfully removed from Firebase.")
    except Exception as e:
        raise Exception(f"Error deleting image from Firebase: {str(e)}")

    return f"The image {os.path.basename(file_path)} has been successfully removed."
