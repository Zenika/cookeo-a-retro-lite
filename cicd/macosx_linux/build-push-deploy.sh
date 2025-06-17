#!/bin/bash

######################
## Common Variables ##
######################

CURRENT_FOLDER=$(pwd -P)
SCRIPT_NAME=$(basename $0)
PROJECT_FOLDER=${CURRENT_FOLDER}

APP_NAME=$1
ENVIRONMENT_NAME=$2

# Load Common Variables and functions

source ${CURRENT_FOLDER}/cicd/macosx_linux/common-cicd.sh

###############
## Functions ##
###############

function gcp_auth() {
    # The gcp_auth function attempts to authenticate to Google Artifact 
    # Repositories using Docker. It retrieves the user's access token, logs in to
    # the GAR registry, and exits with an error message if the authentication 
    # fails. This function is essential for pushing Docker images to GAR.

    info "Authentification on Google Artifact Repositories"
    
    if ! (gcloud auth print-access-token \
        | docker login \
        -u oauth2accesstoken \
        --password-stdin https://${REGION}-docker.pkg.dev)
    then
        error "Authentication to Google Artifact Repositories failed."
        exit 1
    else
        success "Authentication to Google Artifact Repositories succeeded."
    fi
}

function build_docker_image() {

    # The build_docker_image function builds a Docker image based on the 
    # current environment and branch. It handles both non-production and 
    # production environments, ensuring that the correct image tag and Git 
    # tagging are used. The function also includes error handling and success 
    # messages for better user feedback.

    if [[ ${ENVIRONMENT} == "no-prod" ]]; then
        
        info "Building docker image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest..."

        if ! (docker build \
            -t ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest \
            . \
            --platform linux/amd64)
        then
            exit_error "DOCKER_BUILD_FAILED" "Unable to build docker image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest."
        else
            success "Docker image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest built successfully."
        fi
    
    else

        read -p "Tag: " IMAGE_TAG
        read -p "Comment: " "COMMENT_TAG"

        read -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

        info "Tagging main branch with tag v${IMAGE_TAG}..."

        git tag -a "v${IMAGE_TAG}" -m "$COMMENT_TAG"
        
        if ! (git push origin tag v${IMAGE_TAG}); then
            error "TAG_FAILED" "Unable to tag main branch with tag v${IMAGE_TAG}."
            exit 1
        else
            success "Main branch tagged successfully with tag v${IMAGE_TAG}."
        fi

        if ! (docker build \
            -t ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG} \
            . \
            --platform linux/amd64)
        then
            exit_error "DOCKER_BUILD_FAILED" x"Unable to build the docker image ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"
        else
            success "Docker image ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG} built successfully."
        fi
    
    fi
}

function push_docker_image() {

    if [[ ${ENVIRONMENT} == "no-prod" ]]; then
        info "Pushing image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest..."

        if ! (docker push ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest); then
        error "Unable to push the image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest to the registry"
        exit 1
        else
            success "Image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest pushed successfully."
        fi
    else
        info "Pushing image ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}..."

        if ! (docker push ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}); then
        error "Unable to push the image ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG} to the registry"
        exit 1
        else
            success "Image ${GAR_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG} pushed successfully."
        fi
    fi

}

function cloudrun_deploy() {

    info "Deploying service ${SERVICE_NAME}..."

    if [[ ${ENVIRONMENT} == "no-prod" ]]; then

        if ! (gcloud run deploy ${SERVICE_NAME} \
            --region ${REGION} \
            --image ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}:latest \
            --platform managed \
            --port 5000 \
            --set-secrets=$( \
                for secret_name in "${SECRETS[@]}"; do 
                    secret_path=$(gcloud secrets versions access latest --project $PROJECT_ID --secret $secret_name --format='value(name)')
                    echo "$secret_name=$secret_path" 
                done | paste -sd, - \
            ) \
            --set-env-vars=REGION=${REGION},BRANCH_NAME=${BRANCH_NAME},GEMINI_MODEL=${GEMINI_MODEL} \
            --allow-unauthenticated)
        then
            error "Unable to deploy the service ${SERVICE_NAME} on Cloud Run"
            exit 1
        else
            success "Service ${SERVICE_NAME} successfully deployed on Cloud Run"
        fi

    else

        if ! (gcloud run deploy ${SERVICE_NAME} \
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
            --set-env-vars=REGION=${REGION},GEMINI_MODEL=${GEMINI_MODEL} \
            --allow-unauthenticated)
        then
            error "Unable to deploy the service ${SERVICE_NAME} on Cloud Run"
            exit 1
        else
            success "Service ${SERVICE_NAME} successfully deployed on Cloud Run"
        fi

    fi
}

function clean_image_list() {

    info "Cleaning image list..."

    for ID in $(docker image ls | grep none | awk '{print $3}'); do
        docker rmi -f ${ID}
    done

    info "Image list cleaned."
}

##########
## MAIN ##
##########

set_env
gcp_auth
build_docker_image
push_docker_image
clean_image_list
cloudrun_deploy