#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random, logging, markdown, vertexai, requests,os

from flask import Flask, render_template, request, session, url_for, redirect
from google.auth import default
from vertexai.generative_models import GenerationConfig, GenerativeModel
from utils.json_utils import load_json_file
from config.environment import load_env_parameters
from config.firestore import init_firestore, filter_request
from config.mailgun import load_mailgun_parameters
from config.flask import configure_flask_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get project ID, region and secret_key from environment variables
project_id, region, user_collection_name, retro_collection_name, firestore_emulator_host = load_env_parameters()

# Get mailgun parameters 
MAILGUN_USERNAME, MAILGUN_SERVER, MAILGUN_DOMAIN, MAILGUN_API_KEY = load_mailgun_parameters()

# Initialize Firestore client

db = init_firestore(project_id,firestore_emulator_host)

# Configure Flask
app = Flask(__name__)

configure_flask_app(app)

# Use the key to authenticate
credentials, project_id = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])

# Initialize Vertex AI client
vertexai.init(project=project_id, location=region)
model = GenerativeModel("gemini-1.5-pro")
generation_config = GenerationConfig(
    temperature=0.9,
    top_p=1.0,
    top_k=32,
    candidate_count=1,
    max_output_tokens=8192,
)

load_mailgun_parameters()

# Load anecdotes from JSON file 
def load_anecdotes():
    #Load anecdotes from JSON file and return them.
    dict_anecdotes = load_json_file('anecdotes.json')
    
    #Choose a random anecdote 
    anecdote = dict_anecdotes[random.choice(list(dict_anecdotes.keys()))]

    return anecdote

    


# Load options from JSON file 
def load_options():
    """Load options from JSON file and return them."""
    options = load_json_file('retro_options.json')
    return options



# Send email using Mailgun
def send_email(email, html_content):
    """Send an email to the specified email address with the given content."""
    try:
        # Construct the Mailgun API request
        request_url = f"{MAILGUN_SERVER}/v3/{MAILGUN_DOMAIN}/messages"
        request_data = {
            "from": f"ZenikAI <noreply@{MAILGUN_DOMAIN}>",
            "to": email,
            "subject": "Votre rétrospective ZenikAI, le Cookeo à Rétro",
            "html": html_content,
        }
        response = requests.post(
            request_url,
            auth=(MAILGUN_USERNAME, MAILGUN_API_KEY),
            data=request_data,
        )

        if response.status_code == 200:
            logger.info(f"Email sent successfully to {email}")
        else:
            logger.error(f"Error sending email: {response.text}")

    except Exception as e:
        logger.error(f"Error sending email: {e}")

@app.route('/')
def index():
    """Render the index page."""
    options = load_options()
    
    anecdotes = load_anecdotes()

    
    logger.info("Route '/' accessed")

    # Access userChoices from the session
    userChoices = session.get('userChoices', {}) # Default to empty dict if not found

    # Convert attendees to an integer if it exists
    if  'attendees' in userChoices and userChoices['attendees'] is not None:
        userChoices['attendees'] = int(userChoices['attendees'])

    logger.info(f"User choices from cookie: {userChoices}")
    
    return render_template('index.html', options=options, userChoices=userChoices, anecdotes=anecdotes)

