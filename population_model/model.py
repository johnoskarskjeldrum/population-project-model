
import numpy as np
import pandas as pd
import random
from tqdm import tqdm

from population_model.utils import get_age_group

def create_pop(lengde, config):
    """
    Creates an initial population with a given age and sex distribution.
    """
    # Definer aldersintervaller og tilhørende sannsynligheter
    alder_intervaller = list(config['age_groups'].values())
    
    sannsynligheter = [
        0.04974, 0.05486, 0.05956, 0.06003, 0.06034, 0.06653,
        0.07160, 0.06885, 0.06543, 0.06432, 0.06860, 0.06561,
        0.05785, 0.05281, 0.04631, 0.04137, 0.02441, 0.01356,
        0.00630, 0.00171, 0.00023
    ]

    # Normaliser sannsynlighetene slik at de summerer til 1
    total = sum(sannsynligheter)
    sannsynligheter = [s / total for s in sannsynligheter]

    # Velg aldersintervaller for populasjonen basert på sannsynligheter
    alder_valg = np.random.choice(
        range(len(alder_intervaller)), p=sannsynligheter, size=lengde
    )

    # Generer en spesifikk alder innenfor hvert valgt intervall
    alder = [
        random.randint(alder_intervaller[i][0], alder_intervaller[i][1])
        for i in alder_valg
    ]

    # Lag populasjonen
    population = {
        "sex": [random.choice(['K', 'M']) for _ in range(lengde)], 
        "alder": alder,
    }
    
    df = pd.DataFrame(population)
    df["barn"] = df.alder.apply(get_kids)
    
    return df

def get_kids(age):
    values = [0, 1, 2, 3, 4]
    
    if age > 40:
        return random.choices(values, weights=[14.7, 16.5,41.3,20.7,6.8], k=1)[0]
    elif age > 35:
        return random.choices(values, weights=[17.6,17.2,41.7,18.2,5.3], k=1)[0]
    elif age > 30:
        return random.choices(values, weights=[26.7,21.2,36.4,12.5,3.2], k=1)[0]
    elif age > 25:
        return random.choices(values, weights=[87.6,8.5,3.3,0.5,0.1,], k=1)[0]
    elif age > 20:
        return random.choices(values, weights=[98.8, 1.1, 0.1, 0, 0], k=1)[0]
    elif age > 15:
        return random.choices(values, weights=[99.5, 0.5, 0, 0, 0], k=1)[0]
    else:
        return 0

def dodsfall(df, config):
    """
    Simulates the deaths in the population.
    """
    df['aldersgruppe'] = df['alder'].apply(get_age_group, args=(config['age_groups'],))
    df['vekter'] = df['aldersgruppe'].map(config['death_rates'])
    antall_dode = int(len(df) * 0.008)
    dode = df.sample(n=antall_dode, weights="vekter").index
            
    return dode

def create_kids(fruktbare_damer, asfr):
    
    age_group_barn = fruktbare_damer.merge(asfr[["alder", "asfr"]], on = "alder", how="inner", validate = "1:1")
    age_group_barn["barn"] = (age_group_barn["asfr"] * (age_group_barn["sex"] / 1000)).astype(int)
    num_nye_kids = int(age_group_barn["barn"].sum())
    
    nye_kids = (
        pd.DataFrame({
            "sex": [random.choice(['K', 'M']) for _ in range(num_nye_kids)], 
            "alder": [0] * num_nye_kids,
            "barn": [0] * num_nye_kids}))
    
    return nye_kids, age_group_barn[["alder", "barn"]]

