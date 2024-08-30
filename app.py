#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random, logging, markdown, vertexai, requests,os

from flask import Flask, render_template, request, session, url_for, redirect, make_response, flash, g
from google.auth import default
from vertexai.generative_models import GenerationConfig, GenerativeModel
from utils.json_utils import load_json_file
from config.environment import load_env_parameters
from config.firestore import init_firestore, request_firestore
from config.mailgun import load_mailgun_parameters
from config.flask import configure_flask_app
import re, json

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

def get_retro_content(plan_id):
    """Retrieves retrospective content from Firestore based on plan_id.

    Args:
        plan_id: The ID of the retrospective plan.

    Returns:
        A tuple containing:
            - retro_data: A dictionary containing the retrospective data, or None if not found.
            - error_message: An error message if retrieval fails, otherwise None.
    """
    try:
        retro_ref = db.collection(retro_collection_name).document(plan_id).get()

        if retro_ref.exists:
            retro_data = retro_ref.to_dict()
            return retro_data, None
        else:
            return None, f"Plan with ID {plan_id} not found in Firestore."
    except Exception as e:
        logger.error(f"Error retrieving plan from Firestore: {e}")
        return None, f"Error retrieving plan from Firestore: {e}"
    
@app.teardown_appcontext
def close_connection(exception):
    """Supprime les données de la rétrospective à la fin de la requête."""
    retrospective = getattr(g, 'retrospective', None)
    if retrospective is not None:
        del g.retrospective

@app.route('/')
def index():
    """Render the index page."""
    options = load_options()
    anecdotes = load_anecdotes()
    logger.info("Route '/' accessed")

    # Vérifier si un plan_id est passé en paramètre d'URL
    plan_id = request.args.get('plan_id')
    g.retrospective = None # Initialiser pour la requête

    userChoices = {}  # Initialiser userChoices comme un dictionnaire vide

    if plan_id:
        # Récupérer les données du plan depuis Firestore
        retrospective = getattr(g, 'retrospective', None)

        if retrospective is None:
            retrospective, error_message = get_retro_content(plan_id)
            if retrospective is None:
                flash(f"Erreur : Plan non trouvé (ID : {plan_id})", "error")
                # Rediriger vers la page d'accueil sans plan_id
                return redirect(url_for('index')) 
            g.retrospective = retrospective

        userChoices = {
            "theme": retrospective.get('theme'),
            "duree": retrospective.get('duree'),
            "type": retrospective.get('type'),
            "objective": retrospective.get('objective'),
            "base": retrospective.get('base'),
            "facilitation": retrospective.get('facilitation'),
            "attendees": retrospective.get('attendees'),
            "icebreaker": retrospective.get('icebreaker'),
            "distanciel": retrospective.get('distanciel')
        }
    else:
        # Aucun plan_id fourni, réinitialiser userChoices
        userChoices = {}

    # Convert attendees to an integer if it exists
    if  'attendees' in userChoices and userChoices['attendees'] is not None:
        userChoices['attendees'] = int(userChoices['attendees'])

    logger.info(f"User choices from cookie: {userChoices}")
    
    return render_template('index.html', options=options, userChoices=userChoices, anecdotes=anecdotes)

@app.route('/generate_retro', methods=['POST'])
def generate_retro():
    """Handle form submission and generate content."""
    options = load_options()
    logger.info("Route '/generate_retro' accessed")

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
    base = request.form.get('base') or random.choice(options['bases'])
    facilitation = request.form.get('facilitation') or random.choice(options['facilitations'])
    attendees = request.form.get('attendees')
    icebreaker = request.form.get('icebreaker')
    distanciel = request.form.get('distanciel') 

    # Fix for objective:
    objective = request.form.get('objective')
    if not objective:  # Check if objective is None or an empty string
        objective = 'Générique'

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
        f"- [NOMBRE DE PARTICIPANTS]: {attendees}",
        f"- [BUT RECHERCHE]: {objective}"
    ])

    # if objective:  # Add objective only if it's specified
    #    prompt_parts.append(f"- [BUT RECHERCHE]: {objective}")

    if icebreaker==None:
        prompt_parts.append(f"Tu ne proposeras pas d'Ice Breaker")

    if distanciel=='on':
        prompt_parts.append(f"La rétrospective sera animée à distance sur un outils de tableau blanc numérique.")
    else:
        prompt_parts.append(f"La rétrospective sera animée en présentiel à l'aide d'un tableau blanc physique, de feutres, post-it, etc.")

    prompt = "\n".join(prompt_parts)  # Add all the part together

    def generate_content_vertex(prompt=prompt,generation_config=generation_config,model=model):
        logger.info(f"Generating content...")
        response = model.generate_content(
                prompt, 
                stream=False,
                generation_config=generation_config)
        
        return response

    try:
        
        # Generate content using Vertex AI

        response = generate_content_vertex(
            prompt,
            generation_config,model=model
    )
        logger.info(f"Received response from VertexAI")
        
        # html_content = markdown.markdown(response.text)  # Convert Markdown to HTML
        # session['html_content'] = html_content  # Store in session
        
    except Exception as e:
        logger.error(f"Error during content generation: {e}")
        return str(e)
    
    try:

        logger.info(f"Storing restrospective information in Firestore Database collection : {retro_collection_name}")
    
        # Store the plan data in Firestore
        retro_ref = db.collection(retro_collection_name).document()
        
        logger.info(f"Initialization of document {retro_ref.id} in the Firestore Database: {retro_collection_name} ")

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

        plan_id = retro_ref.id

    except Exception as e:
        logger.error(f"Error during content storage: {e}")
        return str(e)
    
    return redirect(url_for('result', plan_id = plan_id))

