from os import getenv

from dotenv import load_dotenv

from definitions import ROOT_DIR


def get_database_path(database: str):
    env_path = ROOT_DIR / '.env'
    load_dotenv(env_path)
    return getenv(database)
