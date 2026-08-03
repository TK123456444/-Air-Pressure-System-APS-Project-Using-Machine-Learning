from sklearn.metrics import f1_score, precision_score, recall_score
from sensor.entity.artifact_entity import ClassificationMetricArtifact
from sensor.exception import SensorException
import numpy as np
import pandas as pd
import sys


def get_classification_score(y_true, y_pred) -> ClassificationMetricArtifact:
    try:
        # Convert to pandas Series
        y_true = pd.Series(y_true)
        y_pred = pd.Series(y_pred)

        print("=" * 60)
        print("y_true dtype:", y_true.dtype)
        print("y_pred dtype:", y_pred.dtype)
        print("Unique y_true:", y_true.unique())
        print("Unique y_pred:", y_pred.unique())
        print("=" * 60)

        # Convert labels if required
        mapping = {"neg": 0, "pos": 1}
        y_true = y_true.replace(mapping)
        y_pred = y_pred.replace(mapping)

        # Convert to integers
        y_true = y_true.astype(int)
        y_pred = y_pred.astype(int)

        model_f1_score = f1_score(y_true, y_pred)
        model_precision_score = precision_score(y_true, y_pred)
        model_recall_score = recall_score(y_true, y_pred)

        classification_metric = ClassificationMetricArtifact(
            f1_score=model_f1_score,
            precision_score=model_precision_score,
            recall_score=model_recall_score,
        )

        return classification_metric

    except Exception as e:
        raise SensorException(e, sys)