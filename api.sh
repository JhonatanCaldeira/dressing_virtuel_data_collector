#!/bin/bash
declare -A apiServicePort=( 
    ["api_server_db"]=$PG_API_PORT
    ["api_models"]=$MODELS_API_PORT
    ["api_celery"]=$CELERY_API_PORT
)

if [ "$1" = "all" ]; then
    if [ "$2" = "start" ]; then
        nohup uvicorn api.api_server_db:app --port $PG_API_PORT > logs/api/api_server_db.log 2>&1 &
        nohup uvicorn api.api_models:app --port $MODELS_API_PORT > logs/api/api_models.log 2>&1 &
        nohup uvicorn api.api_celery:app --port $CELERY_API_PORT > logs/api/api_celery.log 2>&1 &
        nohup celery -A broker.tasks worker --loglevel=INFO > logs/api/celery.log 2>&1 &
    
    elif [ "$2" = "stop" ]; then
        pkill -f "uvicorn .*:app"
        pkill -f "celery -A broker.tasks worker"
    fi
else 
    if [ "$2" = "start" ]; then
        nohup uvicorn api.$1:app --port ${apiServicePort[$1]} > logs/api/$1.log 2>&1 &
    elif [ "$2" = "stop" ]; then
        pkill -f "uvicorn .*$1:app"
    fi
fi