import mysql.connector
import pymongo

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
