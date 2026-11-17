@echo off
title Portal Analisis Sentimen Pemkab Bangka
color 0A
echo ======================================================================
echo    APLIKASI ANALISIS SENTIMEN BERITA PEMERINTAH KABUPATEN BANGKA
echo ======================================================================
echo.
echo Sedang menyiapkan server aplikasi...
echo URL Akses: http://localhost:5000
echo Password Default Admin: adminbangka
echo.

set PY_EXE="C:\Users\INIXINDO\AppData\Local\Programs\Python\Python311\python.exe"

if exist %PY_EXE% (
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000"
    %PY_EXE% app.py
) else (
    timeout /t 2 /nobreak >nul
    start "" "http://localhost:5000"
    python app.py
)

pause

