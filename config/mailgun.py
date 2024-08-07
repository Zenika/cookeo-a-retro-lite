import os

def load_mailgun_parameters():
    """
    Loads Mailgun configuration parameters from environment variables.

    Returns:
        tuple: A tuple containing the Mailgun username, server, domain, and API key.
    """
    # Mailgun configuration
    MAILGUN_USERNAME = os.environ.get('MAILGUN_USERNAME')
    MAILGUN_SERVER = os.environ.get('MAILGUN_SERVER')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    if os.getenv('FLASK_ENV') == 'development':
        MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY_NOPROD')
    else:
        MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY_PROD')

    return MAILGUN_USERNAME, MAILGUN_SERVER, MAILGUN_DOMAIN, MAILGUN_API_KEY