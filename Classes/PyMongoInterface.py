from typing import List, Tuple
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
        """
        The constructor of the class. This function takes care of the connection to the database.
        :param conn_string: The connection string to the database. if not specified, the default connection string will be used.
        :type conn_string: str
        """
        try:
            print("Trying to connect to MongoDB...")
            self.client = pymongo.MongoClient(conn_string)
        except (pymongo.errors.OperationFaliure, pymongo.errors.ConnectionFailure, pymongo.errors.ConfigurationError) as e:
            raise e
        else:
            print("Connected to MongoDB.")

    def list_database_names(self) -> List[str]:
        """
        This function returns a list of the names of the databases in the MongoDB instance.
        :return: A list of the names of the databases in the MongoDB instance.
        :rtype: List[str]
        """
        return self.client.list_database_names()

    def insert(self, *docs, db_name: str, col_name: str) -> pymongo.results.InsertManyResult:
        """
        This function inserts the given documents into a collection.
        :param docs: The documents to insert. You can insert multiple documents at once.
        :type docs: List[dict]
        :param db_name: The name of the database.
        :type db_name: str
        :param col_name: The name of the collection. THIS IS A KWARG
        :type col_name: str
        :return: The result of the insertion. THIS IS A KWARG
        :rtype: pymongo.results.InsertManyResult
        """
        return self.client[db_name][col_name].insert_many(docs)

    def find(self, *objs, db_name: str, col_name: str, limit: int = 0, sort: List[Tuple[str, int]] = []) -> pymongo.cursor.Cursor:
        """
        This function returns a cursor to the documents that match the given query.
        :param objs: The query as would be specified to PyMongo.
        :type objs: List[dict]
        :param db_name: The name of the database. THIS IS A KWARG
        :type db_name: str
        :param col_name: The name of the collection. THIS IS A KWARG
        :type col_name: str
        :param limit: The maximum number of documents to return. If 0 is specified, no limit will be used. THIS IS A KWARG
        :type limit: int
        :param sort: The sort order. This is a list of tuples. Each tuple contains the name of the field to sort on and the sort order. THIS IS A KWARG
        :type sort: List[Tuple[str, int]]
        """
        return self.client[db_name][col_name].find(*objs, limit=limit, sort=sort)

    def update_one(self, filter: dict, update: dict, db_name: str, col_name: str) -> pymongo.results.UpdateResult:
        """
        This function updates the first document that matches the given query.
        :param filter: The query as would be specified to PyMongo.
        :type filter: dict
        :param update: The update to apply as would be specified to PyMongo.
        :type update: dict
        :param db_name: The name of the database. THIS IS A KWARG
        :type db_name: str
        :param col_name: The name of the collection. THIS IS A KWARG
        :type col_name: str
        :return: The result of the update.
        :rtype: pymongo.results.UpdateResult
        """
        return self.client[db_name][col_name].update_one(filter, update)

    def update_many(self, filter: dict, update: dict, db_name: str, col_name: str) -> pymongo.results.UpdateResult:
        """
        This function updates all documents that match the given query.
        :param filter: The query as would be specified to PyMongo.
        :type filter: dict
        :param update: The update to apply as would be specified to PyMongo.
        :type update: dict
        :param db_name: The name of the database. THIS IS A KWARG
        :type db_name: str
        :param col_name: The name of the collection. THIS IS A KWARG
        :type col_name: str
        :return: The result of the update.
        :rtype: pymongo.results.UpdateResult
        """
        return self.client[db_name][col_name].update_many(filter, update)

    def delete_one(self, query: dict, db_name: str, col_name) -> pymongo.results.DeleteResult:
        """
        This function deletes the first document that matches the given query.
        :param query: The query as would be specified to PyMongo.
        :type query: dict
        :param db_name: The name of the database. THIS IS A KWARG
        :type db_name: str
        :param col_name: The name of the collection. THIS IS A KWARG
        :type col_name: str
        :return: The result of the deletion.
        :rtype: pymongo.results.DeleteResult
        """
        return self.client[db_name][col_name].delete_one(query)

    def delete_many(self, query: dict, db_name: str, col_name: str) -> pymongo.results.DeleteResult:
        """
        This function deletes all documents that matches the given query.
        :param query: The query as would be specified to PyMongo.
        :type query: dict
        :param db_name: The name of the database. THIS IS A KWARG
        :type db_name: str
        :param col_name: The name of the collection. THIS IS A KWARG
        :type col_name: str
        :return: The result of the deletion.
        :rtype: pymongo.results.DeleteResult
        """
        return self.client[db_name][col_name].delete_many(query)

    def close(self) -> None:
        """
        This function closes the connection to the database.
        """
        self.client.close()
        print("Connection to MongoDB closed.")

    def __enter__(self) -> 'PyMongoInterface':
        """
        This function is called when the object is used in a with statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        This function is called when the object is used in a with statement.
        """
        self.client.close()

    @classmethod
    def generate_regex(cls, regex: str) -> bson.Regex:
        """
        This function generates a bson.Regex object from the given string.
        :param regex: The regex to generate.
        :type regex: str
        :return: The bson.Regex object.
        :rtype: bson.Regex
        """
        return bson.Regex.from_native(re.compile(regex))

    @classmethod
    def generate_objectid(cls, *args) -> bson.ObjectId:
        """
        This function generates a bson.ObjectId object from the given arguments.
        :param args: The arguments to generate the ObjectId from.
        :type args: List[str]
        """
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

        # id = PyMongoInterface.generate_objectid("6244084095a264afc66e82e2")
        # db.delete_one({"_id": id}, db_name="tmp", col_name="tmp-col")

        # db.update_one({"name": "Jacob"}, {"$set": {"age": 50}}, db_name="tmp", col_name="tmp-col")

        # pattern = PyMongoInterface.generate_regex("^.*David.*$")
        # db.update_many({"name": {"$regex": pattern}}, {"$set": {"age": 3000}}, db_name="tmp", col_name="tmp-col")


if __name__ == "__main__":
    main()
