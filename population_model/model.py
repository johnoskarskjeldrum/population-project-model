
import numpy as np
import pandas as pd
import random
from tqdm import tqdm
from pathlib import Path
import glob

CHILD_DISTRIBUTION_DATA = {}

def load_child_distribution_data(data_path):
    """
    Loads child distribution data from CSV files in the data_barnefordeling directory.
    """
    global CHILD_DISTRIBUTION_DATA
    search_path = data_path / "data_barnefordeling" / "*_Kvinnen.csv"
    files = glob.glob(str(search_path))
    
    if not files:
        print(f"Warning: No child distribution files found in {search_path}")
        return

    for file_path in files:
        try:
            # Extract age from filename (e.g., "20_Kvinnen.csv" -> 20)
            age = int(Path(file_path).name.split('_')[0])
            
            df = pd.read_csv(file_path)
            # Use the last row (latest year)
            latest_row = df.iloc[-1]
            
            # Parse probabilities (replace comma with dot and convert to float)
            probs = []
            for col in ["0 barn", "1 barn", "2 barn", "3 barn", "4 barn eller flere"]:
                val = str(latest_row[col]).replace(',', '.')
                probs.append(float(val) / 100.0) # Convert percentage to probability
            
            # Normalize to ensure sum is 1.0
            total_prob = sum(probs)
            if total_prob > 0:
                probs = [p / total_prob for p in probs]
            
            CHILD_DISTRIBUTION_DATA[age] = probs
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    print(f"Loaded child distribution data for ages: {sorted(CHILD_DISTRIBUTION_DATA.keys())}")

def get_child_prob(age):
    """
    Returns the probability distribution of having 0, 1, 2, 3, 4+ children for a given age.
    Interpolates between available data points.
    """
    if not CHILD_DISTRIBUTION_DATA:
        # Fallback if data not loaded
        return [1.0, 0, 0, 0, 0] # Default to 0 kids

    available_ages = sorted(CHILD_DISTRIBUTION_DATA.keys())
    
    # If age is below min or above max available, use the closest
    if age <= available_ages[0]:
        return CHILD_DISTRIBUTION_DATA[available_ages[0]]
    if age >= available_ages[-1]:
        return CHILD_DISTRIBUTION_DATA[available_ages[-1]]
    
    # Find the two closest ages to interpolate between
    lower_age = max([a for a in available_ages if a <= age])
    upper_age = min([a for a in available_ages if a >= age])
    
    if lower_age == upper_age:
        return CHILD_DISTRIBUTION_DATA[lower_age]
    
    # Linear interpolation
    weight = (age - lower_age) / (upper_age - lower_age)
    lower_probs = np.array(CHILD_DISTRIBUTION_DATA[lower_age])
    upper_probs = np.array(CHILD_DISTRIBUTION_DATA[upper_age])
    
    interpolated_probs = (1 - weight) * lower_probs + weight * upper_probs
    return interpolated_probs.tolist()

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
    weights = get_child_prob(age)
    return random.choices(values, weights=weights, k=1)[0]

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

