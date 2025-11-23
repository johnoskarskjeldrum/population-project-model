import pandas as pd
import glob

def analyze():
    # Find the files
    pop_files = ["data/popfordeling_2023-2123_tfr1_5.csv"]
    utv_files = ["data/test_befolkningsutvikling_2023_2123_1_5.csv"]
    
    if not pop_files or not utv_files:
        print("Files not found.")
        return

    pop_file = pop_files[0]
    utv_file = utv_files[0]
    
    print(f"Analyzing {pop_file} and {utv_file}")
    
    df_pop = pd.read_csv(pop_file)
    df_utv = pd.read_csv(utv_file)
    
    # Sum popfordeling columns (excluding sex, alder)
    pop_sums = {}
    for col in df_pop.columns:
        if col.startswith("pop_"):
            year = int(col.split("_")[1])
            pop_sums[year] = df_pop[col].sum()
            
    # Get utv values
    # utv file has 'år' and 'pop_1.5' (or similar)
    utv_sums = {}
    pop_col = [c for c in df_utv.columns if c.startswith("pop_")][0]
    for _, row in df_utv.iterrows():
        utv_sums[row['år']] = row[pop_col]
        
    print(f"{'Year':<6} {'PopFordeling':<15} {'Utvikling':<15} {'Diff':<10}")
    for year in sorted(pop_sums.keys()):
        p_sum = pop_sums.get(year, 0)
        u_sum = utv_sums.get(year, 0)
        print(f"{year:<6} {p_sum:<15} {u_sum:<15} {p_sum - u_sum:<10}")
        
    # Check for duplicates in popfordeling
    print("\nChecking for duplicates in popfordeling keys (alder, sex):")
    duplicates = df_pop.duplicated(subset=['alder', 'sex'])
    if duplicates.any():
        print(f"Found {duplicates.sum()} duplicate rows in popfordeling!")
        print(df_pop[duplicates].head())
    else:
        print("No duplicates found in popfordeling keys.")

if __name__ == "__main__":
    analyze()
