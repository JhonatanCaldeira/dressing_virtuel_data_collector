#!/bin/bash
declare -A apiServicePort=( 
    ["api_server_db"]=5000
    ["api_classification_model"]=5001
    ["api_segmentation_model"]=5002
    ["api_object_detection_model"]=5003
    ["api_face_recognition"]=5004
)

if [ "$1" = "all" ]; then
    if [ "$2" = "start" ]; then
        nohup uvicorn api.api_server_db:app --port 5000 > logs/api/api_server_db.log 2>&1 &
        nohup uvicorn api.api_classification_model:app --port 5001 > logs/api/api_classification_model.log 2>&1 &
        nohup uvicorn api.api_segmentation_model:app --port 5002 > logs/api/api_segmentation_model.log 2>&1 &
        nohup uvicorn api.api_object_detection_model:app --port 5003 > logs/api/api_object_detectation_model.log 2>&1 &
        nohup uvicorn api.api_face_recognition:app --port 5004 > logs/api/api_face_recognition.log 2>&1 &
    
    elif [ "$2" = "stop" ]; then
        pkill -f "uvicorn .*model:app"
    fi
else 
    if [ "$2" = "start" ]; then
        nohup uvicorn api.$1:app --port ${apiServicePort[$1]} > logs/api/$1.log 2>&1 &
    elif [ "$2" = "stop" ]; then
        pkill -f "uvicorn .*$1:app"
    fi
fi