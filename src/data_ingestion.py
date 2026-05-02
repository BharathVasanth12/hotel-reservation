import os
import sys
import pandas as pd
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.logger import logging
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml_file

class DataIngestion:
    def __init__(self, config):
        if isinstance(config, str):
            config = read_yaml_file(config)

        self.config = config['data_ingestion']
        self.bucket_name = self.config['bucket_name']
        self.bucket_file_name = self.config['bucket_file_name']
        self.train_ratio = float(self.config['train_ratio'])

        os.makedirs(RAW_DIR, exist_ok=True)

        logging.info(
            f"DataIngestion started with {self.bucket_name} and file is {self.bucket_file_name}"
        )

    def download_csv_from_gcp(self):
        try:
            logging.info(f"Attempting to download {self.bucket_file_name} from GCP bucket {self.bucket_name}")
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.bucket_file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logging.info(f"Successfully downloaded {self.bucket_file_name} from GCP bucket {self.bucket_name}")
        except Exception as e:
            logging.error(f"Error downloading file from GCP: {str(e)}")
            raise CustomException(e, sys)
    
    def split_data(self):
        """
        DEPRECATED: This method is kept for backward compatibility only.
        New workflow: Preprocessing handles full dataset, then model_training.py splits it.
        """
        try:
            logging.warning("split_data() is deprecated - train/test split now happens in model_training.py after preprocessing")
            logging.info(f"Attempting to split data into train and test sets with ratio {self.train_ratio}")
            df = pd.read_csv(RAW_FILE_PATH)
            train_df, test_df = train_test_split(df, test_size=1-self.train_ratio, random_state=42)
            os.makedirs(os.path.dirname(TRAIN_FILE_PATH), exist_ok=True)
            os.makedirs(os.path.dirname(TEST_FILE_PATH), exist_ok=True)
            train_df.to_csv(TRAIN_FILE_PATH, index=False)
            test_df.to_csv(TEST_FILE_PATH, index=False)
            logging.info(f"Successfully split data into train and test sets with ratio {self.train_ratio}")
        except Exception as e:
            logging.error(f"Error splitting data into train and test sets: {str(e)}")
            raise CustomException(e, sys)
    
    def run(self, skip_split=True):
        try:
            logging.info("Starting data ingestion process.")
            self.download_csv_from_gcp()
            
            if not skip_split:
                logging.info("Running train/test split (deprecated - use model_training.py instead)")
                self.split_data()
            else:
                logging.info("Skipping train/test split (will be done after preprocessing)")
            
            logging.info("Data ingestion process completed successfully.")
        except Exception as e:
            logging.error(f"Error in data ingestion process: {str(e)}")
            raise CustomException(e, sys)
        

if __name__ == "__main__":
    try:
        data_ingestion = DataIngestion(CONFIG_FILE_PATH)
        data_ingestion.run()
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        raise CustomException(e, sys)