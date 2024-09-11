# Le Cookeo à Rétro

## Description

Le Cookeo à Rétro est une application Flask qui permet aux utilisateurs de générer des plans personnalisés pour des ateliers de rétrospective. Elle utilise l'API de Vertex AI, le [modèle Gemini 1.5 Pro](https://ai.google.dev/gemini-api/docs/models/gemini?hl=fr#gemini-1.5-pro) pour créer des suggestions dynamiques basées sur les entrées des utilisateurs.

## Fonctionnalités
- Génération de plans de rétrospective personnalisés.
- Interface utilisateur responsive avec Materialize CSS.
- Intégration avec l'API Vertex AI pour des suggestions de contenu enrichi.
- Personnalisation avancée avec options supplémentaires révélées dynamiquement.

## Prérequis
- Python 3.8+
- Flask
- Google cloud Project ID

## A propos du prompt

### Paramétrage du prompt

- Temperature : 0.9
- Top_p : 1.0
- Top_k : 16
- Candidate_count : 1
- Max_output_tokens : 8192

### Définition du prompt

La définition du prompt est lisible [ici](config/prompt_parts.txt)

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

#### Installation de Java >= 8 pour l'emulateur google-cloud-firestore

Téléchargez et installez la dernière version de Java 8 ou supérieure à partir du site Web d'Oracle : https://www.oracle.com/java/technologies/javase-downloads.html

##### Ajoutez le JRE à votre variable d'environnement PATH:

###### Windows:

- Ouvrez le menu Démarrer et recherchez "Variables d'environnement".
- Cliquez sur "Modifier les variables d'environnement système".
- Dans la section "Variables système", sélectionnez la variable PATH et cliquez sur "Modifier".
- Ajoutez le chemin d'accès au répertoire bin de votre installation Java à la fin de la valeur de la variable PATH. Par exemple, si votre installation Java est dans C:\Program Files\Java\jdk-11.0.16, vous devez ajouter - C:\Program Files\Java\jdk-11.0.16\bin à la variable PATH.
- Cliquez sur "OK" pour enregistrer les modifications.

###### macOS/Linux:

- Ouvrez votre terminal.
- Modifiez le fichier .bashrc ou .zshrc en fonction de votre shell.
- Ajoutez la ligne suivante au fichier, en remplaçant /path/to/java/bin par le chemin d'accès au répertoire bin de votre installation Java :

    ```sh
    export PATH=$PATH:/path/to/java/bin
    ```

- Enregistrez le fichier et fermez-le.
- Exécutez la commande source ~/.bashrc ou source ~/.zshrc pour appliquer les modifications.

### Configurer les variables d'environnement

Créez un fichier `.env.local` dans le répertoire `env/` avec les variables d'environnement suivantes :

```
PROJECT_ID
REGION
GAR_REPOSITORY
MAILGUN_USERNAME
MAILGUN_DOMAIN
MAILGUN_SERVER
MAILGUN_API_KEY_NOPROD
MAILGUN_API_KEY_PROD
SECRET_KEY
FIRESTORE_EMULATOR_HOST
IMAGE_NAME
SERVICE_NAME
```

Vous pouvez trouver les valeurs pour ces variables dans Secret Manager

## Usage

### Lancer l'application

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Ouvrez votre navigateur et accédez à http://127.0.0.1:5000/ pour utiliser l'application.

## Développement

### Structure du projet

- `app.py`: Le point d'entrée de l'application Flask.
- `/templates`: Dossiers contenant les fichiers HTML pour les templates.
- `/static`: Contient les fichiers CSS et JavaScript.

### Ajouter de nouvelles fonctionnalités

Pour ajouter de nouvelles fonctionnalités, vous pouvez modifier app.py et les templates associés. Assurez-vous de suivre les bonnes pratiques de développement Flask et de documenter vos changements.

### Démarrez l'émulateur Google-Cloud-Firestore

#### Mac OS/Linux

Lancez l'émulateur `google-cloud-firestore` avec la commande :

```sh
gcloud emulators firestore start --host-port=localhost:8080&
```

## Déploiement

### Automatique

#### Sous Mac OS X ou Linux

##### Déploiement

```bash
bash cicd/macosx_linux/build_push_deploy.sh
```

##### Nettoyage

```bash
bash cicd/macosx_linux/clean-env.sh
```

#### Sous Windows

##### Déploiement

```bash
bash deploy_branch.bat
```

### Manuel

#### Tester votre branche

##### Préparation

- Commencez par définir les variables pour builder et déployer votre conteneur en sourçant votre fichier `env/.env.local`

```sh
source env/.env.local
```

