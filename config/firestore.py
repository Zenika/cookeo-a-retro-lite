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

def filter_request(db,collection_name,field=None,operator=None,value=None):
        """
    Queries Firestore for documents based on the provided filter criteria.

    Args:
        db (google.cloud.firestore.Client): The Firestore client object.
        collection_name (str): The name of the Firestore collection to query.
        field (str, optional): The field to filter on. Defaults to None, which queries all fields.
        operator (str, optional): The comparison operator to use. Defaults to None, which queries all fields.
        value (any, optional): The value to compare against. Defaults to None, which queries all fields.

    Returns:
        google.cloud.firestore_v1.base_query.Query: A Firestore query object.
    """
        collection_ref = db.collection(collection_name)

    # If no filter criteria are provided, return all documents
        if field is None or operator is None or value is None:
            return collection_ref.stream()

    # Otherwise, apply the filter criteria
        query_ref = collection_ref.where(filter=FieldFilter(field, operator, value))
        return query_ref.stream()