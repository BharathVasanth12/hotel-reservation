

import os
import sys

from config.paths_config import CONFIG_FILE_PATH, MODEL_OUTPUT_PATH, PROCESSED_DIR, RAW_FILE_PATH
from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataPreprocessor
from src.model_training import ModelTrainer
from src.logger import logging
from src.custom_exception import CustomException


def run_training_pipeline():
    """
    Execute the complete training pipeline:
    1. Data Ingestion
    2. Data Preprocessing
    3. Model Training
    """

    # Step 1: Data Ingestion
    data_ingestion = DataIngestion(CONFIG_FILE_PATH)
    data_ingestion.run()
    
    # Step 2: Data Preprocessing
    PREPROCESSED_FILE_PATH = os.path.join(PROCESSED_DIR, "preprocessed_data.csv")
    preprocessor = DataPreprocessor(
        raw_data_path=RAW_FILE_PATH,
        processed_file_path=PREPROCESSED_FILE_PATH,
        config_path=CONFIG_FILE_PATH
    )
    preprocessor.run()
    
    # Step 3: Model Training
    logging.info("Step 3: Model Training")
    trainer = ModelTrainer(
        preprocessed_file_path=PREPROCESSED_FILE_PATH,
        model_output_path=MODEL_OUTPUT_PATH,
        config_path=CONFIG_FILE_PATH,
        use_hyperparameter_tuning=False  # Set to True to enable RandomizedSearchCV
    )
    metrics = trainer.run()

    return metrics

if __name__ == "__main__":
    run_training_pipeline()