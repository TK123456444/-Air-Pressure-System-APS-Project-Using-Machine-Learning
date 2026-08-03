import os
import sys
import webbrowser
import threading
import pandas as pd

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import numpy as np

from sensor.constant.training_pipeline import (
    SAVED_MODEL_DIR,
    SCHEMA_FILE_PATH
)
from uvicorn import run as app_run

from sensor.logger import logging
from sensor.exception import SensorException

from sensor.pipeline.training_pipeline import TrainPipeline

from sensor.utils.main_utils import (
    read_yaml_file,
    load_object
)

from sensor.constant.training_pipeline import (
    SAVED_MODEL_DIR,
    SCHEMA_FILE_PATH
)

from sensor.constant.application import APP_HOST, APP_PORT

from sensor.ml.model.estimator import (
    ModelResolver,
    TargetValueMapping
)

# =========================================================
# ENV FILE
# =========================================================

env_file_path = os.path.join(os.getcwd(), "env.yaml")


def set_env_variable(env_file_path):
    try:
        if os.getenv("MONGO_DB_URL") is None:
            env_config = read_yaml_file(file_path=env_file_path)
            os.environ["MONGO_DB_URL"] = env_config["MONGO_DB_URL"]
    except Exception as e:
        raise SensorException(e, sys)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return RedirectResponse(url="/docs")


@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()
        return Response("Training Successful")

    except Exception as e:
        return Response(f"Error Occurred: {e}")


@app.post("/predict")
async def predict_route(file: UploadFile = File(...)):
    try:

        # ==========================================
        # SAVE UPLOADED FILE
        # ==========================================

        temp_file_path = "prediction.csv"

        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # ==========================================
        # READ CSV
        # ==========================================

        df = pd.read_csv(temp_file_path)

        # Replace "na" with NaN
        df.replace("na", np.nan, inplace=True)

        # ==========================================
        # LOAD SCHEMA
        # ==========================================

        schema = read_yaml_file(SCHEMA_FILE_PATH)

        drop_columns = schema.get("drop_columns", [])

        # Drop columns removed during training
        df.drop(
            columns=drop_columns,
            inplace=True,
            errors="ignore"
        )

        # Remove target column if uploaded
        if "class" in df.columns:
            df.drop(columns=["class"], inplace=True)

        # ==========================================
        # KEEP SAME COLUMN ORDER AS TRAINING
        # ==========================================

        feature_columns = schema["numerical_columns"]

        feature_columns = [
            col for col in feature_columns
            if col not in drop_columns
        ]

        # Add missing columns if any
        for col in feature_columns:
            if col not in df.columns:
                df[col] = np.nan

        # Keep only training columns
        df = df[feature_columns]

        print("Prediction Shape :", df.shape)

        # ==========================================
        # LOAD MODEL
        # ==========================================

        model_resolver = ModelResolver(
            model_dir=SAVED_MODEL_DIR
        )

        if not model_resolver.is_model_exists():
            return Response("Model not found")

        model = load_object(
            model_resolver.get_best_model_path()
        )

        # ==========================================
        # PREDICT
        # ==========================================

        prediction = model.predict(df)

        df["prediction"] = prediction

        df["prediction"] = df["prediction"].replace(
            TargetValueMapping().reverse_mapping()
        )

        output_path = "prediction_output.csv"

        df.to_csv(
            output_path,
            index=False
        )

        return FileResponse(
            output_path,
            filename="prediction_output.csv",
            media_type="text/csv"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(f"Error Occurred:\n{e}")

def open_browser():
    webbrowser.open(f"http://127.0.0.1:{APP_PORT}/docs")


if __name__ == "__main__":
    try:
        set_env_variable(env_file_path)

        threading.Timer(1.5, open_browser).start()

        app_run(
            app,
            host="127.0.0.1",
            port=APP_PORT
        )

    except Exception as e:
        logging.exception(e)
        print(e)