import sys
from typing import Optional

import numpy as np
import pandas as pd
import json

from sensor.configuration.mongo_db_connection import MongoDBClient
from sensor.constant.database import DATABASE_NAME
from sensor.exception import SensorException


class SensorData:
    """
    Export MongoDB collection as pandas DataFrame
    """

    def __init__(self):
        try:
            self.mongo_client = MongoDBClient(
                database_name=DATABASE_NAME
            )
        except Exception as e:
            raise SensorException(e, sys)

    def save_csv_file(
        self,
        file_path: str,
        collection_name: str,
        database_name: Optional[str] = None
    ):
        try:

            print(f"Reading CSV: {file_path}")

            data_frame = pd.read_csv(file_path)

            print(f"CSV Shape: {data_frame.shape}")

            data_frame.reset_index(
                drop=True,
                inplace=True
            )

            records = list(
                json.loads(
                    data_frame.T.to_json()
                ).values()
            )

            if database_name is None:
                collection = self.mongo_client.database[
                    collection_name
                ]
            else:
                collection = self.mongo_client.client[
                    database_name
                ][
                    collection_name
                ]

            # Delete old records (optional)
            collection.delete_many({})

            collection.insert_many(records)

            print(f"Inserted {len(records)} records into MongoDB")

            return len(records)

        except Exception as e:
            raise SensorException(e, sys)

    def export_collection_as_dataframe(
        self,
        collection_name: str,
        database_name: Optional[str] = None
    ) -> pd.DataFrame:

        try:

            if database_name is None:
                collection = self.mongo_client.database[
                    collection_name
                ]
            else:
                collection = self.mongo_client.client[
                    database_name
                ][
                    collection_name
                ]

            # If collection is empty, import CSV automatically
            if collection.count_documents({}) == 0:

                print("MongoDB collection is empty.")
                print("Importing CSV...")

                self.save_csv_file(
                    file_path=r"C:\Users\tukum\PYthonvscode\MLproject\aps_failure_training_set1.csv",
                    collection_name=collection_name,
                    database_name=database_name
                )

            cursor = collection.find()

            df = pd.DataFrame(list(cursor))

            if df.empty:
                raise Exception("MongoDB returned an empty DataFrame.")

            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            df.replace("na", np.nan, inplace=True)

            print(f"DataFrame Shape: {df.shape}")

            return df

        except Exception as e:
            raise SensorException(e, sys)