@echo off
title Restaurant Management System
echo Starting Restaurant System Server...

:: Start Flask app silently
start /min python app.py

:: Wait 2 seconds for server startup
timeout /t 2 /nobreak > nul

:: Open system in browser
start http://127.0.0.1:5000/orders/cart

echo System is running! Keep this window minimized.