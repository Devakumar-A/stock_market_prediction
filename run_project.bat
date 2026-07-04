@echo off
cd /d %~dp0
call lstm_env\Scripts\activate
python backend\app.py
pause