- Créez la variable `${BRANCH_NAME}` avec le nom de votre branche :

```sh
export BRANCH_NAME=$(git branch --show-current)
```

- Créer la variable `${SERVICE_NAME}` contenant le nom de votre service de test

```sh
export SERVICE_NAME=cookeo-a-retro-${BRANCH_NAME}
```

- Définissez la liste des secrets et la liste des variables d'environnement utilisées par le déploiement

```sh
export SECRETS=(
    "MAILGUN_USERNAME"
    "MAILGUN_DOMAIN"
    "MAILGUN_SERVER"
    "MAILGUN_API_KEY_NOPROD"
    "SECRET_KEY"
)
```

- Authentifiez-vous sur Google Artifact Repositories

```sh
gcloud auth print-access-token \
| docker login \
  -u oauth2accesstoken \
  --password-stdin https://${REGION}-docker.pkg.dev
```

##### Buildez votre conteneur

Pour builder votre conteneur de test, utilisez la commande :

```sh
docker build \
    -t ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest \
    . \
    --platform linux/amd64
```

##### Poussez votre conteneur dans la registry

Poussez votre image dans la registry :

```sh
docker push ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest
```

##### Déployez votre conteneur dans Cloud Run

```sh
gcloud run deploy ${SERVICE_NAME} \
  --region ${REGION} \
  --image ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest \
  --platform managed \
  --port 5000 \
  --set-secrets=$( \
        for secret_name in "${SECRETS[@]}"; do 
            secret_path=$(gcloud secrets versions access latest --project $PROJECT_ID --secret $secret_name --format='value(name)')
            echo "$secret_name=$secret_path" 
        done | paste -sd, - \
    ) \
--set-env-vars=REGION=${REGION},BRANCH_NAME=${BRANCH_NAME} \
--allow-unauthenticated
```

##### Nettoyez la registry et cloud run après vos tests

Afin de ne pas trop consommer de ressources GCP, il est nécessaire de nettoyer les artefacts de sa branches une fois les tests effectués

```sh
gcloud run services delete ${SERVICE_NAME} --region ${REGION}
gcloud artifacts docker images delete ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}
```

###### Suppression des collections Firestore

Supprimez les collections firestore créées temporairement dans la [console Firestore](https://console.cloud.google.com/firestore/databases/-default-)

#### Déploiement en production

##### Préparation

- Assurez-vous d'être sur la branche principale et d'avoir récupérer les dernières modifications

```sh
git checkout main
git pull -r
```

- Tagguez la version sur Git

```sh
export IMAGE_TAG=<votre-tag-au-format-X.Y.Z>
git tag -a v${IMAGE_TAG} -m "<Votre commentaire>"
git push push origin tag v${IMAGE_TAG}
```

- Créez la variable `${SERVICE_NAME}` contenant le nom du service `cookeo-a-retro`

```sh
export SERVICE_NAME=cookeo-a-retro
```

- Définissez la liste des secrets et la liste des variables d'environnement utilisées par le déploiement

```sh
export SECRETS=(
    "MAILGUN_USERNAME"
    "MAILGUN_DOMAIN"
    "MAILGUN_SERVER"
    "MAILGUN_API_KEY_PROD"
    "SECRET_KEY"
)
```

- Authentifiez-vous sur Google Artifact Repositories

```sh
gcloud auth print-access-token \
| docker login \
  -u oauth2accesstoken \
  --password-stdin https://${REGION}-docker.pkg.dev
```

##### Buildez le conteneur

Pour builder le conteneur, utilisez la commande :

```sh
docker build \
    -t ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG} \
    . \
    --platform linux/amd64
```

##### Poussez votre conteneur dans la registry

Poussez votre image dans la registry :

```sh
docker push ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}
```

##### Déployez votre conteneur dans Cloud Run

```sh
gcloud run deploy ${SERVICE_NAME} \
  --region ${REGION} \
  --image ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --port 5000 \
  --set-secrets=$( \
        for secret_name in "${SECRETS[@]}"; do 
            secret_path=$(gcloud secrets versions access latest --project $PROJECT_ID --secret $secret_name --format='value(name)') 
            echo "$secret_name=$secret_path" 
        done | paste -sd, - \
    ) \
--set-env-vars=REGION=${REGION} \
--allow-unauthenticated
```

## Contribution

Les contributions sont les bienvenues. Veuillez ouvrir une issue pour discuter de ce que vous aimeriez changer ou soumettre directement une pull request.

## Licence

[MIT](LICENSE.md)

## Deployment 

For Unix : 

Use the command line : 

./deploy_branch.sh

For Windows : 

Use the command line : 

deploy_branch.bat