def run_simulation(df, config, tfr, år_start, år_slutt, yngste_fodsel, eldste_fodsel, innvandring=True, innvandringsgrad=0.95):
    """
    Runs the population projection simulation.
    """
    liste_med_antall_personer = []

    # Setter ASFT for de ulike aldersgruppene
    asfr_sum = (tfr) * 1000
    asfr = pd.DataFrame(list(config['asfr_norm_avg'].items()), columns=['alder', 'asfr_norm'])
    asfr["asfr"] = asfr.asfr_norm * asfr_sum
    
    # Create a DataFrame for each sex and age combination
    befolkning_start = {'sex': ['K'] * 110 + ['M'] * 110, 'alder': list(range(110)) * 2}
    befolkningsfordeling = pd.DataFrame(befolkning_start)
    
    df_antall = df.groupby(["alder", "sex"]).barn.count().sort_index().reset_index().rename(columns={"barn":f"pop_{2023}"})#
    befolkningsfordeling = befolkningsfordeling.merge(df_antall, on = ["alder", "sex"], how="left")
    
    
    for year in tqdm(range(år_start, år_slutt)):
        # Legger til 1 i alder på hele populasjonen
        df['alder'] += 1
        
        if "aldersgruppe" in df.columns:
            df = df.drop("aldersgruppe", axis=1)
        
         # Assign weights
        df['aldersgruppe'] = df['alder'].apply(get_age_group, args=(config['age_groups'],))
        # Disse vektene setter sannsynlighet for død
        df['vekter'] = df['aldersgruppe'].map(config['death_rates'])
        
        fruktbare_damer = df.loc[(df.alder >= yngste_fodsel) & (df.alder < eldste_fodsel) & (df.sex == "K") & (df.barn < 4)].groupby("alder")["sex"].count().reset_index()
        
        asfr["asfr"] = asfr.asfr_norm * (asfr_sum + random.randint(-4, 4))
        # Definerer fruktbare damer
        nye_kids, age_group_df = create_kids(fruktbare_damer, asfr)

        # Vi legger til barn for de ulike individene ved å legge til 
        for index, row in age_group_df.iterrows():
            age_group = row['alder']
            num_new_kids = int(row["barn"])

            # Vi velger ut individene, vi dropper å legge til barn for mennene, da det ikke har noen egen effekt på simulering
            # Menn kan også egentlig få uendelig med barn
            eligible_individuals = df[(df['alder'] == age_group ) & (df["sex"] == "K")]

            # Sample the required number of individuals
            sampled_indices = np.random.choice(eligible_individuals.index, num_new_kids, replace=True)

            # Increment the 'barn' column for the sampled individuals
            df.loc[sampled_indices, 'barn'] += 1
        

        # Legger til innvandring i populasjonen
        if innvandring:
            if year in [0, 1]:
                innvandrere = 30_000
            else:
                innvandrere = int(np.linspace(18000, 4000, 100)[year-2])
        else:
            innvandrere = 0

        innvandrere_df = create_pop(innvandrere, config)
        
        # Define fractions to remove
        fraction_over_90 = 1/4
        fraction_over_100 = 1/2
        
        # fjerner døde    
        # Remove 1/4 of the population over 90 years old
        over_90 = df[df['alder'] > 90]
        sample_over_90 = over_90.sample(frac=fraction_over_90, random_state=42)
        df = df.drop(sample_over_90.index)

        # Remove 1/2 of the population over 100 years old
        over_100 = df[df['alder'] > 100]
        sample_over_100 = over_100.sample(frac=fraction_over_100, random_state=42)
        df = df.drop(sample_over_100.index)
        
        dodsrate = max(0.002, 0.008 - (((len(over_90) / 4) + (len(over_100) / 2)) / len(df)))
        
        dode_index = dodsfall(df, config)        
        df = df.drop(dode_index)

        df = pd.concat([df, nye_kids, innvandrere_df]).reset_index(drop=True)
        df.drop(columns=['vekter'], inplace=True)

        df_antall = df.groupby(["alder", "sex"]).barn.count().sort_index().reset_index().rename(columns={"barn":f"pop_{2024+year}"})#
        befolkningsfordeling = befolkningsfordeling.merge(df_antall, on = ["alder", "sex"], how="left")
        
        liste_med_antall_personer.append(len(df))
        print(f"Antall fødte: {len(nye_kids)}. Dødsrate: {dodsrate}. Antall døde: {len(dode_index)}. Befolkning: {len(df)}")
        
        
    return liste_med_antall_personer, befolkningsfordeling, df
