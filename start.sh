#!/bin/bash
# FoodWerk — Kill & Restart

echo "Stoppe laufende Instanz..."
pkill -f "python.*foodwerk" 2>/dev/null
sleep 1

echo "Starte FoodWerk..."
cd "$(dirname "$0")"
exec .venv/bin/python3 -m foodwerk
