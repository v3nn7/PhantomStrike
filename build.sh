#!/bin/bash

echo "Building PhantomStrike Applications..."

echo ""
echo "Installing required packages..."
pip3 install pyinstaller cx_freeze

echo ""
echo "Building Server with PyInstaller..."
pyinstaller --onefile --name PhantomStrike-Server --add-data "server_config.ini:." Server.py

echo ""
echo "Building Client with PyInstaller..."
cd client
pyinstaller --onefile --name PhantomStrike-Client --add-data "client_config.ini:." --add-data "core:core" --add-data "functions:functions" core/client_main.py
cd ..

echo ""
echo "Build completed! Executables are in the 'dist' folder."
echo ""
echo "To run:"
echo "  Server: ./dist/PhantomStrike-Server"
echo "  Client: ./dist/PhantomStrike-Client"
