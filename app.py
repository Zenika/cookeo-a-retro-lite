#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, random, os, logging, markdown, smtplib, vertexai

from flask import Flask, render_template, request
from google.cloud import aiplatform
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from vertexai.generative_models import GenerationConfig, GenerativeModel, Image, Part


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get project ID and region from environment variables
project_id = os.environ.get('PROJECT_ID')
region = os.environ.get('REGION')

# Initialize Vertex AI client
vertexai.init(project=project_id, location=region)
model = GenerativeModel("gemini-1.0-pro")
generation_config = GenerationConfig(
    temperature=0.9,
    top_p=1.0,
    top_k=32,
    candidate_count=1,
    max_output_tokens=8192,
)

# Email configuration
sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PASSWORD')

# Load prompt parts from file
with open('config/prompt_parts.txt', 'r') as file:
    prompt_parts = file.readlines()

# Load options from JSON file 
def load_options():
    """Load options from JSON file and return them."""
    with open('retro_options.json', 'r') as file:
        options = json.load(file)
    return options

# Send email
def send_email(email, html_content):
    """Send an email to the specified email address with the given content."""
    try:

        # Send email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Votre rétrospective ZeniCAI"
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        logger.info(f"Email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

@app.route('/')
def index():
    """Render the index page."""
    options = load_options()
    logger.info("Route '/' accessed")
    return render_template('index.html', options=options)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission and generate content."""
    options = load_options()
    logger.info("Route '/submit' accessed")

    # Retrieve form datas
    duree = request.form.get('duree') or random.choice(options['durees'])
    type = request.form.get('type') or random.choice(options['types'])
    theme = request.form.get('theme') or random.choice(options['themes'])
    objective = request.form.get('objective', 'Générique')
    base = request.form.get('base') or random.choice(options['bases'])
    inspiration = request.form.get('inspiration') or random.choice(options['inspirations'])
    icebreaker = 'oui' if 'icebreaker' in request.form else 'non'
    distanciel = 'oui' if 'distanciel' in request.form else 'non'
    firstname = request.form['firstname']  # Le prénom est requis, pas besoin de valeur par défaut
    lastname = request.form['lastname']  # Le nom est requis, pas besoin de valeur par défaut   
    company = request.form['company']  # L'entreprise est requis, pas besoin de valeur par défaut
    email = request.form['email']  # L'email est requis, pas besoin de valeur par défaut

    # Build the prompt including conditionnal options
    prompt_parts.extend([
        f"- [THEME]: {theme}",
        f"- [DUREE]: {duree}",
        f"- [TYPE]: {type}",
        f"- [ATELIER DE BASE]: {base}",
        f'- [INSPIRATION]: {inspiration}',
        f"- [DISTANCIEL]: {distanciel}"
    ])

    if objective:  # Add objective only if it's specified
        prompt_parts.append(f"- [BUT RECHERCHE]: {objective}")

    if icebreaker == "non":
        prompt_parts.append(f"Tu ne proposeras pas d'Ice Breaker")

    prompt = "\n".join(prompt_parts)  # Add all the part together

    try:
        logger.info(f"Generating content with prompt: {prompt}")
        
        response = model.generate_content(
            prompt, 
            stream=False,
            generation_config=generation_config
        )
        
        logger.info(f"Received response: {response.text}")
        
        html_content = markdown.markdown(response.text)  # Convert Markdown to HTML
        
        logger.info(f"Sending email to {email}")
        
        send_email(email, render_template('mail.html', firstname=firstname, result=html_content))
        
        return render_template('result.html', firstname=firstname, result=html_content)
        
    except Exception as e:
        logger.error(f"Error during content generation: {e}")
        return str(e)
    
if __name__ == '__main__':
    app.run(debug=True)