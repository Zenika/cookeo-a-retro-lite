from flask import Flask, render_template, request
import json, random

def load_options():
    """Charge et retourne les options disponibles depuis un fichier JSON."""
    with open('retro_options.json', 'r') as file:
        options = json.load(file)
    return options

app = Flask(__name__)

@app.route('/')
def index():
    options = load_options()
    return render_template('index.html', options=options)

@app.route('/submit', methods=['POST'])
def submit():
    options = load_options()

    duree = request.form.get('duree') or random.choice(options['durees'])
    type = request.form.get('type') or random.choice(options['types'])
    theme = request.form.get('theme') or random.choice(options['themes'])
    but = request.form.get('but', 'Générique')
    base = request.form.get('base') or random.choice(options['bases'])
    inspiration = request.form.get('inspiration') or random.choice(options['inspirations'])
    icebreaker = 'oui' if 'icebreaker' in request.form else 'non'
    distanciel = 'oui' if 'distanciel' in request.form else 'non'
    email = request.form['email']  # L'email est requis, pas besoin de valeur par défaut

    # Construire le prompt en incluant conditionnellement le but
    prompt_parts = [
        "Agis comme un Scrum Master expérimenté.",
        "Crée le plan d'un atelier de rétrospective au format Markdown.",
        "Voici les caractéristiques de cet atelier :",
        f"- Thème: {theme}",
        f"- Durée: {duree}",
        f"- Type: {type}",
        f"- Base: {base}",
        f'- Inspiration: {inspiration}',
        f"- Distanciel: {distanciel}"
    ]

    if but:  # Ajouter le but seulement s'il est renseigné
        prompt_parts.append(f"- But recherché: {but}")

    if icebreaker == "non":
        prompt_parts.append(f"Tu ne proposeras pas d'Ice Breaker")

    prompt = "\n".join(prompt_parts)  # Assembler toutes les parties en une seule chaîne
    
    return render_template('result.html', prompt=prompt)

if __name__ == '__main__':
    app.run(debug=True)