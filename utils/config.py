import yaml
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv() # Load environment variables from .env

def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def get_config_val(key_path, default=None):
    """
    Get a configuration value using dot-notation (e.g., 'openai.model_name').
    """
    config = load_config()
    keys = key_path.split(".")
    for key in keys:
        if isinstance(config, dict):
            config = config.get(key)
        else:
            return default
    return config if config is not None else default