@app.route('/result/<plan_id>')
def result(plan_id):
    """Display the result page for the specified plan"""
    logger.info(f"Route '/result/{plan_id}' accessed")

    retrospective = getattr(g, 'retrospective', None)
    
    if retrospective is None:
    
        retrospective, error_message = get_retro_content(plan_id)
    
        if not retrospective:
            return render_template(
                'retro_not_found.html',
                error=error_message,
                cancel_url=url_for('clear_and_redirect')
            ), 404

        html_content = markdown.markdown(retrospective['result'])
    
        return render_template(
            'result.html', 
            result=html_content, 
            plan_id=plan_id, 
            cancel_url=url_for('clear_and_redirect')
        )

@app.route('/clear_and_redirect')
def clear_and_redirect():
    """Clear session and redirect to the index"""
    logger.info("Route '/clear_and_redirect' accessed")
    logger.info("Clearing session and redirecting to the index")

    # Reset session ID and userChoices
    session.pop('userChoices', None)  # Remove userChoices from session
    session.pop('_id', None)  # Remove session ID from session

    # Create a response object
    response = make_response(redirect(url_for('index')))

    # Delete the cookies
    response.delete_cookie('session')
    response.delete_cookie('cookie_session_id')

    return response

@app.route('/contact/<plan_id>', methods=['POST'])
def contact(plan_id):
    """Send email to the specified email address."""

    logger.info("Route '/contact' accessed")

    # Retrieve form datas
    firstname = request.form['firstname']  # Le prénom est requis, pas besoin de valeur par défaut
    lastname = request.form['lastname']  # Le nom est requis, pas besoin de valeur par défaut   
    company = request.form['company']  # L'entreprise est requis, pas besoin de valeur par défaut
    email = request.form['email']  # L'email est requis, pas besoin de valeur par défaut
    consent = True if 'consent' in request.form else False

    retrospective = getattr(g, 'retrospective', None)
    if retrospective is None:
        retrospective, error_message = get_retro_content(plan_id)

    html_content = markdown.markdown(retrospective['result'])
    
    logger.info(f"Sending email to {email}")
        
    send_email(
        email, 
        render_template(
            'mail.html', 
            firstname=firstname, 
            result=html_content
        )
    )

    # Store user data in Firestore if user give his consent
    try:
        # request to db for checking if the email don't exist in db
        docs = request_firestore(db,collection_name=user_collection_name,field='email',operator='==',value=email,limit=1)
        
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
            
        elif consent == True and email in user_email: 
            logger.info(f"208 : the email {email} already exists in the database because it has already been used for another retrospective")
        else:
             logger.info(f"204 : the user has not given his consent")   

    except Exception as e:
        logger.error(f"Error during content storage: {e}")
        return str(e)

    # Reset session ID and userChoices
    # session.pop('userChoices', None)  # Remove userChoices from session
    # session.pop('_id', None)  # Remove session ID from session

    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    """Render the thank you page."""
    logger.info("Route '/thank-you' accessed")

    return render_template('thank_you.html', cancel_url=url_for('clear_and_redirect'))

@app.route('/retro_history')
def view_retro_history():
    logger.info("Route '/retro_history' accessed")

    retros = request_firestore(db=db,collection_name=retro_collection_name,limit=10)

    retrospectives = []

    # Get the list of retros
    for doc in retros:
            retro_data = doc.to_dict()
            retrospectives.append({
            "title": retro_data.get('result').split('\n', 1)[0][2:],  
            "theme": retro_data.get('theme'),
            "duration": retro_data.get('duree'),
            "attendees": retro_data.get('attendees'),
            "plan_id": retro_data.get('plan_id'),
            "distanciel": retro_data.get('distanciel'),
            "icebreaker": retro_data.get('icebreaker')})

    return render_template('retro_history.html', json_retrospectives=retrospectives)

if __name__ == '__main__':
    app.run(debug=True)