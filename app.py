from flask import Flask, render_template, request
import json, random
from google.cloud import aiplatform
import os
import logging
import markdown

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les options depuis le fichier JSON
def load_options():
    """Charge et retourne les options disponibles depuis un fichier JSON."""
    with open('retro_options.json', 'r') as file:
        options = json.load(file)
    return options

app = Flask(__name__)

# Get project ID and region from environment variables
project_id = os.environ.get('PROJECT_ID')
region = os.environ.get('REGION')

# Initialize Vertex AI client
import vertexai
vertexai.init(project=project_id, location=region)
from vertexai.generative_models import GenerationConfig, GenerativeModel, Image, Part
model = GenerativeModel("gemini-1.0-pro")
generation_config = GenerationConfig(
    temperature=0.9,
    top_p=1.0,
    top_k=32,
    candidate_count=1,
    max_output_tokens=8192,
)


@app.route('/')
def index():
    options = load_options()
    logger.info("Route '/' accessed")
    return render_template('index.html', options=options)

@app.route('/submit', methods=['POST'])
def submit():
    options = load_options()
    logger.info("Route '/submit' accessed")

    duree = request.form.get('duree') or random.choice(options['durees'])
    type = request.form.get('type') or random.choice(options['types'])
    theme = request.form.get('theme') or random.choice(options['themes'])
    but = request.form.get('but', 'Générique')
    base = request.form.get('base') or random.choice(options['bases'])
    inspiration = request.form.get('inspiration') or random.choice(options['inspirations'])
    icebreaker = 'oui' if 'icebreaker' in request.form else 'non'
    distanciel = 'oui' if 'distanciel' in request.form else 'non'
    firstname = request.form['firstname']  # Le prénom est requis, pas besoin de valeur par défaut
    lastname = request.form['lastname']  # Le nom est requis, pas besoin de valeur par défaut   
    company = request.form['company']  # L'entreprise est requis, pas besoin de valeur par défaut
    email = request.form['email']  # L'email est requis, pas besoin de valeur par défaut

    # Construire le prompt en incluant conditionnellement le but
    prompt_parts = [
        "Tu es un Scrum Master expérimenté et un Coach Agile expérimenté. Tu maîtrises la facilitation et l'animation d'atelier.",
        "Mon contexte est la création d'une rétrospective sur le thème [THEME] pour une équipe de développement agile de logiciel.",
        "Tu vas animer cette rétrospective agile sur le thème [THEME].",
        "Pour ça, voici les étapes à suivre :",
        "1. Préparer des activités et des questions de rétrospective en lien avec le thème.",
        "2. Créer un cadre accueillant pour la session (décorations, musiques, etc.).",
        "3. Faciliter les discussions pour identifier les points forts et les axes d'amélioration des itérations passées."
        "4. Encourager l'équipe à partager des anecdotes et des expériences positives liées au travail et au thème.",
        "5. Synthétiser les retours et définir des actions concrètes à mettre en œuvre pour les prochaines itérations.",
        "Voici les caractéristiques du résultat attendu :",
        "- Ambiance engageante.",
        "- Participation active de tous les membres de l'équipe.",
        "- Identification claire des points forts et des axes d'amélioration.",
        "- Actions concrètes définies pour les prochaines itérations.",
        "- Intégration d'éléments de [THEME] pour renforcer la cohésion de l'équipe.",
        "- Ne demande pas l'avis de l'utilisateur, c'est une demande one-shot",
        "- Format Markdown attendu",
        "Voici des caractéristiques pour la rétrospective :",
        f"- [THEME]: {theme}",
        f"- [DUREE]: {duree}",
        f"- [TYPE]: {type}",
        f"- [ATELIER DE BASE]: {base}",
        f'- [INSPIRATION]: {inspiration}',
        f"- [DISTANCIEL]: {distanciel}"
    ]

    if but:  # Ajouter le but seulement s'il est renseigné
        prompt_parts.append(f"- [BUT RECHERCHE]: {but}")

    if icebreaker == "non":
        prompt_parts.append(f"Tu ne proposeras pas d'Ice Breaker")

    prompt = "\n".join(prompt_parts)  # Assembler toutes les parties en une seule chaîne

    try:
        logger.info(f"Generating content with prompt: {prompt}")
        response = model.generate_content(
            prompt, 
            stream=False,
            generation_config=generation_config
        )
        logger.info(f"Received response: {response.text}")
        html_content = markdown.markdown(response.text)  # Convert Markdown to HTML
        logger.info(f"Convertion to HTML: {html_content}")
        return render_template('result.html', firstname=firstname, result=html_content)
        
    except Exception as e:
        logger.error(f"Error during content generation: {e}")
        return str(e)
    
if __name__ == '__main__':
    app.run(debug=True)