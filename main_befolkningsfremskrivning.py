import numpy as np
import random
import pandas as pd
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
from pathlib import Path


data = Path("data")

os.listdir(data)


def create_pop(lengde):
    # Definer aldersintervaller og tilhørende sannsynligheter
    alder_intervaller = [
        (0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29),
        (30, 34), (35, 39), (40, 44), (45, 49), (50, 54), (55, 59),
        (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89),
        (90, 94), (95, 99), (100, 104)
    ]
    
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
        "barn": [random.randint(1, 4) if alder[i] > 20 else 0 for i in range(lengde)]
    }

    df = pd.DataFrame(population)
    return df

# Generer en populasjon på 100,000 individer
populasjon = create_pop(100_000)
print(populasjon)


import pandas as pd
import random
from tqdm import tqdm

dodsrate = 0.008
def get_age_group(age):
    if age < 5:
        return '0-4'
    elif age < 10:
        return '5-9'
    elif age < 15:
        return '10-14'
    elif age < 20:
        return '15-19'
    elif age < 25:
        return '20-24'
    elif age < 30:
        return '25-29'
    elif age < 35:
        return '30-34'
    elif age < 40:
        return '35-39'
    elif age < 45:
        return '40-44'
    elif age < 50:
        return '45-49'
    elif age < 55:
        return '50-54'
    elif age < 60:
        return '55-59'
    elif age < 65:
        return '60-64'
    elif age < 70:
        return '65-69'
    elif age < 75:
        return '70-74'
    elif age < 80:
        return '75-79'
    elif age < 85:
        return '80-84'
    elif age < 90:
        return '85-89'
    elif age < 95:
        return '90-94'
    elif age < 100:
        return '95-99'
    else:
        return '100+'

# Definerer aldersgrupper og deres respektive vekter
age_groups = {
    '0-4': 0.00133,
    '5-9': 0.00133,
    '10-14': 0.00080,
    '15-19': 0.00080,
    '20-24': 0.00171,
    '25-29': 0.00171,
    '30-34': 0.00276,
    '35-39': 0.00276,
    '40-44': 0.00506,
    '45-49': 0.00506,
    '50-54': 0.01196,
    '55-59': 0.01196,
    '60-64': 0.03285,
    '65-69': 1,
    '70-74': 2,
    '75-79': 4,
    '80-84': 8,
    '85-89': 16,
    '90-94': 0,
    '95-99': 0,
    '100+': 0
}

asfr_norm_avg = {
    15: 0.0000223,
    16: 0.00015456666081951678,
    17: 0.0004949861781749781,
    18: 0.0011674475260175403,
    19: 0.0033592304084229915,
    20: 0.0055138033164292225,
    21: 0.009514667201587971,
    22: 0.014315699164430738,
    23: 0.019837655531792474,
    24: 0.027895650211561356,
    25: 0.03682567554371083,
    26: 0.04893903823222015,
    27: 0.056379833310768214,
    28: 0.0687315396068868,
    29: 0.07576266588023392,
    30: 0.08200941908861684,
    31: 0.08235265382956841,
    32: 0.0807535491015141,
    33: 0.07478674239102576,
    34: 0.06735667592832152,
    35: 0.05916656230115619,
    36: 0.046898637006940004,
    37: 0.0398135933887908,
    38: 0.030154684429826304,
    39: 0.0227276979362053,
    40: 0.015583565201711341,
    41: 0.010818005295249336,
    42: 0.007535077361319142,
    43: 0.004881074100956407,
    44: 0.0025466658751533877,
    45: 0.0015014269738305359,
    46: 0.00118720166519388,
    47: 0.0005843715634940675,
    48: 0.0002711420188867829,
    49: 0.0001565854384135422
                }


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
    

def create_pop(lengde):
    # Definer aldersintervaller og tilhørende sannsynligheter
    alder_intervaller = [
        (0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29),
        (30, 34), (35, 39), (40, 44), (45, 49), (50, 54), (55, 59),
        (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89),
        (90, 94), (95, 99), (100, 104)
    ]
    
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

def dodsfall(df, dodsrate):
    antall_dode = int(len(df) * dodsrate)
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
    

def populasjonsutvikling(df, TFR, år_start, år_slutt, yngste_fodsel, eldste_fodsel, innvandring=True,  innvandringsgrad=0.95):
    print(f"Regner populasjon med\nTFR={TFR}\nYngste fødsel: {yngste_fodsel}\nEldste fødsel: {eldste_fødsel}\n{år} år")
    
    liste_med_antall_personer = []

    # Setter ASFT for de ulike aldersgruppene
    asfr_sum = (TFR) * 1000
    asfr = pd.DataFrame(list(asfr_norm_avg.items()), columns=['alder', 'asfr_norm'])
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
        df['aldersgruppe'] = df['alder'].apply(get_age_group)
        # Disse vektene setter sannsynlighet for død
        df['vekter'] = df['aldersgruppe'].map(age_groups)
        
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

        innvandrere_df = create_pop(innvandrere)
        
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
        
        dode_index = dodsfall(df, dodsrate)        
        df = df.drop(dode_index)

        df = pd.concat([df, nye_kids, innvandrere_df]).reset_index(drop=True)
        df.drop(columns=['vekter'], inplace=True)

        df_antall = df.groupby(["alder", "sex"]).barn.count().sort_index().reset_index().rename(columns={"barn":f"pop_{2024+year}"})#
        befolkningsfordeling = befolkningsfordeling.merge(df_antall, on = ["alder", "sex"], how="left")
        
        liste_med_antall_personer.append(len(df))
        print(f"Antall fødte: {len(nye_kids)}. Dødsrate: {dodsrate}. Antall døde: {len(dode_index)}. Befolkning: {len(df)}")
        
        
    return liste_med_antall_personer, befolkningsfordeling, df

