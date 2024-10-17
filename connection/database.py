import mysql.connector
import pymongo
import firebase_admin
from firebase_admin import credentials, storage
def connectdataBase():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="10122001",
            database="DB_SazonIa"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        return None

def connectdataBaseMongo():
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["dbImageProfile"]
        collection = db["profile"]
        return collection
    except pymongo.errors.ConnectionError as err:
        print(f"Error connecting to MongoDB: {err}")
        return None

def connectdataBaseMongoFacialRecognition():
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['dbfacialrecognition']
        useFacesCollection = db['facialRecognition']
        return useFacesCollection
    except pymongo.errors.ConnectionError as err:
        print(f"Error connecting to MongoDB: {err}")
        return None
    
# Inicializa la aplicación de Firebase
cred = credentials.Certificate('D:/Pruebas/KeyFireBase.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'dblicenceine.appspot.com',  # Asegúrate de que este nombre sea correcto
})