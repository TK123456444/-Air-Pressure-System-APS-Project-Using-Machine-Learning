import pymongo

from dotenv import load_dotenv

load_dotenv()

from sensor.constant.database import DATABASE_NAME

from sensor.constant.env_variable import (
    MONGODB_URL_KEY
)

import certifi
import os

ca = certifi.where()


class MongoDBClient:

    client = None

    def __init__(self,database_name=DATABASE_NAME) -> None:
        try:
            if MongoDBClient.client is None:

                mongo_db_url = os.getenv(MONGODB_URL_KEY)

                if mongo_db_url is None:

                    raise Exception(
                        "MongoDB URL not found"
                    )

                MongoDBClient.client = (pymongo.MongoClient(mongo_db_url,tlsCAFile=ca))

            self.client = MongoDBClient.client

            self.database = self.client[database_name]

            print("MongoDB connected successfully")

        except Exception as e:

            print("MongoDB connection failed")

            print(e)

            raise e