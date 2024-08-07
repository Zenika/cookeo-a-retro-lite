from flask import Flask
import os

# Configure Flask
def configure_flask_app(app):
    
# Configure Flask
    app.config['SESSION_COOKIE_NAME'] = 'cookeo_session_id'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # Get from environment variable
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'txt'}

# TODO Seems to be not used
def allowed_file(filename,app):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']