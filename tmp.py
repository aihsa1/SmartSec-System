import pymongo

USERNAME = "KyHSAVsQnqTw1HC0"
PASSWORD = "XnHZPdap8941pypr"


mongodb_client = pymongo.MongoClient(F"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.pueke.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
print(mongodb_client.list_database_names())