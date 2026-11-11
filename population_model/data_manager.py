
import numpy as np
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

def load_death_probs(data_path, max_age):
    """
    Loads a life table (columns: sex, alder, q) and returns a dict
    {sex: array indexed by age at the start of the year} with the probability
    of dying during the year. Ages beyond the table get 1.0.

    A person who is x at the start of the year is x to x+1 through the year,
    and therefore meets half a year of mortality for age x and half for x+1.
    """
    df = pd.read_csv(data_path)
    death_probs = {}
    for sex, gruppe in df.groupby("sex"):
        q = np.ones(max_age + 2)
        q[gruppe["alder"].to_numpy()] = gruppe["q"].to_numpy()
        death_probs[sex] = 1 - np.sqrt((1 - q[:-1]) * (1 - q[1:]))
    return death_probs

def load_projected_death_probs(data_path, base_probs, years):
    """
    Loads projected death probabilities (columns: år, sex, alder, q) and returns
    a dict {year: {sex: array indexed by age at the start of the year}} for the
    given years.

    SSB's projected probabilities are given by age at the end of the year, so
    a person who is x at the start of the year meets the probability for x+1.
    Years before the first projected year use base_probs, years after the last
    use the last projected year. Ages above the projected table follow
    base_probs, scaled by the change at the oldest projected age.
    """
    df = pd.read_csv(data_path)
    første, siste = df["år"].min(), df["år"].max()
    tabeller = {}
    for (år, sex), gruppe in df.groupby(["år", "sex"]):
        base = base_probs[sex]
        q = gruppe.sort_values("alder")["q"].to_numpy()[1:]
        eldste = len(q) - 1
        probs = np.where(base < 1.0, np.minimum(base * q[eldste] / base[eldste], 1.0), 1.0)
        probs[:eldste + 1] = q
        tabeller.setdefault(år, {})[sex] = probs
    return {
        year: base_probs if year < første else tabeller[min(year, siste)]
        for year in years
    }
