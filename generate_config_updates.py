
import yaml
import numpy as np
from pathlib import Path

def generate_realistic_death_rates():
    """
    Generates a more realistic set of death rates that increase sharply for older age groups.
    This function uses a logistic growth curve to model mortality, which is a common
    approach in demography.
    """
    age_groups = {
        '0-4': [0, 4], '5-9': [5, 9], '10-14': [10, 14], '15-19': [15, 19],
        '20-24': [20, 24], '25-29': [25, 29], '30-34': [30, 34], '35-39': [35, 39],
        '40-44': [40, 44], '45-49': [45, 49], '50-54': [50, 54], '55-59': [55, 59],
        '60-64': [60, 64], '65-69': [65, 69], '70-74': [70, 74], '75-79': [75, 79],
        '80-84': [80, 84], '85-89': [85, 89], '90-94': [90, 94], '95-99': [95, 99],
        '100+': [100, 120]
    }
    
    death_rates = {}
    
    # Parameters for the logistic function
    # These are chosen to create a curve that starts low, rises steeply around age 80,
    # and approaches 1 (or a high value) for the oldest ages.
    L = 1.0  # Maximum mortality rate
    k = 0.15 # Steepness of the curve
    x0 = 85  # Midpoint of the curve (age at which mortality is increasing fastest)

    for group, (min_age, max_age) in age_groups.items():
        mid_age = (min_age + max_age) / 2
        
        # Use a logistic function for ages above 60
        if mid_age > 60:
            rate = L / (1 + np.exp(-k * (mid_age - x0)))
        else:
            # For younger ages, use a simpler, low mortality rate
            # (can be replaced with more detailed data if available)
            base_rates = {
                '0-4': 0.0013, '5-9': 0.0005, '10-14': 0.0004, '15-19': 0.0008,
                '20-24': 0.001, '25-29': 0.0012, '30-34': 0.0015, '35-39': 0.002,
                '40-44': 0.003, '45-49': 0.005, '50-54': 0.008, '55-59': 0.012,
                '60-64': 0.02
            }
            rate = base_rates.get(group, 0.001)
            
        death_rates[group] = round(float(rate), 4)

    return death_rates

def update_config_with_new_rates(config_path, new_rates):
    """
    Loads the YAML config, updates the death_rates, and saves it back.
    """
    config_path = Path(config_path)
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    config['death_rates'] = new_rates
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    
    print(f"Successfully updated death rates in {config_path}")
    print("New death rates:")
    for group, rate in new_rates.items():
        print(f"  {group}: {rate}")

if __name__ == '__main__':
    config_file = 'config.yaml'
    realistic_rates = generate_realistic_death_rates()
    update_config_with_new_rates(config_file, realistic_rates)
