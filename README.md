# Le Cookeo à Rétro

## Description
Le Cookeo à Rétro est une application Flask qui permet aux utilisateurs de générer des plans personnalisés pour des ateliers de rétrospective. Elle utilise l'API GPT-4 d'OpenAI pour créer des suggestions dynamiques basées sur les entrées des utilisateurs.

## Fonctionnalités
- Génération de plans de rétrospective personnalisés.
- Interface utilisateur responsive avec Materialize CSS.
- Intégration avec l'API GPT-4 pour des suggestions de contenu enrichi.
- Personnalisation avancée avec options supplémentaires révélées dynamiquement.

## Prérequis
- Python 3.8+
- Flask
- OpenAI API Key

## Installation

### Cloner le dépôt

```bash
git clone https://votre-repository/votre-projet.git
cd votre-projet
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Configurer les variables d'environnement

Créez un fichier .env à la racine du projet et ajoutez votre clé API d'OpenAI :

```
OPENAI_API_KEY='votre-clé-api'
```

### Usage

#### Lancer l'application

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Ouvrez votre navigateur et accédez à http://127.0.0.1:5000/ pour utiliser l'application.

### Développement

#### Structure du projet

- `app.py`: Le point d'entrée de l'application Flask.
- `/templates`: Dossiers contenant les fichiers HTML pour les templates.
- `/static`: Contient les fichiers CSS et JavaScript.

#### Ajouter de nouvelles fonctionnalités

Pour ajouter de nouvelles fonctionnalités, vous pouvez modifier app.py et les templates associés. Assurez-vous de suivre les bonnes pratiques de développement Flask et de documenter vos changements.

### Contribution

Les contributions sont les bienvenues. Veuillez ouvrir une issue pour discuter de ce que vous aimeriez changer ou soumettre directement une pull request.

### Licence

MIT