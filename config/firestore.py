from google.cloud import firestore
import os

def  init_firestore(project_id,firestore_emulator_host):
        """
    Initializes a Firestore client based on the environment.

    Args:
        project_id (str): The Google Cloud Project ID.
        firestore_emulator_host (str): The host address of the Firestore emulator if running in development mode.

    Returns:
        google.cloud.firestore.Client: A Firestore client object.
    """
        if os.getenv('FLASK_ENV') == 'development':
         db = firestore.Client(project=project_id, emulator_host=firestore_emulator_host)
        else:
         db = firestore.Client()

        return db