import os
from django.conf import settings

def states_processor(request):
    """
    This function makes a list of all state names available to all templates.
    """
    states_path = os.path.join(settings.DATA_DIR, 'states')
    all_states = []
    try:
        # Get all filenames from the data/states/ directory
        filenames = os.listdir(states_path)
        # Clean up the names by removing '.csv'
        all_states = sorted([name.replace('.csv', '') for name in filenames if name.endswith('.csv')])
    except FileNotFoundError:
        # If the directory doesn't exist, just return an empty list
        all_states = []
        
    return {'all_states': all_states}