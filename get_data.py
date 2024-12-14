from pymongo import MongoClient

class db_retriever:
    def __init__(self, connection):
        self.client = MongoClient(connection)
        self.db = None
        self.db_name = "dbqr"
        self.users_collection = "dbqrcol"
        self.preprocessed_data_collection = "pre_data"
        self.knowledge_collection = "scraped_data"
    
    def connect(self, db_name = "dbqr"):
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        if self.db == None:
            raise ValueError("No database selected. Call 'connect()' first.")
        return self.db[collection_name]

    def get_user(self, key, value):
        collection = self.get_collection(self.users_collection)
        return collection.find_one({f"{key}": f"{value}"})
    
    def get_preprocessed_data(self):
        collection = self.get_collection(self.preprocessed_data_collection)
        return collection.find()

    def get_knowledge(self):
        collection = self.get_collection(self.knowledge_collection)
        return collection.find()

    def close_connection(self):
        """Closes the connection to the MongoDB server."""
        self.client.close()

if __name__ == "__main__":
    pass
