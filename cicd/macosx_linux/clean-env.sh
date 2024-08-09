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

function clean_service() {

    info "Cleaning service ${SERVICE_NAME}..."

    if ! (gcloud run services delete ${SERVICE_NAME} \
        --region ${REGION})
    then
        error "Unable to delete service ${SERVICE_NAME}"
        exit 1
    else
        success "Deletion of service ${SERVICE_NAME} successful."
    fi

}

function clean_image_on_repository() {

    info "Cleaning image on Artifact Repositories..."

    if ! (gcloud artifacts docker images delete ${GAR_REPOSITORY}/${IMAGE_NAME}-${SUFFIXE}); then
        error "Unable to delete images on Google Artifacts Repositories"
        exit 1
    else
        success "Images on Google Artifacts Repositories have been cleaned"
    fi

}

##########
## MAIN ##
##########

set_env
clean_service
clean_image_on_repository
