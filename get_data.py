import json
from pymongo import MongoClient

class db_retriever:
    def __init__(self, connection):
        self.client = MongoClient(connection)
        self.db = None
        self.db_name = "dbqr"
        self.users_collection = "dbqrcol"
        self.doctor_keys = "medkeys"
    
    def connect(self, db_name = "dbqr"):
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        if self.db == None:
            raise ValueError("No database selected. Call 'connect()' first.")
        return self.db[collection_name]

    def get_user(self, key, value):
        collection = self.get_collection(self.users_collection)
        return collection.find_one({f"{key}": f"{value}"})
    
    def get_med_data(self):
        """Reads and returns all medical data from med_data.json file."""
        try:
            with open('med_data.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError("med_data.json file not found")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in med_data.json")

    def doctor_keys(self, key):
        collection = self.get_collection(self.doctor_keys)
        return collection.find_one({"medic_key": f"{key}"})

    def close_connection(self):
        """Closes the connection to the MongoDB server."""
        self.client.close()


"""
db = db_retriever("mongodb+srv://Ilyas:NlzFSgDrycE0gRGt@cluster0.9t4o9.mongodb.net/")
db.connect()

data = db.get_med_data()
for key, value in data.items():
    print(key + ":", value)
    print()

db.close_connection()
"""
