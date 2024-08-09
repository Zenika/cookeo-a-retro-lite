from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
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

def filter_request(db,user_collection_name,field,operator,value):
    # request to db for checking if the email don't exist in db
    users_ref = db.collection(user_collection_name)
    query_ref = users_ref.where(filter=FieldFilter(field, operator, value)).limit(1)
    # Get the documents from the query
    docs = query_ref.stream()

    return docs