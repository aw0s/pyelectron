import os

import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from ...settings import DATABASE, DEFAULT_COLLECTION, SERVER

config_keys = ["_folder", "_filter"]
DATABASE_CURSOR = {"CURSOR": None}


class Connection_mongo:
    def __init__(self):
        print(self)
        self.server: MongoClient
        self.db: Database
        self.collection: Collection

    def connect(self, collection=None):
        try:
            server = pymongo.MongoClient(SERVER)
            # install dnspython
            db = server[DATABASE]
            DATABASE_CURSOR["CURSOR"] = db[
                collection if collection else DEFAULT_COLLECTION
            ]
            print("connection successful")  # tag_console
        except:
            print("wrong connection, brake process")  # tag_console
            os._exit(0)


class Controller_mongo:
    def __init__(self, _collection=None, _folder="", _filter={}) -> None:
        self.config = {"_folder": _folder, "_filter": _filter}
        self.collection = DATABASE_CURSOR.get("CURSOR")
        self._collection = _collection

    def tool(self, options) -> None:
        for config_key, config_value in options.items():
            if config_key not in config_keys:
                continue
            self.config[config_key] = config_value

    def attr(self, config_selector) -> str:
        return self.config.get(config_selector)

    def save(self, name, data=None, **options) -> None:
        self.tool(options)
        _folder = self.attr("_folder")
        _filter = self.attr("_filter")

        if not bool(_filter):
            return

        self.collection.update_one(
            _filter,
            {
                "$set"
                if data
                else "$unset": {f"{_folder}.{name}" if _folder else f"{name}": data}
            },
        )

    def insert(self, data, **options):
        self.tool(options)
        self.collection.insert_one(data)

    def _get_folder(self, catalogs, result) -> dict:
        for catalog in catalogs:
            if condition_result := result.get(catalog, None):
                result = condition_result
            else:
                return None
        return result

    def load(self, loop=False, **options):
        self.tool(options)
        _folder = self.attr("_folder")
        _filter = self.attr("_filter")
        _finder_options = options.get("_finder", None)
        params = _folder.split(".")

        def generator():
            for result in self.collection.find(_filter, _finder_options):
                if bool(_folder):
                    yield self._get_folder(params, result)
                else:
                    yield result

        return generator() if loop else next(generator(), None)

    def delete(self, name, **options):
        self.save(name, None, **options)
