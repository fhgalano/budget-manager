"""
Common Definitions required throughout the project that do not need
to be hidden in the .env file
"""
from pathlib import Path


# Root Directory
ROOT_DIR = Path(__file__).parent

# References
SYMBOLS = ['*', '#', '%', '(', ')', '-', '=', '"', '.', '/', "'"]
SELLER_NAME_MAP = {
    'nintendo': 'NINTENDO',
    'ebay': 'EBAY',
    'patreon': 'PATREON',
    'youtube': 'YOUTUBE',
    'vrv': 'VRV',
    'doist': 'TODOIST'
}
POINT_OF_SALE = ['tst', 'sq', 'paypal']

CYCLE_DATE = 24

# Test Variables
TEST_RESOURCE_DIR = ROOT_DIR / 'tests/resources'

# Constants
EXPECTED_COST_TOLERANCE = 0.2

# Locations
PROCESSED_FILE_DIR = ROOT_DIR / 'transactions/'
