
import pandas as pd

def get_age_group(age, age_groups):
    """
    Returns the age group for a given age.
    """
    for group, (min_age, max_age) in age_groups.items():
        if min_age <= age <= max_age:
            return group
    return None
