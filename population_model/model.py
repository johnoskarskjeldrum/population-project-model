
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
    
    # Justert for å reflektere at innvandrere typisk er unge voksne (spesielt 20-35 år)
    sannsynligheter = [
        0.02, 0.03, 0.04, 0.08, 0.18, 0.22, # 0-4 til 25-29
        0.18, 0.10, 0.06, 0.04, 0.02, 0.01, # 30-34 til 55-59
        0.005, 0.005, 0.005, 0.003, 0.001, 0.001, # 60-64 til 85-89
        0.000, 0.000, 0.000 # 90+
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

def run_simulation(df, config, target_tfr, år_start, år_slutt, yngste_fodsel, eldste_fodsel, innvandring=True, start_tfr=None, fade_years=0):
    """
    Runs the population projection simulation.
    """
    liste_med_antall_personer = []

    # If no start_tfr is provided, we assume no fade (instant jump to target_tfr)
    if start_tfr is None:
        start_tfr = target_tfr

    # Pre-load ASFR normalization
    asfr = pd.DataFrame(list(config['asfr_norm_avg'].items()), columns=['alder', 'asfr_norm'])
    
    # Create a DataFrame for each sex and age combination
    befolkning_start = {'sex': ['K'] * 110 + ['M'] * 110, 'alder': list(range(110)) * 2}
    befolkningsfordeling = pd.DataFrame(befolkning_start)
    
    df_antall = df.groupby(["alder", "sex"]).size().reset_index(name=f"pop_{år_start}")

    befolkningsfordeling = befolkningsfordeling.merge(df_antall, on = ["alder", "sex"], how="left")
    
    # Generer dødsannsynligheter for hvert enkelt år (0 til 120)
    max_possible_age = 120
    death_probs = np.zeros(max_possible_age + 1)
    for age in range(max_possible_age + 1):
        if age < 60:
            death_probs[age] = 0.001
        elif age < 90:
            # Gradvis økning fra 60 til 90 (når ca 12% ved 90)
            death_probs[age] = 0.001 * np.exp(0.13 * (age - 60))
        else:
            # Veldig bratt økning etter 90 år (biologisk grense)
            # 90 år = ~12%, 100 år = ~35%, 105 år = ~60%
            base_90 = 0.12
            death_probs[age] = base_90 + ((age - 90) * 0.035) 
            
    death_probs[death_probs > 1.0] = 1.0
    death_probs[config.get('max_age', 110):] = 1.0 # Tving død ved maksalder

    for i, year in enumerate(tqdm(range(år_start, år_slutt))):
        # Calculate current TFR for this year (linear interpolation during fade)
        if fade_years > 0 and i < fade_years:
            current_tfr = start_tfr + (target_tfr - start_tfr) * (i / fade_years)
        else:
            current_tfr = target_tfr

        asfr_sum = current_tfr * 1000
        asfr["asfr"] = asfr.asfr_norm * (asfr_sum + random.randint(-4, 4))

        # Legger til 1 i alder på hele populasjonen
        df['alder'] += 1
        
        fruktbare_damer = df.loc[(df.alder >= yngste_fodsel) & (df.alder < eldste_fodsel) & (df.sex == "K") & (df.barn < 4)].groupby("alder")["sex"].count().reset_index()
        
        nye_kids, age_group_df = create_kids(fruktbare_damer, asfr)

        # Vektoriser tildeling av barn (kun til kvinner for å unngå dobbelttelling og fikse fordeling)
        indices_to_increment = []
        for _, row in age_group_df.iterrows():
            age_group = row['alder']
            num_new_kids = int(row["barn"])
            eligible_indices_women = df.index[(df['alder'] == age_group) & (df['sex'] == 'K') & (df['barn'] < 4)]

            if not eligible_indices_women.empty:
                sampled_indices_women = np.random.choice(eligible_indices_women, num_new_kids, replace=True)
                indices_to_increment.extend(sampled_indices_women)
        
        if indices_to_increment:
            counts = pd.Series(indices_to_increment).value_counts()
            df.loc[counts.index, 'barn'] += counts.values

        # Legg til innvandring basert på en rate
        if innvandring:
            innvandrere = int(len(df) * config['immigration_rate'])
        else:
            innvandrere = 0

        innvandrere_df = create_pop(innvandrere, config)
        
        # Vektoriserte dødsfall ved bruk av numpy
        # Klipp alder for å ikke overskride maksimum i death_probs
        clipped_alder = np.clip(df['alder'].values, 0, max_possible_age).astype(int)
        current_death_probs = death_probs[clipped_alder]
        
        # Trekk tilfeldige tall for hver person og sjekk hvem som dør
        random_draws = np.random.rand(len(df))
        survivors_mask = random_draws > current_death_probs
        
        all_indices_to_drop = df.index[~survivors_mask]
        df = df[survivors_mask]

        df = pd.concat([df, nye_kids, innvandrere_df], ignore_index=True)

        df_antall = df.groupby(["alder", "sex"]).size().reset_index(name=f"pop_{year+1}")
        befolkningsfordeling = befolkningsfordeling.merge(df_antall, on=["alder", "sex"], how="left")
        
        antall_personer = len(df)
        liste_med_antall_personer.append(antall_personer)
        print(f"Antall fødte: {len(nye_kids)}. Antall døde: {len(all_indices_to_drop)}. Befolkning: {antall_personer}")
        
    return liste_med_antall_personer, befolkningsfordeling, df
