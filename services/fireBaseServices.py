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
        raise Exception(f"Error al subir la imagen a Firebase: {str(e)}")

    return blob.generate_signed_url(timedelta(hours=1))

def deleteFromFirebase(file_path):
    bucket = storage.bucket()
    blob = bucket.blob(f'credential_images/{os.path.basename(file_path)}')

    try:
        blob.delete()
        print(f"La imagen {os.path.basename(file_path)} ha sido eliminada exitosamente de Firebase.")
    except Exception as e:
        raise Exception(f"Error al eliminar la imagen de Firebase: {str(e)}")

    return f"La imagen {os.path.basename(file_path)} ha sido eliminada exitosamente."