@echo off
call .venv\Scripts\activate.bat
python app/tiff_compression_gui.py %*
pause