import os
from dotenv import load_dotenv

 
def load_env_file():
    """
    Loads environment variables from a .env file based on the FLASK_ENV setting.

    If FLASK_ENV is set to 'development', it loads variables from 'env/.env.local'.
    Otherwise, it loads variables from 'env/.env.prod'.
    """
    if os.getenv('FLASK_ENV') == 'development':
        load_dotenv('env/.env.local')
    else:
        load_dotenv('env/.env.prod')

def load_env_parameters():
        """
    Loads project ID, region, user collection name, retro collection name, and Firestore emulator host from environment variables.

    Returns:
        tuple: A tuple containing the project ID, region, user collection name, retro collection name, and Firestore emulator host.
    """
        load_env_file()
    
        project_id = os.environ.get('PROJECT_ID')
        region = os.environ.get('REGION')
        branch = os.environ.get('BRANCH_NAME', 'default')
        user_collection_name = f"{branch}-users"
        retro_collection_name = f"{branch}-retros"
        firestore_emulator_host = os.environ.get('FIRESTORE_EMULATOR_HOST')
    
        return project_id, region, user_collection_name, retro_collection_name, firestore_emulator_host

