
import pandas as pd
import yaml

def load_config(config_path):
    """
    Loads the configuration file.
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_population(data_path):
    """
    Loads the population data.
    """
    return pd.read_csv(data_path)

def save_population(df, data_path):
    """
    Saves the population data.
    """
    df.to_csv(data_path, index=False)