def run_simulation(df, config, tfr, år_start, år_slutt, yngste_fodsel, eldste_fodsel, innvandring=True):
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
    
    # Forbered bins for pd.cut
    age_groups = config['age_groups']
    bins = [age_groups[key][0] for key in age_groups] + [age_groups[list(age_groups.keys())[-1]][1]]
    labels = list(age_groups.keys())

    for year in tqdm(range(år_start, år_slutt)):
        # Legger til 1 i alder på hele populasjonen
        df['alder'] += 1
        
        # Vektoriser aldersgruppetildeling
        df['aldersgruppe'] = pd.cut(df['alder'], bins=bins, labels=labels, right=False)
        df['vekter'] = df['aldersgruppe'].map(config['death_rates'])
        
        fruktbare_damer = df.loc[(df.alder >= yngste_fodsel) & (df.alder < eldste_fodsel) & (df.sex == "K") & (df.barn < 4)].groupby("alder")["sex"].count().reset_index()
        
        asfr["asfr"] = asfr.asfr_norm * (asfr_sum + random.randint(-4, 4))
        nye_kids, age_group_df = create_kids(fruktbare_damer, asfr)

        # Vektoriser tildeling av barn
        indices_to_increment = []
        for _, row in age_group_df.iterrows():
            age_group = row['alder']
            num_new_kids = int(row["barn"])
            eligible_indices_women = df.index[(df['alder'] == age_group) & (df['sex'] == 'K') & (df['barn'] < 4)]
            eligible_indices_men = df.index[(df['alder'] == age_group) & (df['sex'] == 'M') & (df['barn'] < 4)]

            if not eligible_indices_women.empty:
                sampled_indices_women = np.random.choice(eligible_indices_women, num_new_kids, replace=True)
                indices_to_increment.extend(sampled_indices_women)
            if not eligible_indices_men.empty:
                sampled_indices_men = np.random.choice(eligible_indices_men, num_new_kids, replace=True)
                indices_to_increment.extend(sampled_indices_men)
        
        if indices_to_increment:
            df.loc[indices_to_increment, 'barn'] += 1

        # Legg til innvandring basert på en rate
        if innvandring:
            innvandrere = int(len(df) * config['immigration_rate'])
        else:
            innvandrere = 0

        innvandrere_df = create_pop(innvandrere, config)
        
        # Effektiviser dødsfall
        deterministic_indices_to_drop = []
        
        # 1. Fjern de som har nådd maksalder
        max_age_indices = df.index[df['alder'] >= config['max_age']]
        if not max_age_indices.empty:
            deterministic_indices_to_drop.extend(max_age_indices)

        # 2. Fjern en andel av de eldste
        over_90_pool = df[(df['alder'] > 90) & (~df.index.isin(deterministic_indices_to_drop))]
        if not over_90_pool.empty:
            sample_over_90 = over_90_pool.sample(frac=1/4, random_state=42)
            deterministic_indices_to_drop.extend(sample_over_90.index)

        over_100_pool = df[(df['alder'] > 100) & (~df.index.isin(deterministic_indices_to_drop))]
        if not over_100_pool.empty:
            sample_over_100 = over_100_pool.sample(frac=1/2, random_state=42)
            deterministic_indices_to_drop.extend(sample_over_100.index)
        
        # 3. Beregn tilfeldige dødsfall fra resten av befolkningen
        remaining_for_random_death_df = df.drop(list(set(deterministic_indices_to_drop)))
        
        dodsrate = max(0.002, 0.008 - (len(deterministic_indices_to_drop) / len(df)))
        num_random_deaths = int(len(remaining_for_random_death_df) * dodsrate)
        
        all_indices_to_drop = list(set(deterministic_indices_to_drop))
        if num_random_deaths > 0:
            random_death_indices = remaining_for_random_death_df.sample(n=num_random_deaths, weights="vekter").index
            all_indices_to_drop.extend(random_death_indices)

        df = df.drop(all_indices_to_drop)

        df = pd.concat([df, nye_kids, innvandrere_df], ignore_index=True)
        df.drop(columns=['vekter', 'aldersgruppe'], inplace=True, errors='ignore')

        df_antall = df.groupby(["alder", "sex"]).size().reset_index(name=f"pop_{year+1}")
        befolkningsfordeling = befolkningsfordeling.merge(df_antall, on=["alder", "sex"], how="left")
        
        antall_personer = len(df)
        liste_med_antall_personer.append(antall_personer)
        print(f"Antall fødte: {len(nye_kids)}. Dødsrate: {dodsrate}. Antall døde: {len(all_indices_to_drop)}. Befolkning: {antall_personer}")
        
    return liste_med_antall_personer, befolkningsfordeling, df
