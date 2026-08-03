from dataclasses import dataclass
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()


@dataclass
class EnvironmentVariable:

    mongo_db_url: str = os.getenv(
        "MONGO_DB_URL"
    )


env_var = EnvironmentVariable()


if env_var.mongo_db_url is None:

    raise Exception(
        "MONGO_DB_URL is not set in .env file"
    )


mongo_client = pymongo.MongoClient(
    env_var.mongo_db_url
)

print("MongoDB connected successfully")