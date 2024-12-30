#!/bin/bash
cd /home/jcaldeira/dressing_virtuel_data_collector/
source /home/jcaldeira/dressing_virtuel_data_collector/load_env.sh
echo $PG_DB_HOST
echo $PG_DB_PORT
PYTHONPATH=/home/jcaldeira/dressing_virtuel_data_collector 
/home/jcaldeira/dressing_virtuel_data_collector/.venv/bin/python -m models.model_evaluation.evaluation_segb3 > /home/jcaldeira/dressing_virtuel_data_collector/logs/evaluation_segb3.log 2>&1