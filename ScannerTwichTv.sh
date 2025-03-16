#!/bin/bash
# Variables de entorno
ENV_DIR="/home/villafapd/Documents/PythonProjects/Elnueve/.venv"
lxterminal --title="Scanner_TwichTv" --geometry=60x30+10+10 --command="/bin/bash -c 'source $ENV_DIR/bin/activate; exec python3.11 /home/villafapd/Documents/PythonProjects/Elnueve/scanner_twich_tv.py'"