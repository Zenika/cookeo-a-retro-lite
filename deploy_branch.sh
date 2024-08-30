#!/bin/zsh

source env/.env.local

export BRANCH_NAME=$(git branch --show-current)
export SERVICE_NAME=cookeo-a-retro-${BRANCH_NAME}

echo "SERVICE_NAME=$SERVICE_NAME"

if [[ $1 = "CLEAN" ]]; then
echo "Nettoyez la registry et cloud run après vos tests pour pas consommer trop de ressources"
echo "gcloud run services delete ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID}"
gcloud run services delete ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID}

echo "gcloud artifacts docker images delete ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME} --project ${PROJECT_ID}"
gcloud artifacts docker images delete ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME} --project ${PROJECT_ID}

exit 255
fi

export SECRETS=(
    "MAILGUN_USERNAME"
    "MAILGUN_DOMAIN"
    "MAILGUN_SERVER"
    "MAILGUN_API_KEY_NOPROD"
    "SECRET_KEY"
)

echo "SECRETS=$SECRETS"
echo "Authentifiez-vous sur Google Artifact Repositories"

  echo "gcloud auth print-access-token \
| docker login \
  -u oauth2accesstoken \
  --password-stdin https://${REGION}-docker.pkg.dev"

gcloud auth print-access-token \
| docker login \
  -u oauth2accesstoken \
  --password-stdin https://${REGION}-docker.pkg.dev

echo "Buildez votre conteneur"

echo "docker build \
    -t ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest \
    . \
    --platform linux/amd64"

docker build \
    -t ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest \
    . \
    --platform linux/amd64

echo "Poussez votre conteneur dans la registry"

echo "push ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest"

docker push ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest

echo "Set Project_ID"

echo "gcloud config set core/project ${PROJECT_ID}"

gcloud config set core/project ${PROJECT_ID}

echo "Déployez votre conteneur dans Cloud Run"

echo "gcloud run deploy ${SERVICE_NAME}
  --region ${REGION} 
  --image ${GAR_REPOSITORY}/${IMAGE_NAME}-${BRANCH_NAME}:latest 
  --platform managed 
  --port 5000 
  --set-secrets=$(
        for secret_name in "${SECRETS[@]}"; do 
            secret_path=$(gcloud secrets versions access latest --project $PROJECT_ID --secret $secret_name --format='value(name)')
            echo "$secret_name=$secret_path" 
        done | paste -sd, -
    ) "

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