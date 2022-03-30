import pymongo
import bson
import re
import datetime

USERNAME = "KyHSAVsQnqTw1HC0"
PASSWORD = "XnHZPdap8941pypr"

print("Connecting to MongoDB...")
mongodb_client = pymongo.MongoClient(F"mongodb+srv://{USERNAME}:{PASSWORD}@smartsec1.pueke.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
print(mongodb_client.list_database_names())
db = mongodb_client["tmp"]
col = db["tmp-col"]

# col.insert_one({"name": "David", "age": 35})
# col.insert_one({"name": "Jacob", "age": 60})
# col.insert_one({"name": "John", "age": 15})
# col.insert_one({"name": "John", "age": 15})
# col.insert_one({"name": "John", "age": 15})
# col.insert_one({"name": "John", "age": 15})

# col.insert_one({"name": "David", "age": 35, "ref": bson.ObjectId("624088f14d260b008081f374")})

# col.insert_one({"name": "Davidov", "age": 28, "date": datetime.datetime.now()})



for x in col.find({}, sort=[("name", pymongo.ASCENDING)]):
    print(x)

# for x in col.find({"name": "john"}):
#     print(x)

# query = {"name": {"$regex": "^.*n$"}}
# for x in col.find(query).sort("age", pymongo.DESCENDING):
#     print(x)

# pattern = re.compile("^.*a.*$")
# pattern = bson.Regex.from_native(pattern)
# query = {"name": {"$regex": pattern}}
# for x in col.find(query).sort("age", pymongo.DESCENDING):
#     print(x)

# col.delete_one({"name": "Jhon"})

# col.delete_many({"name": "John"})

# col.update_one({"_id": bson.ObjectId("624088f14d260b008081f374")}, {"$set": {"name": "Ran Davidos", "age": 17.5}})

mongodb_client.close()