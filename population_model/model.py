
import numpy as np
import pandas as pd
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

def create_pop(lengde, config, rng):
    """
    Creates an initial population with a given age and sex distribution.
    """
    # Definer aldersintervaller og tilhørende sannsynligheter
    alder_intervaller = np.array(list(config['age_groups'].values()))
    
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
    alder_valg = rng.choice(
        range(len(alder_intervaller)), p=sannsynligheter, size=lengde
    )

    # Generer en spesifikk alder innenfor hvert valgt intervall
    alder = rng.integers(alder_intervaller[alder_valg, 0], alder_intervaller[alder_valg, 1] + 1)

    # Lag populasjonen
    df = pd.DataFrame({
        "sex": rng.choice(['K', 'M'], size=lengde),
        "alder": alder.astype(int),
    })
    df["barn"] = get_kids(alder, rng)
    
    return df

def get_kids(alder, rng):
    """
    Draws the number of children (0-4) for each age in alder.
    """
    kumulativ = np.cumsum([get_child_prob(a) for a in range(int(alder.max()) + 1)], axis=1) if len(alder) else np.zeros((1, 5))
    trekk = rng.random(len(alder))
    return (trekk[:, None] > kumulativ[alder, :4]).sum(axis=1).astype(int)

def create_kids(num_nye_kids, andel_gutter, rng):
    """
    Creates the newborns for one year.
    """
    return pd.DataFrame({
        "sex": np.where(rng.random(num_nye_kids) < andel_gutter, 'M', 'K'),
        "alder": np.zeros(num_nye_kids, dtype=int),
        "barn": np.zeros(num_nye_kids, dtype=int)})

def run_simulation(df, config, death_probs, target_tfr, år_start, år_slutt, yngste_fodsel, eldste_fodsel, netto_innvandring=0, start_tfr=None, fade_years=0, seed=None):
    """
    Runs the population projection simulation.

    death_probs is a dict {year: {sex: array}} with the probability of dying
    during the year by age at the start of the year (see data_manager). netto_innvandring is
    the number of net immigrants added each year.
    """
    rng = np.random.default_rng(seed)
    liste_med_antall_personer = []

    # If no start_tfr is provided, we assume no fade (instant jump to target_tfr)
    if start_tfr is None:
        start_tfr = target_tfr

    # ASFR normalisert til å summere til 1, indeksert på alder
    max_age = config.get('max_age', 110)
    asfr_norm = np.zeros(max_age + 1)
    for alder, verdi in config['asfr_norm_avg'].items():
        if yngste_fodsel <= alder <= eldste_fodsel:
            asfr_norm[alder] = verdi
    asfr_norm = asfr_norm / asfr_norm.sum()

    andel_gutter = config.get('share_boys_at_birth', 0.5)

    # Create a DataFrame for each sex and age combination
    befolkning_start = {'sex': ['K'] * max_age + ['M'] * max_age, 'alder': list(range(max_age)) * 2}
    befolkningsfordeling = pd.DataFrame(befolkning_start)
    
    df_antall = df.groupby(["alder", "sex"]).size().reset_index(name=f"pop_{år_start}")

    befolkningsfordeling = befolkningsfordeling.merge(df_antall, on = ["alder", "sex"], how="left")

    for i, year in enumerate(tqdm(range(år_start, år_slutt))):
        # Calculate current TFR for this year (linear interpolation during fade)
        if fade_years > 0 and i < fade_years:
            current_tfr = start_tfr + (target_tfr - start_tfr) * (i / fade_years)
        else:
            current_tfr = target_tfr

        alder = df['alder'].to_numpy()
        er_kvinne = (df['sex'] == 'K').to_numpy()

        # Dødsfall: sannsynligheten gjelder alderen ved starten av året
        doed_sannsynlighet = np.where(
            er_kvinne, death_probs[year]['K'][alder], death_probs[year]['M'][alder]
        )
        doed_sannsynlighet[alder >= max_age - 1] = 1.0 # Tving død ved maksalder
        survivors_mask = rng.random(len(df)) > doed_sannsynlighet
        antall_doede = int((~survivors_mask).sum())

        # Legger til 1 i alder på hele populasjonen
        df['alder'] += 1
        alder = df['alder'].to_numpy()

        # Fødsler: hver kvinne i fruktbar alder får barn med sannsynlighet ASFR for sin alder
        fodsel_sannsynlighet = np.where(er_kvinne, asfr_norm[alder] * current_tfr, 0.0)
        mor_mask = rng.random(len(df)) < fodsel_sannsynlighet
        df.loc[mor_mask, 'barn'] += 1
        nye_kids = create_kids(int(mor_mask.sum()), andel_gutter, rng)

        df = df[survivors_mask]

        deler = [df, nye_kids]
        if netto_innvandring > 0:
            deler.append(create_pop(netto_innvandring, config, rng))

        df = pd.concat(deler, ignore_index=True)

        df_antall = df.groupby(["alder", "sex"]).size().reset_index(name=f"pop_{year+1}")
        befolkningsfordeling = befolkningsfordeling.merge(df_antall, on=["alder", "sex"], how="left")
        
        antall_personer = len(df)
        liste_med_antall_personer.append(antall_personer)
        print(f"Antall fødte: {len(nye_kids)}. Antall døde: {antall_doede}. Befolkning: {antall_personer}")
        
    return liste_med_antall_personer, befolkningsfordeling, df
