#!/bin/bash

ENV_FILE=config/.env

# Check if the .env file exists
if [ -f $ENV_FILE ]; then
    # Export all variables defined in the .env file
    export $(grep -v '^#' $ENV_FILE | xargs)
    echo "Environment variables loaded from .env"
else
    echo ".env file not found!"
fi
