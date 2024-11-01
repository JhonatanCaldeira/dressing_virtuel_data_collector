#!/bin/bash
declare -A apiServicePort=( 
    ["api_server_db"]=$PG_API_PORT
    ["api_classification_model"]=$CLASSIFICATION_API_PORT
    ["api_segmentation_model"]=$SEGMENTATION_API_PORT
    ["api_object_detection_model"]=$OBJ_DETECTION_API_PORT
    ["api_face_recognition"]=$FACE_RECOGNITION_API_PORT
)

if [ "$1" = "all" ]; then
    if [ "$2" = "start" ]; then
        nohup uvicorn api.api_server_db:app --port $PG_API_PORT > logs/api/api_server_db.log 2>&1 &
        nohup uvicorn api.api_classification_model:app --port $CLASSIFICATION_API_PORT > logs/api/api_classification_model.log 2>&1 &
        nohup uvicorn api.api_segmentation_model:app --port $SEGMENTATION_API_PORT > logs/api/api_segmentation_model.log 2>&1 &
        nohup uvicorn api.api_object_detection_model:app --port $OBJ_DETECTION_API_PORT > logs/api/api_object_detectation_model.log 2>&1 &
        nohup uvicorn api.api_face_recognition:app --port $FACE_RECOGNITION_API_PORT > logs/api/api_face_recognition.log 2>&1 &
    
    elif [ "$2" = "stop" ]; then
        pkill -f "uvicorn .*:app"
    fi
else 
    if [ "$2" = "start" ]; then
        nohup uvicorn api.$1:app --port ${apiServicePort[$1]} > logs/api/$1.log 2>&1 &
    elif [ "$2" = "stop" ]; then
        pkill -f "uvicorn .*$1:app"
    fi
fi