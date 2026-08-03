import sys

from sensor.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
    ModelPusherConfig
)

from sensor.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
    ModelEvaluationArtifact,
    ModelPusherArtifact
)

from sensor.component.data_ingestion import DataIngestion
from sensor.component.data_validation import DataValidation
from sensor.component.data_transformation import DataTransformation
from sensor.component.data_trainer import ModelTrainer
from sensor.component.model_evaluation import ModelEvaluation
from sensor.component.model_pusher import ModelPusher

from sensor.exception import SensorException


class TrainPipeline:

    def __init__(self):

        try:

            self.training_pipeline_config = (
                TrainingPipelineConfig()
            )

            self.is_pipeline_running = False

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # DATA INGESTION
    # =====================================================

    def start_data_ingestion(
        self
    ) -> DataIngestionArtifact:

        try:

            print("DATA INGESTION STARTED")

            data_ingestion_config = (
                DataIngestionConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            data_ingestion = DataIngestion(
                data_ingestion_config=
                data_ingestion_config
            )

            data_ingestion_artifact = (
                data_ingestion
                .initiate_data_ingestion()
            )

            print("DATA INGESTION COMPLETED")

            return data_ingestion_artifact

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # DATA VALIDATION
    # =====================================================

    def start_data_validation(
        self,
        data_ingestion_artifact:
        DataIngestionArtifact
    ) -> DataValidationArtifact:

        try:

            print("DATA VALIDATION STARTED")

            data_validation_config = (
                DataValidationConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            data_validation = DataValidation(
                data_ingestion_artifact=
                data_ingestion_artifact,

                data_validation_config=
                data_validation_config
            )

            data_validation_artifact = (
                data_validation
                .initiate_data_validation()
            )

            print("DATA VALIDATION COMPLETED")

            return data_validation_artifact

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # DATA TRANSFORMATION
    # =====================================================

    def start_data_transformation(
        self,
        data_validation_artifact:
        DataValidationArtifact
    ) -> DataTransformationArtifact:

        try:

            print("DATA TRANSFORMATION STARTED")

            data_transformation_config = (
                DataTransformationConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            data_transformation = (
                DataTransformation(
                    data_validation_artifact=
                    data_validation_artifact,

                    data_transformation_config=
                    data_transformation_config
                )
            )

            data_transformation_artifact = (
                data_transformation
                .initiate_data_transformation()
            )

            print("DATA TRANSFORMATION COMPLETED")

            return data_transformation_artifact

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # MODEL TRAINER
    # =====================================================

    def start_model_trainer(
        self,
        data_transformation_artifact:
        DataTransformationArtifact
    ) -> ModelTrainerArtifact:

        try:

            print("MODEL TRAINER STARTED")

            model_trainer_config = (
                ModelTrainerConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            model_trainer = ModelTrainer(
                model_trainer_config=
                model_trainer_config,

                data_transformation_artifact=
                data_transformation_artifact
            )

            model_trainer_artifact = (
                model_trainer
                .initiate_model_trainer()
            )

            print("MODEL TRAINER COMPLETED")

            return model_trainer_artifact

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # MODEL EVALUATION
    # =====================================================

    def start_model_evaluation(self,data_validation_artifact:DataValidationArtifact,model_trainer_artifact:ModelTrainerArtifact) -> ModelEvaluationArtifact:

        try:

            print("MODEL EVALUATION STARTED")

            model_eval_config = (
                ModelEvaluationConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            model_eval = ModelEvaluation(
                model_eval_config=
                model_eval_config,

                data_validation_artifact=
                data_validation_artifact,

                model_trainer_artifact=
                model_trainer_artifact
            )

            model_eval_artifact = (
                model_eval
                .initiate_model_evaluation()
            )

            print("MODEL EVALUATION COMPLETED")

            return model_eval_artifact

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # MODEL PUSHER
    # =====================================================

    def start_model_pusher(
        self,
        model_eval_artifact:
        ModelEvaluationArtifact

    ) -> ModelPusherArtifact:

        try:

            print("MODEL PUSHER STARTED")

            model_pusher_config = (
                ModelPusherConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            model_pusher = ModelPusher(
                model_pusher_config=
                model_pusher_config,

                model_eval_artifact=
                model_eval_artifact
            )

            model_pusher_artifact = (
                model_pusher
                .initiate_model_pusher()
            )

            print("MODEL PUSHER COMPLETED")

            return model_pusher_artifact

        except Exception as e:

            raise SensorException(e, sys)

    # =====================================================
    # RUN COMPLETE PIPELINE
    # =====================================================

    def run_pipeline(self):

        try:

            self.is_pipeline_running = True

            print("PIPELINE STARTED")

            self.data_ingestion_artifact = (
                self.start_data_ingestion()
            )

            self.data_validation_artifact = (
                self.start_data_validation(
                    data_ingestion_artifact=
                    self.data_ingestion_artifact
                )
            )

            self.data_transformation_artifact = (
                self.start_data_transformation(
                    data_validation_artifact=
                    self.data_validation_artifact
                )
            )

            self.model_trainer_artifact = (
                self.start_model_trainer(
                    data_transformation_artifact=
                    self.data_transformation_artifact
                )
            )

            self.model_evaluation_artifact = (
                self.start_model_evaluation(
                    data_validation_artifact=
                    self.data_validation_artifact,

                    model_trainer_artifact=
                    self.model_trainer_artifact
                )
            )

            if self.model_evaluation_artifact.is_model_accepted:

                self.model_pusher_artifact = (
                    self.start_model_pusher(
                        model_eval_artifact=
                        self.model_evaluation_artifact
                    )
                )

                print("MODEL ACCEPTED")

            else:

                print("MODEL REJECTED")

            print(
                "PIPELINE COMPLETED SUCCESSFULLY"
            )

        except Exception as e:

            print("PIPELINE FAILED")
            print(e)

            raise SensorException(e, sys)

        finally:

            self.is_pipeline_running = False