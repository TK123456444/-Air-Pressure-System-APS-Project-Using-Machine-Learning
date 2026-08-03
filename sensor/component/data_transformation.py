import sys
import os

import numpy as np
import pandas as pd

from imblearn.combine import SMOTETomek

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from sensor.constant.training_pipeline import (
    TARGET_COLUMN
)

from sensor.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)

from sensor.entity.config_entity import (
    DataTransformationConfig
)

from sensor.exception import SensorException

from sensor.logger import logging

from sensor.ml.model.estimator import (
    TargetValueMapping
)

from sensor.utils.main_utils import (
    save_numpy_array_data,
    save_object
)


class DataTransformation:
    def __init__(self,data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact = (data_validation_artifact)

            self.data_transformation_config = (data_transformation_config)
        except Exception as e:
            raise SensorException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:

        try:

            return pd.read_csv(file_path)

        except Exception as e:

            raise SensorException(e, sys)

    @classmethod
    def get_data_transformer_object(
        cls
    ) -> Pipeline:

        try:

            logging.info(
                "Creating preprocessing object"
            )

            simple_imputer = SimpleImputer(
                strategy="constant",
                fill_value=0
            )

            robust_scaler = RobustScaler()

            preprocessor = Pipeline(
                steps=[
                    (
                        "Imputer",
                        simple_imputer
                    ),

                    (
                        "RobustScaler",
                        robust_scaler
                    )
                ]
            )

            return preprocessor

        except Exception as e:

            raise SensorException(e, sys)

    def initiate_data_transformation(
        self
    ) -> DataTransformationArtifact:

        try:

            print("DATA TRANSFORMATION STARTED")

            # ==================================================
            # READ TRAIN AND TEST DATA
            # ==================================================

            train_df = DataTransformation.read_data(
                self.data_validation_artifact.valid_train_file_path
            )

            test_df = DataTransformation.read_data(
                self.data_validation_artifact.valid_test_file_path
            )

            print(f"Train Shape: {train_df.shape}")
            print(f"Test Shape: {test_df.shape}")

            # ==================================================
            # PREPROCESSOR
            # ==================================================

            preprocessor = (
                self.get_data_transformer_object()
            )

            # ==================================================
            # TRAIN INPUT/TARGET
            # ==================================================

            input_feature_train_df = train_df.drop(
                columns=[TARGET_COLUMN]
            )

            target_feature_train_df = (
                train_df[TARGET_COLUMN]
            )

            # ==================================================
            # TARGET MAPPING
            # ==================================================

            target_feature_train_df = (
                target_feature_train_df
                .replace({
                    "neg": 0,
                    "pos": 1
                })
            )

            # convert target into integer
            target_feature_train_df = (
                pd.to_numeric(
                    target_feature_train_df,
                    errors="coerce"
                )
            )

            target_feature_train_df = (
                target_feature_train_df.astype(int)
            )

            # ==================================================
            # TEST INPUT/TARGET
            # ==================================================

            input_feature_test_df = test_df.drop(
                columns=[TARGET_COLUMN]
            )

            target_feature_test_df = (
                test_df[TARGET_COLUMN]
            )

            target_feature_test_df = (
                target_feature_test_df
                .replace({
                    "neg": 0,
                    "pos": 1
                })
            )

            target_feature_test_df = (
                pd.to_numeric(
                    target_feature_test_df,
                    errors="coerce"
                )
            )

            target_feature_test_df = (
                target_feature_test_df.astype(int)
            )

            print("TARGET COLUMN CONVERTED")

            # ==================================================
            # FIT TRANSFORM
            # ==================================================

            preprocessor_object = (
                preprocessor.fit(
                    input_feature_train_df
                )
            )

            transformed_input_train_feature = (
                preprocessor_object.transform(
                    input_feature_train_df
                )
            )

            transformed_input_test_feature = (
                preprocessor_object.transform(
                    input_feature_test_df
                )
            )

            print("DATA TRANSFORMATION DONE")

            # ==================================================
            # SMOTE
            # ==================================================

            smt = SMOTETomek(
                sampling_strategy="minority",
                random_state=42
            )

            input_feature_train_final, target_feature_train_final = (
                smt.fit_resample(
                    transformed_input_train_feature,
                    target_feature_train_df
                )
            )

            input_feature_test_final, target_feature_test_final = (
                smt.fit_resample(
                    transformed_input_test_feature,
                    target_feature_test_df
                )
            )

            print("SMOTE APPLIED")

            # ==================================================
            # CREATE NUMPY ARRAY
            # ==================================================

            train_arr = np.c_[
                input_feature_train_final,
                np.array(target_feature_train_final)
            ]

            test_arr = np.c_[
                input_feature_test_final,
                np.array(target_feature_test_final)
            ]

            # ==================================================
            # SAVE TRANSFORMED FILES
            # ==================================================

            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_train_file_path,
                array=train_arr
            )

            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_test_file_path,
                array=test_arr
            )

            save_object(
                file_path=self.data_transformation_config.transformed_object_file_path,
                obj=preprocessor_object
            )

            print("train.npy SAVED")
            print("test.npy SAVED")
            print("preprocessing.pkl SAVED")

            # ==================================================
            # ARTIFACT
            # ==================================================

            data_transformation_artifact = (
                DataTransformationArtifact(
                    transformed_object_file_path=
                    self.data_transformation_config.transformed_object_file_path,

                    transformed_train_file_path=
                    self.data_transformation_config.transformed_train_file_path,

                    transformed_test_file_path=
                    self.data_transformation_config.transformed_test_file_path
                )
            )
            print("DATA TRANSFORMATION COMPLETED")

            return data_transformation_artifact

        except Exception as e:

            print("DATA TRANSFORMATION ERROR")
            print(e)

            raise SensorException(e, sys)