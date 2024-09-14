#!/bin/bash

echo "Create Account Admin..."
python3 create_admin.py

if [ $? -ne 0 ]; then
    echo "Error: Python script failed with exit code $?."
else
    echo "Create done!"
fi
