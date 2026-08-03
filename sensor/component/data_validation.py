import os
import sys
import pandas as pd

from scipy.stats import ks_2samp

from sensor.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact
)

from sensor.entity.config_entity import (
    DataValidationConfig
)

from sensor.exception import SensorException

from sensor.logger import logging

from sensor.utils.main_utils import (
    read_yaml_file,
    write_yaml_file
)

from sensor.constant.training_pipeline import (
    SCHEMA_FILE_PATH
)


class DataValidation:

    def __init__(self,
    data_ingestion_artifact: DataIngestionArtifact,
    data_validation_config: DataValidationConfig):

        try:

            self.data_ingestion_artifact = (
                data_ingestion_artifact
            )

            self.data_validation_config = (
                data_validation_config
)
            self._schema_config = read_yaml_file(
                SCHEMA_FILE_PATH         )
        except Exception as e:
            raise SensorException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:

        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise SensorException(e, sys)

    # =====================================================
    # VALIDATE NUMBER OF COLUMNS
    # =====================================================

    def validate_number_of_columns(
        self,
        dataframe: pd.DataFrame
    ) -> bool:

        try:

            schema_columns = (
                self._schema_config["columns"]
            )

            drop_columns = (
                self._schema_config["drop_columns"]
            )

            expected_columns = []

            # =========================================
            # EXTRACT COLUMN NAMES FROM YAML
            # =========================================

            for item in schema_columns:

                if isinstance(item, dict):

                    column_name = (
                        list(item.keys())[0]
                    )

                    # Skip dropped columns
                    if column_name not in drop_columns:

                        expected_columns.append(
                            column_name
                        )

            print(
                f"Expected Columns: "
                f"{len(expected_columns)}"
            )

            print(
                f"Actual Columns: "
                f"{len(dataframe.columns)}"
            )

            # =========================================
            # FIND MISSING COLUMNS
            # =========================================

            missing_columns = []
            for column in expected_columns:
                if column not in dataframe.columns:
                    missing_columns.append(column)
            if len(missing_columns) > 0:
                print("\nMissing Columns:")
                print(missing_columns)
                return False
            return True
        except Exception as e:
            raise SensorException(e, sys)

    # =====================================================
    # CHECK NUMERICAL COLUMNS
    # =====================================================

    def is_numerical_column_exist(self,dataframe: pd.DataFrame) -> bool:

        try:

            numerical_columns = (
                self._schema_config[
                    "numerical_columns"
                ]
            )

            dataframe_columns = (
                dataframe.columns
            )

            missing_columns = []

            for column in numerical_columns:

                if column not in dataframe_columns:

                    missing_columns.append(column)

            if len(missing_columns) > 0:

                print("\nMissing Numerical Columns:")
                print(missing_columns)

                return False

            return True

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # DATA DRIFT
    # =====================================================

    def detect_dataset_drift(
        self,
        base_df: pd.DataFrame,
        current_df: pd.DataFrame,
        threshold=0.05
    ) -> bool:

        try:

            status = True

            report = {}

            for column in base_df.columns:

                d1 = base_df[column]

                d2 = current_df[column]

                is_same_dist = ks_2samp(
                    d1,
                    d2
                )

                if threshold <= is_same_dist.pvalue:

                    is_found = False

                else:

                    is_found = True

                    status = False

                report.update({

                    column: {

                        "p_value": float(
                            is_same_dist.pvalue
                        ),

                        "drift_status": is_found
                    }
                })

            drift_report_file_path = (
                self.data_validation_config
                .drift_report_file_path
            )

            dir_path = os.path.dirname(
                drift_report_file_path
            )

            os.makedirs(
                dir_path,
                exist_ok=True
            )

            write_yaml_file(
                file_path=drift_report_file_path,
                content=report
            )

            return status

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # INITIATE DATA VALIDATION
    # =====================================================

    def initiate_data_validation(self) -> DataValidationArtifact:

        try:

            error_message = ""

            train_file_path = (
                self.data_ingestion_artifact
                .train_file_path
            )

            test_file_path = (
                self.data_ingestion_artifact
                .test_file_path
            )

            # =========================================
            # READ DATA
            # =========================================

            train_dataframe = (
                self.read_data(
                    train_file_path
                )
            )

            test_dataframe = (
                self.read_data(
                    test_file_path
                )
            )

            # =========================================
            # VALIDATE COLUMNS
            # =========================================

            status = (
                self.validate_number_of_columns(
                    dataframe=train_dataframe
                )
            )

            if not status:

                error_message += (
                    "Train dataframe column mismatch\n"
                )

            status = (
                self.validate_number_of_columns(
                    dataframe=test_dataframe
                )
            )

            if not status:

                error_message += (
                    "Test dataframe column mismatch\n"
                )

            # =========================================
            # VALIDATE NUMERICAL COLUMNS
            # =========================================

            status = (
                self.is_numerical_column_exist(
                    dataframe=train_dataframe
                )
            )

            if not status:

                error_message += (
                    "Train numerical columns missing\n"
                )

            status = (
                self.is_numerical_column_exist(
                    dataframe=test_dataframe
                )
            )

            if not status:

                error_message += (
                    "Test numerical columns missing\n"
                )

            # =========================================
            # ERROR CHECK
            # =========================================

            if len(error_message) > 0:

                raise Exception(
                    error_message
                )

            # =========================================
            # DATA DRIFT
            # =========================================

            status = (
                self.detect_dataset_drift(
                    base_df=train_dataframe,
                    current_df=test_dataframe
                )
            )

            # =========================================
            # ARTIFACT
            # =========================================

            data_validation_artifact = (
                DataValidationArtifact(

                    validation_status=status,

                    valid_train_file_path=(
                        train_file_path
                    ),

                    valid_test_file_path=(
                        test_file_path
                    ),

                    invalid_train_file_path=None,

                    invalid_test_file_path=None,

                    drift_report_file_path=(
                        self.data_validation_config
                        .drift_report_file_path
                    )
                )
            )

            logging.info(
                f"Data Validation Artifact: "
                f"{data_validation_artifact}"
            )

            return data_validation_artifact

        except Exception as e:

            raise SensorException(e, sys)