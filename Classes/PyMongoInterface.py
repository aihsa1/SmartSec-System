from typing import List
import pymongo
import bson
import re

class PyMongoInterface:
    DEFAULT_USERNAME = "KyHSAVsQnqTw1HC0"
    DEFAULT_PASSWORD = "XnHZPdap8941pypr"
    DEFAULT_CONN_STRING = F"mongodb+srv://{DEFAULT_USERNAME}:{DEFAULT_PASSWORD}@smartsec1.pueke.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

    ASCENDING = pymongo.ASCENDING
    DESCENDING = pymongo.DESCENDING

    def __init__(self, conn_string: str = DEFAULT_CONN_STRING) -> None:
        try:
            print("Trying to connect to MongoDB...")
            self.client = pymongo.MongoClient(conn_string)
        except (pymongo.errors.OperationFaliure, pymongo.errors.ConnectionFailure, pymongo.errors.ConfigurationError) as e:
            raise e
        else:
            print("Connected to MongoDB.")
    
    def list_database_names(self) -> List[str]:
        return self.client.list_database_names()
    
    def insert(self, *docs, db_name, col_name):
        return self.client[db_name][col_name].insert_many(docs)
    
    def find(self, *objs, db_name, col_name, limit=0, sort=[]):
        return self.client[db_name][col_name].find(*objs, limit=limit, sort=sort)
    
    def update_one(self, filter, update, db_name, col_name):
        return self.client[db_name][col_name].update_one(filter, update)
    
    def update_many(self, filter, update, db_name, col_name):
        return self.client[db_name][col_name].update_many(filter, update)
    
    def delete_one(self, query, db_name, col_name):
        return self.client[db_name][col_name].delete_one(query)
    
    def delete_many(self, query, db_name, col_name):
        return self.client[db_name][col_name].delete_many(query)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    @classmethod
    def generate_regex(cls, regex: str) -> bson.Regex:
        return bson.Regex.from_native(re.compile(regex))
    
    @classmethod
    def generate_objectid(cls, *args) -> bson.ObjectId:
        return bson.ObjectId(*args)
    
    


def main():
    with PyMongoInterface() as db:
        print(db.list_database_names())

        # pattern = PyMongoInterface.generate_regex("^David.*$")
        # for x in db.find({"name": {"$regex": pattern}}, {"name": 1, "_id": 0, "age": 1}, db_name="tmp", col_name="tmp-col", sort=[("age", PyMongoInterface.DESCENDING)]):
        #     print(x)

        # db.insert({"name": "Jane Doe", "age": 20}, {"name": "John Doe", "age": 21}, db_name="tmp", col_name="tmp-col")

        # pattern = PyMongoInterface.generate_regex("^.*Doe$")
        # db.delete_many({"name": {"$regex": pattern}}, db_name="tmp", col_name="tmp-col")

        # id = PyMongoInterface.generate_objectid("624088f04d260b008081f373")
        # db.delete_one({"_id": id}, db_name="tmp", col_name="tmp-col")

        # db.update_one({"name": "Jacob"}, {"$set": {"age": 30}}, db_name="tmp", col_name="tmp-col")

        # pattern = PyMongoInterface.generate_regex("^.*David.*$")
        # db.update_many({"name": {"$regex": pattern}}, {"$set": {"age": 100}}, db_name="tmp", col_name="tmp-col")



if __name__ == "__main__":
    main()