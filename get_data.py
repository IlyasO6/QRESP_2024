from pymongo import MongoClient

# Step 1: Connect to MongoDB server
client = MongoClient("mongodb+srv://carlosnieves:Uo7pzJh5iDvlS37M@cluster0.9t4o9.mongo.net/")  # Replace with your MongoDB URI

# Step 2: Access the database
db = client["dbqr"]  # Replace 'my_database' with your database name

# Step 3: Access the collection
collection = db["dbqrcol"]  # Replace 'my_collection' with your collection name

# Step 4: Fetch data
"""
# Example 1: Fetch all documents
documents = collection.find()
for doc in documents:
    print(doc)

# Example 2: Fetch documents with a query
query = {"age": {"$gt": 25}}  # Find documents where 'age' is greater than 25
filtered_documents = collection.find(query)
for doc in filtered_documents:
    print(doc)
"""
# Example 3: Fetch a single document
single_document = collection.find_one({"username": "Carlos"})  # Find a document with 'name' = 'John'
print(single_document)
