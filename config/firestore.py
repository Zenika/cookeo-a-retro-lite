from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1 import aggregation
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

def request_firestore(db, collection_name, limit=None, offset=None, perform_count=None, **filters):
    """
    Queries Firestore for documents based on the provided filter criteria.

    Args:
        db (google.cloud.firestore.Client): The Firestore client object.
        collection_name (str): The name of the Firestore collection to query.
        limit (int, optional): The maximum number of documents to retrieve. Defaults to 10.
        offset (int, optional): The number of documents to skip. Defaults to None.
        **filters: Variable keyword arguments for filtering. Each keyword should be a field name,
                   and the value should be a tuple of (operator, value) for the filter.

    Returns:
        google.cloud.firestore_v1.base_query.Query: A Firestore query object.
    """

    collection_ref = db.collection(collection_name)
    query_ref = collection_ref
    aggregate_query=None

    # Apply filters
    if filters:
        for field, (operator, value) in filters.items():
            query_ref = query_ref.where(filter=FieldFilter(field, operator, value))

    # Apply offset 
    if offset is not None:
        query_ref = query_ref.offset(offset)

    # Apply limit
    if limit is not None:
        query_ref = query_ref.limit(limit)

    if perform_count:
        # Perform the count aggregation
        aggregate_query = aggregation.AggregationQuery(query_ref).count().get()
        

    return query_ref.stream(), aggregate_query
