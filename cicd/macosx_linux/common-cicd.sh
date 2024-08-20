#!/bin/bash

######################
## Common Variables ##
######################

# colors for printing

RED='\033[1;31m'
BLUE='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENV_REPOSITORY=${PROJECT_FOLDER}/env
DOCKERFILE=${PROJECT_FOLDER}/Dockerfile
BRANCH_NAME=$(git branch --show-current)

source ${ENV_REPOSITORY}/.env.local

######################
## Common Functions ##
######################

function info() {
  printf "${BLUE}${@}${NC}\n"
}

function error() {
  printf "${RED}${@}${NC}\n"
}

function warn() {
  printf "${YELLOW}${@}${NC}\n"
}

function success() {
  printf "${GREEN}${@}${NC}\n"
}

# Print the error ($2) and the exit code ($1)
function exit_error() {
  error $@
  exit 1
}

function set_env() {
    
    info "You're on the branch ${BRANCH_NAME}. Setting up env variables."
    
    if [[ ${BRANCH_NAME} != "main" ]]; then
        SUFFIXE=$(echo ${BRANCH_NAME} | sed s/'_'/'-'/g)
        SERVICE_NAME=${SERVICE_NAME}-${SUFFIXE}
        SECRETS=(
            "MAILGUN_USERNAME"
            "MAILGUN_DOMAIN"
            "MAILGUN_SERVER"
            "MAILGUN_API_KEY_NOPROD"
            "SECRET_KEY"
        )
        ENVIRONMENT=no-prod
    else
        SECRETS=(
            "MAILGUN_USERNAME"
            "MAILGUN_DOMAIN"
            "MAILGUN_SERVER"
            "MAILGUN_API_KEY_PROD"
            "SECRET_KEY"
        )
        ENVIRONMENT=prod
    fi
    
    info "ENVIRONMENT=${ENVIRONMENT}"
    info "ENV_REPOSITORY=${ENV_REPOSITORY}"
    info "SERVICE_NAME=${SERVICE_NAME}"
    info "DOCKERFILE=${DOCKERFILE}"
    info "REGION=${REGION}"
    info "SECRETS:"
    for secret in "${SECRETS[@]}"; do
        info "  - $secret"
    done

}