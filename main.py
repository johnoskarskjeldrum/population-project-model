
import pandas as pd
import argparse
from pathlib import Path

from population_model.data_manager import load_config, load_population, save_population
from population_model.model import run_simulation, load_child_distribution_data

def main():
    """
    Main function to run the population projection model.
    """
    # Load configuration
    config = load_config('config.yaml')
    data_path = Path('data')
    
    # Load child distribution data
    load_child_distribution_data(Path('.'))

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run population projection model.")
    parser.add_argument('--test', action='store_true', help='Use test population data for a faster run.')
    parser.add_argument('--start-year', type=int, default=2023, help='Start year of the simulation (default: 2023)')
    parser.add_argument('--years', type=int, default=100, help='Number of years to simulate (default: 100)')
    parser.add_argument('--min-fertility-age', type=int, default=15, help='Minimum age for fertility (default: 15)')
    parser.add_argument('--max-fertility-age', type=int, default=49, help='Maximum age for fertility (default: 49)')
    parser.add_argument('--tfrs', type=float, nargs='+', default=[1.5], help='List of Total Fertility Rates to simulate (default: 1.5)')
    parser.add_argument('--file', default='startpop_no.csv', help='startpopulation to run')
    parser.add_argument('--start-tfr', type=float, help='The TFR of the input file (for smooth transitions).')
    parser.add_argument('--fade-years', type=int, default=0, help='Number of years to transition from start-tfr to target-tfr.')
    args = parser.parse_args()

    # Load initial population
    use_test_population = args.test
    if use_test_population:
        pop_file = data_path / 'startpop_no_test.csv'
    else:
        pop_file = data_path / args.file
    
    print(f"Loading population from: {pop_file.absolute()}")
    start_pop = load_population(pop_file)
    
    # Ensure alder and barn are integers (sometimes loaded as floats from previously saved files)
    start_pop['alder'] = start_pop['alder'].astype(int)
    start_pop['barn'] = start_pop['barn'].astype(int)

    # Set simulation parameters
    år_start = args.start_year
    år = args.years
    år_slutt = år_start + år
    yngste_fodsel = args.min_fertility_age
    eldste_fødsel = args.max_fertility_age
    tfrs = args.tfrs

    # Determine filename prefix
    filename_prefix = "test_" if use_test_population else ""

    # Run simulation for each TFR
    for tfr in tfrs:
        df_for_run = start_pop.copy()
        utv = [len(start_pop)]
        utvikling, pop_fordeling, df = run_simulation(
            df_for_run, config, tfr, år_start, år_slutt, yngste_fodsel, eldste_fødsel, 
            innvandring=False, start_tfr=args.start_tfr, fade_years=args.fade_years
        )
        
        # Save results
        pop_fordeling.to_csv(
            data_path / f"{filename_prefix}popfordeling_{år_start}-{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", 
            index=False
        )
        df.to_csv(
            data_path / f"{filename_prefix}populasjon_{år_slutt}_tfr{str(tfr).replace('.','_')}.csv", 
            index=False
        )
        utv.extend(utvikling)
        befolkningsutvikling = pd.DataFrame({
            'år': range(år_start, år_slutt + 1),
            f'pop_{tfr}': utv
        })
        befolkningsutvikling.to_csv(
            data_path / f"{filename_prefix}befolkningsutvikling_{år_start}_{år_slutt}_{'-'.join([str(tfr).replace('.', '_') for tfr in tfrs])}.csv",
            index=False
        )

if __name__ == '__main__':
    main()
