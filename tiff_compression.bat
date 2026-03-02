@echo off
call .venv\Scripts\activate.bat
start /b pythonw app/tiff_compression_gui.py %*