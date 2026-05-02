import os
import sys
import pandas as pd
import yaml

from src.logger import logging
from src.custom_exception import CustomException

def read_yaml_file(file_path: str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        
        with open(file_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        logging.info(f"Successfully read YAML file: {file_path}")
        return config
    except Exception as e:
        logging.error(f"Error reading YAML file: {file_path} - {str(e)}")
        raise CustomException(e, sys)
    
def load_data(path: str):
    try:
        logging.info(f"Attempting to load data from: {path}")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data file not found: {path}")
        
        data = pd.read_csv(path)
        logging.info(f"Successfully loaded data from: {path}")
        return data
    except Exception as e:
        logging.error(f"Error loading data from: {path} - {str(e)}")
        raise CustomException(e, sys)