@echo
setlocal

:: Charger les variables d'environnement depuis env/.env.local
for /f "tokens=*" %%i in (env/.env.local) do set %%i

:: Définir le nom de la branche Git
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH_NAME=%%i
set SERVICE_NAME=cookeo-a-retro-%BRANCH_NAME%

echo SERVICE_NAME=%SERVICE_NAME%

if "%1" == "CLEAN" (
    echo Nettoyez la registry et cloud run après vos tests pour ne pas consommer trop de ressources

    echo gcloud run services delete %SERVICE_NAME% --region %REGION% --project %PROJECT_ID%
    gcloud run services delete %SERVICE_NAME% --region %REGION% --project %PROJECT_ID%

    echo gcloud artifacts docker images delete %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME% --project %PROJECT_ID%
    gcloud artifacts docker images delete %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME% --project %PROJECT_ID%

    exit /b 255
)
set SECRETS=MAILGUN_USERNAME MAILGUN_DOMAIN MAILGUN_SERVER MAILGUN_API_KEY_NOPROD SECRET_KEY

echo SECRETS=%SECRETS%

echo Authentifiez-vous sur Google Artifact Repositories

echo gcloud auth print-access-token ^| docker login -u oauth2accesstoken --password-stdin https://%REGION%-docker.pkg.dev

gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://%REGION%-docker.pkg.dev

echo Buildez votre conteneur

echo docker build -t %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME%:latest .

docker build -t %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME%:latest .

echo Poussez votre conteneur dans la registry

echo docker push %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME%:latest

docker push %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME%:latest

gcloud config set core/project %PROJECT_ID%

echo Déployez votre conteneur dans Cloud Run

setlocal enabledelayedexpansion
set SECRETS_ARG=
for %%S in (%SECRETS%) do (
    for /f "tokens=*" %%P in ('gcloud secrets versions access latest --project %PROJECT_ID% --secret %%S --format="value(name)"') do (
        set SECRETS_ARG=!SECRETS_ARG!,%%S=%%P
    )
)
endlocal & set SECRETS_ARG=%SECRETS_ARG:~1%

gcloud run deploy %SERVICE_NAME% ^
  --region %REGION% ^
  --image %GAR_REPOSITORY%/%IMAGE_NAME%-%BRANCH_NAME%:latest ^
  --platform managed ^
  --port 5000 ^
  --set-secrets=%SECRETS_ARG% ^
  --set-env-vars=REGION=%REGION%,BRANCH_NAME=%BRANCH_NAME% ^
  --allow-unauthenticated

endlocal