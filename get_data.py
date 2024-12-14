from pymongo import MongoClient

class db_retriever:
    def __init__(self, connection):
        self.client = MongoClient(connection)
        self.db = None
        self.db_name = "dbqr"
        self.users_collection = "dbqrcol"
        self.knowledge_collection = "pre_data"
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
    
    def get_knowledge(self):
        collection = self.get_collection(self.knowledge_collection)
        return collection.find()

    def doctor_keys(self, key):
        collection = self.get_collection(self.doctor_keys)
        return collection.find_one({"medic_key": f"{key}"})

    def close_connection(self):
        """Closes the connection to the MongoDB server."""
        self.client.close()


"""
EJEMPLO DE USO
db = db_retriever("mongodb+srv://Ilyas:NlzFSgDrycE0gRGt@cluster0.9t4o9.mongodb.net/")
db.connect()
user1 = db.get_user("username", "Andres")

print(user1['medical_info']['age'])

db.close_connection()
"""
