
import pandas as pd
from pathlib import Path

def create_representative_sample(full_pop_path, sample_pop_path, sample_fraction=0.01, random_state=42):
    """
    Creates a smaller, representative sample of a population using stratified sampling.

    Args:
        full_pop_path (Path): Path to the full population CSV file.
        sample_pop_path (Path): Path to save the sampled population CSV file.
        sample_fraction (float): The fraction of the population to sample (e.g., 0.01 for 1%).
        random_state (int): Seed for the random number generator for reproducibility.
    """
    print(f"Loading full population from {full_pop_path}...")
    try:
        df = pd.read_csv(full_pop_path)
    except FileNotFoundError:
        print(f"Error: The file {full_pop_path} was not found.")
        return

    print(f"Original population size: {len(df)}")
    print("Creating a representative sample using stratified sampling on 'alder' and 'sex'...")

    # Perform stratified sampling
    # The groupby operation ensures that the sample is drawn proportionally from each age-sex group.
    sample_df = df.groupby(['alder', 'sex'], group_keys=False).apply(
        lambda x: x.sample(frac=sample_fraction, random_state=random_state)
    )

    print(f"New sample population size: {len(sample_df)}")

    # Save the new sample population
    sample_df.to_csv(sample_pop_path, index=False)
    print(f"Successfully saved test population to {sample_pop_path}")

if __name__ == '__main__':
    data_dir = Path('data')
    full_population_file = data_dir / 'startpop_no.csv'
    test_population_file = data_dir / 'startpop_no_test.csv'
    
    # Create a sample that is 1% of the original population size
    create_representative_sample(full_population_file, test_population_file, sample_fraction=0.01)