befolkning_for_2023 = pd.read_csv("befolkning.csv")#.loc[lambda x: x.år <= 2022]

# Dette er en startspopoulasjon basert på data fra ssb.
start_pop = pd.read_csv("startpop_no.csv")
start_pop

# Demonstrasjon av Norge
år_start = 2023
år = 100
år_slutt = år_start + år
yngste_fodsel = 15
eldste_fødsel = 49
befolkningsutvikling = pd.DataFrame()
befolkningsutvikling["år"] = range(år_start, år_slutt+1)
tfrs = [1.5]
# befolkningsutvikling

for tfr in tfrs:
    df_for_run = start_pop.copy()
    utv = [len(start_pop)]
    utvikling, pop_fordeling, df = populasjonsutvikling(df_for_run, tfr, år, yngste_fodsel, eldste_fødsel)
    pop_fordeling.to_csv(data / f"popfordeling_{år_start}-{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", index=False)
    df.to_csv(data / f"populasjon_{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", index=False)
    utv.extend(utvikling)
    befolkningsutvikling[f"pop_{tfr}"] = pd.Series(utv)
    
befolkningsutvikling.to_csv(data / f"befolkningsutvikling_{år_start}_{år_slutt}_{'-'.join([str(tfr).replace('.', '_') for tfr in tfrs])}.csv")


# Demonstrasjon av Norge
år_start = 2023
år = 10
år_slutt = år_start + år
yngste_fodsel = 15
eldste_fødsel = 49
befolkningsutvikling = pd.DataFrame()
befolkningsutvikling["år"] = range(år_start, år_slutt+1)
tfrs = [1.5]
# befolkningsutvikling


df_for_run = start_pop.copy()
befolkning_ferdig = pd.DataFrame()
delta = 20
for curr_run in range(0,100,delta):
    år_start = 2023 + curr_run
    år_slutt = år_start +  delta
    befolkningsutvikling = pd.DataFrame()
    befolkningsutvikling["år"] = range(år_start, år_slutt+1)
    utv = [len(start_pop)]
    utvikling, pop_fordeling, df = populasjonsutvikling(df_for_run, tfr, curr_run, (curr_run + 10) , yngste_fodsel, eldste_fødsel)
    pop_fordeling.to_csv(data / f"popfordeling_{år_start}-{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", index=False)
    df.to_csv(data / f"populasjon_{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", index=False)

    befolkningsutvikling[f"pop_{tfr}"] = pd.Series(utv)
    befolkning_ferdig = pd.concat([befolkning_ferdig, befolkningsutvikling])
    df_for_run = df
    
befolkning_ferdig.to_csv(data / f"befolkningsutvikling_{år_start}_{år_slutt}_{'-'.join([str(tfr).replace('.', '_') for tfr in tfrs])}_v2.csv")

files = [file for file in os.listdir("Data") if file.startswith("populasjon") and file.endswith("1_5.csv")]
files.sort()
files

pd.read_csv('Data/populasjon_2043_tfr1_5.csv')

delta = 20
tfr = 2.1
yngste_fodsel = 15
eldste_fødsel = 49
befolkningsutvikling = pd.DataFrame()
befolkningsutvikling["år"] = range(år_start, år_slutt+1)
befolkning_ferdig = pd.DataFrame()

for år in [2043, 2063, 2083]:
    df_for_run = pd.read_csv(f'Data/populasjon_{år}_tfr1_5.csv')
    år_start = år
    år_slutt = 2140
    befolkningsutvikling = pd.DataFrame()
    befolkningsutvikling["år"] = range(år_start, år_slutt+1)
    utv = [len(start_pop)]
    utvikling, pop_fordeling, df = populasjonsutvikling(df_for_run, tfr, år, år_slutt , yngste_fodsel, eldste_fødsel, innvandring=False)
    pop_fordeling.to_csv(data / f"popfordeling_{år_start}-{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", index=False)
    df.to_csv(data / f"populasjon_{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", index=False)
    pd.Series(utvikling).to_csv(data / f"utvikling_{år}.csv", index=False)
   # utv.extend(utvikling)
  #  befolkningsutvikling[f"pop_{år}_{trf}"] = pd.Series(utv)
    
    
#befolkning_ferdig.to_csv(data / f"befolkningsutvikling_{år_start}_{år_slutt}_{tfr}_v3.csv")