@app.route('/result.html', methods=['POST', 'GET'])
def result():
    """Handle form submission and generate content."""
    options = load_options()
    logger.info("Route '/result.html' accessed")

    # Check if the request is a GET (cancel button)
    if request.method == 'GET':
        # Reset session ID and userChoices
        session.pop('userChoices', None)  # Remove userChoices from session
        session.pop('_id', None)  # Remove session ID from session
        return redirect(url_for('index'))  # Redirect to the index page

    # Load prompt parts from file
    with open('config/prompt_parts.txt', 'r') as file:
        prompt_parts = file.readlines()

    # Reset userChoices before repopulating
    session['userChoices'] = {}  

    # Retrieve form datas
    duree = request.form.get('duree') or random.choice(options['durees'])
    type = request.form.get('type') or random.choice(options['types'])
    theme = request.form.get('theme') or random.choice(options['themes'])
    objective = request.form.get('objective', 'Générique')
    base = request.form.get('base') or random.choice(options['bases'])
    facilitation = request.form.get('facilitation') or random.choice(options['facilitations'])
    attendees = request.form.get('attendees')
    icebreaker = 'oui' if 'icebreaker' in request.form else 'non'
    distanciel = 'oui' if 'distanciel' in request.form else 'non' 


    session['userChoices'] = {
        "theme": theme, 
        "duree": duree, 
        "type": type, 
        "objective": objective, 
        "base": base, 
        "facilitation": facilitation, 
        "attendees": attendees, 
        "icebreaker": icebreaker, 
        "distanciel": distanciel
    }   

    logger.info(f"User choices: {session['userChoices']}")

    # Build the prompt including conditionnal options
    prompt_parts.extend([
        f"- [THEME]: {theme}",
        f"- [DUREE]: {duree}",
        f"- [TYPE]: {type}",
        f"- [ATELIER DE BASE]: {base}",
        f'- [FACILITATION]: {facilitation}',
        f"- [NOMBRE DE PARTICIPANTS]: {attendees}"
        f"- [DISTANCIEL]: {distanciel}"
    ])

    if objective:  # Add objective only if it's specified
        prompt_parts.append(f"- [BUT RECHERCHE]: {objective}")

    if icebreaker == "non":
        prompt_parts.append(f"Tu ne proposeras pas d'Ice Breaker")

    prompt = "\n".join(prompt_parts)  # Add all the part together

    try:
        logger.info(f"Generating content...")
        
        response = model.generate_content(
            prompt, 
            stream=False,
            generation_config=generation_config
        )
        
        logger.info(f"Received response from VertexAI")
        
        html_content = markdown.markdown(response.text)  # Convert Markdown to HTML
        session['html_content'] = html_content  # Store in session
        
    except Exception as e:
        logger.error(f"Error during content generation: {e}")
        return str(e)
    
    try:

        logger.info(f"Storing restrospective information in Firestore Database collection : {retro_collection_name}")
    
        # Store the plan data in Firestore
        retro_ref = db.collection(retro_collection_name).document()
        
        logger.info(f"Initialization of document in the Firestore Database: {retro_ref}")
        
        retro_ref.set({
            'theme': theme,
            'duree': duree,
            'type': type,
            'objective': objective,
            'base': base,
            'facilitation': facilitation,
            'attendees': attendees,
            'icebreaker': icebreaker,
            'distanciel': distanciel,
            'prompt': prompt,
            'result': response.text,
            'plan_id': retro_ref.id
        })

    except Exception as e:
        logger.error(f"Error during content storage: {e}")
        return str(e)

    return render_template('result.html', result=html_content, cancel_url=url_for('result'))

    
@app.route('/contact', methods=['POST'])
def contact():
    """Send email to the specified email address."""

    logger.info("Route '/contact' accessed")

    # Retrieve form datas
    firstname = request.form['firstname']  # Le prénom est requis, pas besoin de valeur par défaut
    lastname = request.form['lastname']  # Le nom est requis, pas besoin de valeur par défaut   
    company = request.form['company']  # L'entreprise est requis, pas besoin de valeur par défaut
    email = request.form['email']  # L'email est requis, pas besoin de valeur par défaut
    consent = True if 'consent' in request.form else False
    html_content = session.get('html_content')  # Retrieve from session

    logger.info(f"Sending email to {email}")
        
    send_email(email, render_template('mail.html', firstname=firstname, result=html_content))

    # Store user data in Firestore if user give his consent
    try:
        # request to db for checking if the email don't exist in db
        docs = filter_request(db=db,user_collection_name=user_collection_name,field='email',operator='==',value=email)
        
        # Get the email from docs
        user_email = [doc.to_dict()['email'] for doc in docs]

        
        # Store user data in Firestore if user give his consent and the email don't exist in db
        if consent == True and email not in user_email:

            logger.info(f"Storing user data in Firestore Database collection : {user_collection_name}")

            user_ref = db.collection(user_collection_name).document()

            logger.info(f"Initialization of document {user_ref.id} in the Firestore Database: {user_collection_name} ")

            user_ref.set({
                'firstname': firstname,
                'lastname': lastname,
                'company': company,
                'email': email,
                'user_id': user_ref.id
            })
            
        else: 
            logger.info(f"l'email {email} existe déjà dans la base de données car il a déjà été utilisé pour une autre retrospective")

    except Exception as e:
        logger.error(f"Error during content storage: {e}")
        return str(e)

    # Reset session ID and userChoices
    session.pop('userChoices', None)  # Remove userChoices from session
    session.pop('_id', None)  # Remove session ID from session

    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)